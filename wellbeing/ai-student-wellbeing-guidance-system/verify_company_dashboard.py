
import unittest
import json
from app import app
from extensions import mongo
from flask import session
import bcrypt
from datetime import datetime

class TestCompanyDashboard(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        
        # Cleanup
        mongo.db.users.delete_many({"email": {"$regex": "test_company_"}})
        mongo.db.emotional_analysis.delete_many({"user_id": {"$regex": "test_company_"}}) # Note: user_id here is usually ObjectId str

        # 1. Create Manager
        self.manager_email = "test_company_manager@example.com"
        self.company_name = "TechCorp Test"
        manager_data = {
            "name": "Manager Bob",
            "email": self.manager_email,
            "password": bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt()),
            "role": "company_manager",
            "company_name": self.company_name,
            "department": "Management"
        }
        self.manager_id = str(mongo.db.users.insert_one(manager_data).inserted_id)

        # 2. Create Employee 1 (Healthy)
        emp1_data = {
            "name": "Employee Alice",
            "email": "test_company_emp1@example.com",
            "password": bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt()),
            "role": "company_employee",
            "company_name": self.company_name,
            "department": "Engineering"
        }
        self.emp1_id = str(mongo.db.users.insert_one(emp1_data).inserted_id)
        
        # Add Healthy Data for Emp 1
        mongo.db.emotional_analysis.insert_one({
            "user_id": self.emp1_id,
            "ai_mood": "Happy",
            "ai_stress": "Low",
            "wellbeing_score": 85,
            "created_at": datetime.utcnow()
        })

        # 3. Create Employee 2 (Stressed)
        emp2_data = {
            "name": "Employee Charlie",
            "email": "test_company_emp2@example.com",
            "password": bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt()),
            "role": "company_employee",
            "company_name": self.company_name,
            "department": "Sales"
        }
        self.emp2_id = str(mongo.db.users.insert_one(emp2_data).inserted_id)

        # Add Stressed Data for Emp 2
        mongo.db.emotional_analysis.insert_one({
            "user_id": self.emp2_id,
            "ai_mood": "Anxious",
            "ai_stress": "High",
            "wellbeing_score": 30,
            "created_at": datetime.utcnow()
        })

    def tearDown(self):
        mongo.db.users.delete_many({"email": {"$regex": "test_company_"}})
        # Clean up analysis records based on stored IDs
        mongo.db.emotional_analysis.delete_many({"user_id": {"$in": [self.emp1_id, self.emp2_id]}})
        self.ctx.pop()

    def login_manager(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = self.manager_id
            sess['role'] = 'company_manager'
            sess['_permanent'] = True

    def test_dashboard_access_and_metrics(self):
        self.login_manager()
        
        response = self.app.get('/dashboard/company')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        
        # Verify Company Name
        self.assertIn(self.company_name, content)
        
        # Verify Employee Count (Should be 2)
        # We look for the number in the HTML. 
        # Since HTML might have other numbers, we look for "2" near "Total Employees" or just existence.
        # A simpler check is to check context locals if Flask allowed, but we parse HTML or check key strings.
        self.assertIn(">2</h3>", content) # Assuming <h3>2</h3> for count
        
        # Verify Active Concerns (Should be 1: Charlie)
        self.assertIn(">1</h3>", content) # active concerns
        
        # Verify Employee Names in Risk List
        self.assertIn("Employee Charlie", content)
        self.assertNotIn("Employee Alice", content) # Alice is healthy, shouldn't be in risk list
        
        print("\n✅ Verification Successful: Company Dashboard loads with correct metrics.")

if __name__ == '__main__':
    unittest.main()
