from flask import Flask, session
from routes.emergency import emergency
from utils.email_service import send_emergency_email
from unittest.mock import MagicMock, patch
import sys

# Mock Flask app and session
app = Flask(__name__)
app.register_blueprint(emergency)
app.secret_key = "supersecret"

def run_test(stress_score, history_scores, expect_email):
    print(f"\n--- Testing with Current Score {stress_score} and History {history_scores} ---")
    
    with app.test_request_context('/emergency/send_alert', method='POST'):
        # Mock session
        with app.test_client() as client:
            # Use a valid 24-char hex string for ObjectId
            valid_id = "507f1f77bcf86cd799439011"
            with client.session_transaction() as sess:
                sess['user_id'] = valid_id 
            
            # Mock Mongo
            with patch('routes.emergency.mongo') as mock_mongo:
                # Mock user
                mock_mongo.db.users.find_one.return_value = {
                    "_id": valid_id,
                    "name": "Test Student",
                    "email": "student@test.com",
                    "emergency_contact_name": "Mom", 
                    "emergency_phone": "1234567890",
                    "emergency_email": "mom@test.com"
                }

                # Construct logs
                logs = [{"created_at": None, "stress_score": stress_score, "emotion": "Stressed"}]
                for s in history_scores:
                    logs.append({"created_at": None, "stress_score": s, "emotion": "Stressed"})
                    
                mock_mongo.db.daily_logs.find.return_value.sort.return_value.limit.return_value = logs

                # Capture stdout
                from io import StringIO
                captured_output = StringIO()
                sys.stdout = captured_output

                try:
                    response = client.post('/emergency/send_alert', follow_redirects=True)
                    
                    sys.stdout = sys.__stdout__ # Reset stdout
                    output = captured_output.getvalue()
                    
                    print(output)
                    
                    email_sent = "SIMULATED EMAIL ALERT" in output
                    if expect_email:
                        if email_sent:
                            print("SUCCESS: Email was sent as expected.")
                        else:
                            print("FAILURE: Email was NOT sent, but should have been.")
                    else:
                        if not email_sent:
                            print("SUCCESS: Email was NOT sent, as expected.")
                        else:
                            print("FAILURE: Email WAS sent, but should NOT have been.")
                        
                except Exception as e:
                    sys.stdout = sys.__stdout__
                    print(f"ERROR: {e}")

if __name__ == "__main__":
    # Test 1: Critical (Current 90, History 90, 90) -> Should Send
    run_test(90, [90, 90], expect_email=True)
    
    # Test 2: Non-Critical (Current 50, History 50) -> Should NOT Send
    run_test(50, [50], expect_email=False)
