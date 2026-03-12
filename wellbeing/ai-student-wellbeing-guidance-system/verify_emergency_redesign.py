
import unittest
from app import app
from extensions import mongo
from flask import session
import bcrypt
from bs4 import BeautifulSoup

class TestEmergencyRedesign(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        
        # Create a test user with emergency contact
        self.test_email = "test_emergency@example.com"
        mongo.db.users.delete_one({"email": self.test_email})
        
        self.user_data = {
            "name": "Emergency Tester",
            "email": self.test_email,
            "password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()),
            "role": "student",
            "emergency_contact_name": "Guardian Angel",
            "emergency_phone": "+19876543210",
            "emergency_email": "guardian@example.com"
        }
        self.user_id = mongo.db.users.insert_one(self.user_data).inserted_id

    def tearDown(self):
        mongo.db.users.delete_one({"_id": self.user_id})
        self.ctx.pop()

    def login(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = str(self.user_id)
            sess['role'] = 'student'
            sess['_permanent'] = True

    def test_emergency_page_rendering(self):
        self.login()
        response = self.app.get('/emergency')
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # 1. Verify Contact Name is displayed
        self.assertIn("Guardian Angel", response.data.decode())
        
        # 2. Verify Call Link
        call_link = soup.find('a', href=f"tel:{self.user_data['emergency_phone']}")
        self.assertIsNotNone(call_link, "Call link (tel:) not found or incorrect")
        
        # 3. Verify SMS Link
        sms_link = soup.find('a', href=lambda x: x and x.startswith(f"sms:{self.user_data['emergency_phone']}"))
        self.assertIsNotNone(sms_link, "SMS link (sms:) not found or incorrect")
        
        # 4. Verify Email Link
        email_link = soup.find('a', href=lambda x: x and x.startswith(f"mailto:{self.user_data['emergency_email']}"))
        self.assertIsNotNone(email_link, "Email link (mailto:) not found or incorrect")
        
        print("\n✅ Verification Successful: All emergency links generated correctly.")

if __name__ == '__main__':
    unittest.main()
