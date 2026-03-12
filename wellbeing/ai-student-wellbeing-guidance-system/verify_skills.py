
import unittest
import json
from app import app
from extensions import mongo
from flask import session
import bcrypt
from bson import ObjectId

class TestSkillsModule(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        
        # Create a test user
        self.test_email = "test_skills@example.com"
        mongo.db.users.delete_one({"email": self.test_email})
        
        self.user_data = {
            "name": "Skill Tester",
            "email": self.test_email,
            "password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()),
            "role": "student"
        }
        self.user_id = mongo.db.users.insert_one(self.user_data).inserted_id
        
        # Ensure skills are initialized by hitting the route once (or manually here if needed)
        # We rely on the route to init default skills
        
        # Reset user skills
        mongo.db.user_skills.delete_many({"user_id": self.user_id})

    def tearDown(self):
        mongo.db.users.delete_one({"_id": self.user_id})
        mongo.db.user_skills.delete_many({"user_id": self.user_id})
        self.ctx.pop()

    def login(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = str(self.user_id)
            sess['role'] = 'student'
            sess['_permanent'] = True

    def test_skills_flow(self):
        self.login()
        
        # 1. Access Skills Dashboard (Should trigger init_default_skills)
        response = self.app.get('/skills')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Skill Development", response.data)
        
        # 2. Get a skill ID
        skill = mongo.db.skills.find_one({"name": "Python Basics"})
        self.assertIsNotNone(skill, "Default skills not initialized")
        skill_id = str(skill["_id"])
        
        # 3. Update Progress (Increment)
        response = self.app.post(f'/skills/update/{skill_id}', 
                                 data=json.dumps({"action": "increment"}),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['new_completed'], 1)
        
        # 4. Verify Database Update
        user_progress = mongo.db.user_skills.find_one({
            "user_id": self.user_id,
            "skill_id": skill["_id"]
        })
        self.assertIsNotNone(user_progress)
        self.assertEqual(user_progress['completed_modules'], 1)
        
        print("\n✅ Verification Successful: Skills initialized, accessed, and progress updated.")

if __name__ == '__main__':
    unittest.main()
