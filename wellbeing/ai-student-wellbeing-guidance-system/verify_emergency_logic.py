from flask import Flask
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime, timedelta
import sys
import time

# Setup Minimal App
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/student_wellbeing"
mongo = PyMongo(app)

# Inject mongo into extensions (hack for standalone script)
import extensions
extensions.mongo = mongo

from utils.emergency_manager import check_emergency

def run_test():
    with app.app_context():
        print("--- Starting Emergency Logic Verification ---")
        
        # 1. Setup Test User
        user_id = ObjectId()
        test_user = {
            "_id": user_id,
            "name": "Test Student",
            "email": "test@student.com",
            "emergency_contact_name": "Test Parent",
            "emergency_phone": "555-0000"
        }
        
        print(f"Created Test User: {user_id}")
        
        # Helper to clear logs
        def clear_logs():
            mongo.db.daily_logs.delete_many({"user_id": user_id})
            
        clear_logs()
        
        # --- TEST 1: Calm Mode (Level 1) ---
        print("\n[TEST 1] Single High Stress Entry (Score 60)")
        res = check_emergency(60, test_user)
        if res["level"] == 1 and res["action"] == "suggest_meditation":
            print("✅ PASS: Correctly identified Level 1 (Calm Mode)")
        else:
            print(f"❌ FAIL: Expected Level 1, Got {res['level']}")
            
        # --- TEST 2: Recommendation Mode (Level 2) ---
        print("\n[TEST 2] Persistent High Stress (3 entries > 70)")
        # Insert 2 past entries > 70
        mongo.db.daily_logs.insert_one({"user_id": user_id, "stress_score": 75, "created_at": datetime.utcnow() - timedelta(days=1)})
        mongo.db.daily_logs.insert_one({"user_id": user_id, "stress_score": 80, "created_at": datetime.utcnow() - timedelta(days=2)})
        
        # Current entry > 70
        res = check_emergency(72, test_user)
        if res["level"] == 2 and res["action"] == "recommend_counselor":
             print("✅ PASS: Correctly identified Level 2 (Counselor Mode)")
        else:
             print(f"❌ FAIL: Expected Level 2, Got {res['level']} (Msg: {res.get('message')})")
             
        clear_logs()
        
        # --- TEST 3: Critical Mode (Level 3) ---
        print("\n[TEST 3] Persistent Critical Stress (3 entries > 85)")
        # Insert 2 past entries > 85
        mongo.db.daily_logs.insert_one({"user_id": user_id, "stress_score": 90, "created_at": datetime.utcnow() - timedelta(days=1), "emotion": "Devastated"})
        mongo.db.daily_logs.insert_one({"user_id": user_id, "stress_score": 88, "created_at": datetime.utcnow() - timedelta(days=2), "emotion": "Hopeless"})
        
        # Current entry > 85
        res = check_emergency(95, test_user)
        if res["level"] == 3 and res["alert_sent"] == True:
             print("✅ PASS: Correctly identified Level 3 (Critical Mode) and triggered alert")
        else:
             print(f"❌ FAIL: Expected Level 3 with Alert, Got {res['level']}")

        # --- TEST 4: Direct Email Service Verification ---
        print("\n[TEST 4] Direct Email Service Verification")
        from utils.email_service import send_emergency_email
        email_success = send_emergency_email(
            test_user, 
            99, 
            [{"created_at": datetime.utcnow(), "emotion": "Test Mood", "stress_score": 99}], 
            context="Manual Verification"
        )
        if email_success:
             print("✅ PASS: Email service executed successfully (Simulated)")
        else:
             print("❌ FAIL: Email service failed")

        # Cleanup
        clear_logs()
        print("\n--- Verification Complete ---")

if __name__ == "__main__":
    run_test()
