def get_recommendations(mood, stress_level):
    """
    Returns a dictionary of recommendations based on Mood and Stress Level.
    Output format:
    {
        "status_color": "success" | "warning" | "danger",
        "status_text": "Doing Great" | "Needs Attention" | "Critical",
        "tips": ["Tip 1", "Tip 2"],
        "resources": [
            {"title": "...", "type": "Article/Video", "link": "#"}
        ]
    }
    """
    
    # Defaults
    recommendations = {
        "status_color": "success",
        "status_text": "Balanced",
        "tips": [],
        "resources": []
    }
    
    # 1. Stress Logic (Priority)
    if stress_level == "High":
        recommendations["status_color"] = "danger"
        recommendations["status_text"] = "High Stress - Immediate Action Recommended"
        recommendations["tips"] = [
            "Stop what you are doing and take 5 deep breaths.",
            "Step away from your screen for 10 minutes.",
            "Drink a glass of water.",
            "Contact a counselor or trusted friend immediately."
        ]
        recommendations["resources"] = [
            {"title": "5-Minute Stress Relief Guided Meditation", "type": "Video", "link": "https://www.youtube.com/results?search_query=5+minute+stress+relief"},
            {"title": "Box Breathing Technique", "type": "Technique", "link": "https://www.healthline.com/health/box-breathing"},
            {"title": "Emergency Helpline Numbers", "type": "Urgent", "link": "/emergency"}
        ]
        return recommendations # Return early for high stress
        
    elif stress_level == "Medium":
        recommendations["status_color"] = "warning"
        recommendations["status_text"] = "Moderate Stress"
        recommendations["tips"].extend([
            "Break your tasks into smaller, manageable chunks.",
            "Take a short walk outside.",
            "Listen to calming music while working."
        ])
        recommendations["resources"].append(
            {"title": "Managing Academic Stress", "type": "Article", "link": "#"}
        )

    # 2. Mood Logic
    if mood == "Sad":
        recommendations["status_color"] = "warning" if stress_level != "High" else "danger"
        recommendations["tips"].extend([
            "It's okay to feel sad. Allow yourself to feel it.",
            "Talk to a friend or write about your feelings.",
            "Do one small thing that usually brings you joy."
        ])
    elif mood == "Anxious":
        recommendations["status_color"] = "warning"
        recommendations["tips"].extend([
            "Focus on the present moment.",
            "Try the 5-4-3-2-1 grounding technique.",
            "Limit caffeine intake today."
        ])
    elif mood == "Happy" or mood == "Excited":
        recommendations["status_color"] = "success"
        recommendations["status_text"] = "Thriving"
        recommendations["tips"].extend([
            "Share your positive energy with someone!",
            "Use this motivation to tackle a difficult task.",
            "Reflect on what made today good."
        ])
    elif mood == "Neutral" or mood == "Calm":
        recommendations["tips"].extend([
            "A great state for focused work.",
            "Maintain this balance with regular breaks.",
            "Plan your schedule for tomorrow."
        ])
        
    # Default Resources if none added
    if not recommendations["resources"]:
        recommendations["resources"] = [
            {"title": "General Wellbeing Guide", "type": "PDF", "link": "#"},
            {"title": "Mindfulness for Students", "type": "Video", "link": "#"}
        ]

    return recommendations
