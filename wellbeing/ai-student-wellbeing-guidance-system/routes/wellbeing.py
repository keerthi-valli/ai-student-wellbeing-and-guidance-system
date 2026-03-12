from datetime import datetime, timedelta
from flask import Blueprint, render_template, session, redirect, url_for
from extensions import mongo
from bson import ObjectId
from utils.recommendations import get_recommendations

wellbeing = Blueprint("wellbeing", __name__)

@wellbeing.route("/wellbeing")
def wellbeing_page():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    user_id = ObjectId(session["user_id"])
    user = mongo.db.users.find_one({"_id": user_id})
    
    # --- 1. Fetch Data from daily_logs ---
    # Get all logs sorted by date (newest first)
    logs = list(mongo.db.daily_logs.find(
        {"user_id": session["user_id"]}
    ).sort("created_at", -1))
    
    # --- 2. Current Status (Today's Mood / Latest) ---
    current_mood = "Neutral"
    current_stress = "Low"
    warning_msg = None
    
    if logs:
        latest = logs[0]
        current_mood = latest.get("emotion", "Neutral")
        current_stress = latest.get("stress_score", "Low")
        
        # Simple Warning Logic
        if current_stress == "High":
             warning_msg = "Your stress levels seem high. Consider taking a break or talking to a counselor."
        elif current_mood in ["Sad", "Anxious", "Depressed"]:
             warning_msg = "We noticed you might be feeling down. Check out the recommended resources below."

    # --- 3. 7-Day Mood Distribution (Pie Chart) ---
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    emotion_counts = {}
    
    for log in logs:
        if log["created_at"] >= seven_days_ago:
            emotion = log.get("emotion", "Neutral")
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
    # --- 4. 30-Day Stress Trend (Line Graph) ---
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    stress_map = {"Low": 20, "Medium": 50, "High": 80}
    
    # Group by Date
    daily_stress = {}
    
    for log in logs:
        if log["created_at"] >= thirty_days_ago:
            date_str = log["created_at"].strftime("%Y-%m-%d")
            s_val = stress_map.get(log.get("stress_score", "Low"), 20)
            
            if date_str not in daily_stress:
                daily_stress[date_str] = []
            daily_stress[date_str].append(s_val)
            
    # Calculate Averages and Sort by Date
    sorted_dates = sorted(daily_stress.keys())
    line_labels = [] # Dates
    line_data = []   # Avg Stress Scores
    
    for d in sorted_dates:
        scores = daily_stress[d]
        avg_score = sum(scores) / len(scores)
        line_labels.append(d)
        line_data.append(avg_score)
        
    # --- 5. Recommendations ---
    recommendations = get_recommendations(current_mood, current_stress)
    
    return render_template(
        "wellbeing.html",
        user=user,
        current_mood=current_mood,
        current_stress=current_stress,
        warning_msg=warning_msg,
        recommendations=recommendations,
        # Chart Data
        emotion_counts=emotion_counts,
        line_labels=line_labels,
        line_data=line_data
    )
