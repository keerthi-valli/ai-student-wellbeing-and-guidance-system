from utils.emergency_manager import check_emergency

# User Dummy Data
user_dummy = {
    "name": "Test User",
    "emergency_contact_name": "Dr. Smith",
    "emergency_phone": "555-0199"
}

def verify_level(score, name):
    print(f"\n--- Testing {name} (Score: {score}) ---")
    result = check_emergency(score, user_dummy)
    print(f"Level: {result['level']}")
    print(f"Category: {result['category']}")
    print(f"Message: {result['message']}")
    print(f"Action: {result['action']}")
    print(f"Alert Sent: {result['alert_sent']}")
    if result['alert_sent']:
        print(" [PASS] Alert correctly triggered.")
    else:
        if score > 85:
             print(" [FAIL] Alert NOT triggered for critical score.")

if __name__ == "__main__":
    verify_level(40, "Normal")
    verify_level(60, "Level 1 (Suggestion)")
    verify_level(75, "Level 2 (Recommendation)")
    verify_level(90, "Level 3 (Critical)")
