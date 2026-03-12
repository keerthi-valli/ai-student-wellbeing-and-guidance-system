
from flask import Flask, session
from extensions import mongo
from config import Config
from utils.analytics import get_user_analytics
from bson import ObjectId
import datetime

app = Flask(__name__)
app.config.from_object(Config)
mongo.init_app(app)

def test_analytics_output():
    """
    Simulates fetching analytics for a user and checks if the output structure 
    and value ranges are correct for the new Chart.js implementation (0-100).
    """
    print("Testing Analytics Output for Chart.js Integration...")
    
    with app.app_context():
        # Find a test user (e.g., student)
        user = mongo.db.users.find_one({"role": "student"})
        if not user:
            print("No student user found for testing.")
            return

        print(f"Testing with User ID: {user['_id']}")
        
        # Call the function
        analytics = get_user_analytics(str(user['_id']))
        
        # Verify Keys
        required_keys = ["history_labels", "history_data", "wellbeing_score"]
        for key in required_keys:
            if key not in analytics:
                print(f"FAILED: Missing key '{key}' in analytics output.")
                return

        # Verify Data Types and Ranges
        labels = analytics["history_labels"]
        data = analytics["history_data"]
        
        print(f"Labels: {labels}")
        print(f"Data: {data}")
        
        if not isinstance(data, list):
             print("FAILED: history_data is not a list.")
             return
             
        # Check if values are likely 0-100 (and not 1-5 legacy)
        # Verify at least one value if list is not empty
        if data:
            if all(0 <= x <= 100 for x in data):
                print("SUCCESS: Data values are within 0-100 range.")
                
                # Heuristic: if we have values > 5, it confirms we are using the new scale
                if any(x > 5 for x in data):
                     print("CONFIRMED: Detected values > 5, confirming 0-100 scale usage.")
                else:
                     print("WARNING: All values are <= 5. Could be low scores or legacy data remaining.")
            else:
                 print(f"FAILED: Data values out of range (0-100). Found: {data}")
        else:
            print("WARNING: No history data found (history_data is empty). Add diary entries to test fully.")

        print("Analytics Structure Verification Complete.")

if __name__ == "__main__":
    test_analytics_output()
