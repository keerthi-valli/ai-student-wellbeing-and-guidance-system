from flask import Flask, session, request, jsonify
from routes.academic import academic
from bson import ObjectId
from unittest.mock import patch, MagicMock
import sys
import json

# Setup Flask App
app = Flask(__name__)
app.register_blueprint(academic)
app.secret_key = "secret"

def test_skill_roadmap_flow():
    print("\n--- Testing Employee Skill Roadmap Flow ---")
    
    with app.test_request_context():
        with app.test_client() as client:
            user_id = ObjectId("507f1f77bcf86cd799439011")
            
            # Mock Session
            with client.session_transaction() as sess:
                sess['user_id'] = str(user_id)
                sess['role'] = 'company_employee'
            
            # --- Test 1: Create Roadmap ---
            print("\n1. Testing Roadmap Creation...")
            with patch('routes.academic.mongo') as mock_mongo:
                # Mock User
                mock_mongo.db.users.find_one.return_value = {
                    "_id": user_id,
                    "email": "emp@test.com",
                    "role": "company_employee"
                }
                # Mock Daily Logs (for mood)
                mock_mongo.db.daily_logs.find_one.return_value = {
                    "stress_score": 40, "emotion": "Happy"
                }
                
                # Mock Update/Insert for skill_profiles
                mock_mongo.db.skill_profiles.update_one.return_value = MagicMock(upserted_id=user_id)
                
                # Verify generate_roadmap calls are mocked or real?
                # We can let it run real if utils available, or mock it.
                # Let's mock generate_roadmap to avoid dependency issues if environment is strict
                with patch('utils.roadmap_engine.generate_roadmap') as mock_gen:
                    mock_gen.return_value = {
                        "roadmap": [
                            {"week": 1, "topics": [{"topic": "Intro", "completed": False}]}
                        ],
                        "progress": 0
                    }
                    
                    data = {
                        "action": "create_skill_roadmap",
                        "skill_name": "Python",
                        "current_level": "Beginner",
                        "daily_time_commitment": "2",
                        "goal": "Mastery"
                    }
                    
                    resp = client.post('/academic/employee', data=data, follow_redirects=True)
                    
                    if resp.status_code == 200:
                        print("SUCCESS: Roadmap Creation Request Processed.")
                        mock_mongo.db.skill_profiles.update_one.assert_called()
                        print("SUCCESS: DB Update Called.")
                    else:
                        print(f"FAILURE: Status Code {resp.status_code}")

            # --- Test 2: Update Progress ---
            print("\n2. Testing Progress Update...")
            with patch('routes.academic.mongo') as mock_mongo:
                 # Mock fetch profile
                mock_mongo.db.skill_profiles.find_one.return_value = {
                    "user_id": user_id,
                    "roadmap": {
                        "roadmap": [
                            {"week": 1, "topics": [{"topic": "Intro", "completed": False}, {"topic": "Basics", "completed": False}]}
                        ]
                    }
                }
                
                payload = {
                    "topic": "Intro",
                    "week": 1,
                    "completed": True
                }
                
                resp = client.post('/academic/update_progress', json=payload)
                
                print(f"Response: {resp.get_json()}")
                
                if resp.status_code == 200 and resp.get_json()['success']:
                    print("SUCCESS: Progress Update Successful.")
                    mock_mongo.db.skill_profiles.update_one.assert_called()
                    print("SUCCESS: Skill Profile Updated.")
                    
                    # Verify user collection update also called (field: skill_progress)
                    args, kwargs = mock_mongo.db.users.update_one.call_args
                    if "skill_progress" in args[1]['$set']:
                        print("SUCCESS: User Skill Progress Updated.")
                    else:
                        print("FAILURE: User Skill Progress NOT Updated.")
                else:
                    print(f"FAILURE: {resp.data}")

if __name__ == "__main__":
    try:
        test_skill_roadmap_flow()
    except Exception as e:
        print(f"ERROR: {e}")
