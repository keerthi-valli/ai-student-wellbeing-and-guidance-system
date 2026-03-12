from utils.roadmap_engine import generate_roadmap

# Test 1: Standard Subject
print("Test 1: Standard Subject (Python)")
profile_1 = {"subject": "python", "daily_hours": 2}
roadmap_1 = generate_roadmap(profile_1)
print(f"Topics per week: {roadmap_1['topics_per_week']}")
first_topic = roadmap_1['roadmap'][0]['topics'][0]
print(f"First topic structure: {first_topic}")
if isinstance(first_topic, dict) and "topic" in first_topic and "completed" in first_topic:
    print("[PASS] Topic is an object")
else:
    print("[FAIL] Topic is not an object")

# Test 2: Custom Subject
print("\nTest 2: Custom Subject (React JS)")
profile_2 = {"subject": "other", "custom_subject": "React JS", "daily_hours": 2}
roadmap_2 = generate_roadmap(profile_2)
first_topic_2 = roadmap_2['roadmap'][0]['topics'][0]
print(f"First topic: {first_topic_2['topic']}")
if "React JS" in first_topic_2['topic']:
    print("[PASS] Custom subject title generated")
else:
    print("[FAIL] Custom subject title missing")

# Test 3: Stress Adaptation
print("\nTest 3: Stress Adaptation")
profile_3 = {"subject": "python", "daily_hours": 2} # Normal ~5 topics
mood_stress = {"stress_score": 90, "mood": "Anxious"}
roadmap_3 = generate_roadmap(profile_3, mood_stress)
print(f"High Stress Topics/Week: {roadmap_3['topics_per_week']}")
print(f"Adaptation Message: {roadmap_3['adaptation_message']}")

mood_happy = {"stress_score": 20, "mood": "Happy"}
roadmap_4 = generate_roadmap(profile_3, mood_happy)
print(f"Low Stress Topics/Week: {roadmap_4['topics_per_week']}")

if roadmap_3['topics_per_week'] < roadmap_4['topics_per_week']:
    print("[PASS] Workload reduced for high stress")
else:
    print("[FAIL] Workload not reduced")
