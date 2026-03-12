from utils.roadmap_engine import generate_roadmap
import json

# Profile 1: Standard
profile1 = {"subject": "python", "daily_hours": 2}
mood1 = {"stress_level": "Medium", "mood": "Neutral"}

# Profile 2: High Stress (Should reduce topics)
profile2 = {"subject": "mathematics", "daily_hours": 3}
mood2 = {"stress_level": "High", "mood": "Anxious"}

# Profile 3: Positive Mood (Should increase topics)
profile3 = {"subject": "english", "daily_hours": 1}
mood3 = {"stress_level": "Low", "mood": "Happy"}

def verify_roadmap(name, profile, mood):
    print(f"\n--- Verifying {name} ---")
    print(f"Profile: {profile}")
    print(f"Mood: {mood}")
    
    result = generate_roadmap(profile, mood)
    
    print(f"Total Weeks: {result['total_weeks']}")
    print(f"Topics Per Week: {result['topics_per_week']}")
    if result['adaptation_message']:
        print(f"Adaptation: {result['adaptation_message']}")
    
    # Print first week topics
    if result['roadmap']:
        print(f"Week 1 Topics: {result['roadmap'][0]['topics']}")
    else:
        print("[FAIL] No roadmap generated")

if __name__ == "__main__":
    verify_roadmap("Standard Profile", profile1, mood1)
    verify_roadmap("High Stress Profile", profile2, mood2)
    verify_roadmap("Positive Mood Profile", profile3, mood3)
