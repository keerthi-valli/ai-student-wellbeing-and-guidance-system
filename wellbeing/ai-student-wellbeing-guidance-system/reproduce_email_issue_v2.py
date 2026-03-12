from utils.email_service import send_emergency_email
from datetime import datetime
import sys

# Mock user object with emergency email
mock_user = {
    "name": "Test Student",
    "email": "student@test.com",
    "emergency_contact_name": "Mom",
    "emergency_phone": "1234567890",
    "emergency_email": "mom@test.com"  # This should be used
}

# Mock logs
mock_logs = [
    {"created_at": datetime.now(), "emotion": "Anxious", "stress_score": 85}
]

print("--- Testing send_emergency_email ---")
# Redirect stdout to handle encoding issues if necessary, but here we just print
# The goal is to see 'mom@test.com' in the output
try:
    send_emergency_email(mock_user, 85, mock_logs, context="Test Alert")
except Exception as e:
    print(f"Error: {e}")

print("\n--- Check above output for 'mom@test.com' ---")
