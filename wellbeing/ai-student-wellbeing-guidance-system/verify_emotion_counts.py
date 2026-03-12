from datetime import datetime, timedelta

# Mock Data
seven_days_ago = datetime.utcnow() - timedelta(days=7)
logs = [
    {"created_at": datetime.utcnow(), "emotion": "Happy"},
    {"created_at": datetime.utcnow() - timedelta(days=1), "emotion": "Sad"},
    {"created_at": datetime.utcnow() - timedelta(days=2), "emotion": "Happy"},
    {"created_at": datetime.utcnow() - timedelta(days=8), "emotion": "Angry"}, # Should be excluded
]

emotion_counts = {}
    
for log in logs:
    if log["created_at"] >= seven_days_ago:
        emotion = log.get("emotion", "Neutral")
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

print(f"Emotion Counts: {emotion_counts}")
expected = {'Happy': 2, 'Sad': 1}
assert emotion_counts == expected, f"Expected {expected}, got {emotion_counts}"
print("Verification Passed!")
