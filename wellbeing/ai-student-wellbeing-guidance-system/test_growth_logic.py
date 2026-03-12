from utils.analytics import get_user_analytics
from datetime import datetime, timedelta
# Mocking mongo for local testing properly is hard without a full mock, 
# so we will rely on a script that IMPORTS the function but we might need to mock mongo.
# Instead, since I can't easily mock mongo here without a library, 
# I will create a standalone script that duplicates the logic I PLAN to write 
# to verify the formula, or I will write the test to run against the ACTUAL db 
# if I can insert dummy data. 
# 
# Better approach: Write a script that defines the NEW function logic and tests it 
# with in-memory data, then I can copy-paste it to analytics.py.

def calculate_mood_growth(entries):
    """
    Proposed logic for 7-day growth.
    Entries are sorted Newest -> Oldest (as per current analytics.py).
    """
    # Filter last 7 days
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_entries = [e for e in entries if e['created_at'] >= seven_days_ago]
    
    # We need Newest -> Oldest for splitting? 
    # Logic: "Compare First 3 days average vs Last 3 days average"
    # "First 3 days" usually means the OLDER 3 days of the week.
    # "Last 3 days" usually means the NEWER 3 days of the week.
    
    # Sort Oldest -> Newest for easier slicing
    recent_entries.sort(key=lambda x: x['created_at'])
    
    if len(recent_entries) < 2:
        return 0, "No Trend"
        
    # Split
    # If we have 7 days: Day 1,2,3 (Old) vs Day 5,6,7 (New). Day 4 is middle.
    # If we have fewer, we split as best we can.
    
    mid = len(recent_entries) // 2
    first_half = recent_entries[:mid] # Older
    last_half = recent_entries[mid:]  # Newer (includes middle if odd? or split evenly?)
    
    # User Requirement: "First 3 days average vs Last 3 days average"
    # Let's try to grab exactly 3 if available, or all if less.
    
    # Actually, strictly "First 3 days" (oldest) and "Last 3 days" (newest)
    
    if len(recent_entries) >= 6:
        older_group = recent_entries[:3]
        newer_group = recent_entries[-3:]
    else:
        # Fallback for few entries
         older_group = recent_entries[:mid]
         newer_group = recent_entries[mid:]
    
    def get_score(e):
        return e.get('score', 50) # Assuming we have a score
    
    avg_old = sum(get_score(e) for e in older_group) / len(older_group)
    avg_new = sum(get_score(e) for e in newer_group) / len(newer_group)
    
    growth = ((avg_new - avg_old) / avg_old) * 100 if avg_old != 0 else 0
    
    return growth

# Test Data
now = datetime.now()
mock_entries = [
    {'created_at': now - timedelta(days=6), 'score': 40}, # Old
    {'created_at': now - timedelta(days=5), 'score': 45}, # Old
    {'created_at': now - timedelta(days=4), 'score': 50}, # Old
    {'created_at': now - timedelta(days=3), 'score': 60},
    {'created_at': now - timedelta(days=2), 'score': 70}, # New
    {'created_at': now - timedelta(days=1), 'score': 75}, # New
    {'created_at': now, 'score': 80}                      # New
]

growth = calculate_mood_growth(mock_entries)
print(f"Calculated Growth: {growth:.2f}%")
print(f"Expected: Positive growth (approx 80-100% increase?)")

# avg_old = (40+45+50)/3 = 45
# avg_new = (70+75+80)/3 = 75
# growth = (75 - 45) / 45 = 30 / 45 = 0.666 -> 66.6%

