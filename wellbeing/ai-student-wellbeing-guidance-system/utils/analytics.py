from datetime import datetime, timedelta
from extensions import mongo
from bson import ObjectId

def get_user_analytics(user_id):
    """
    Fetches diary entries for the user and calculates:
    - Current Mood (most recent)
    - Stress Level (most recent)
    - Wellbeing Score (0-100)
    - Mood History (last 7 days for Chart.js)
    """
    
    # Defaults
    analytics = {
        "current_mood": "Neutral",
        "stress_level": "Medium",
        "wellbeing_score": 50,
        "history_labels": [],
        "history_data": [],
        "last_entry_date": "No entries yet",
        "mood_growth_percent": 0  # Default value
    }
    
    # Fetch last 7 days of entries
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    entries = list(mongo.db.diary_entries.find({
        "user_id": ObjectId(user_id),
        # "created_at": {"$gte": seven_days_ago} # Optional: Filter by date if needed strict 7 days
    }).sort("created_at", -1)) # Newest first

    if not entries:
        return analytics

    # --- Current Status (Most Recent) ---
    latest = entries[0]
    analytics["current_mood"] = latest.get("mood", "Neutral")
    analytics["stress_level"] = latest.get("stress_level", "Medium")
    analytics["last_entry_date"] = latest.get("created_at").strftime("%d %b, %Y")

    # --- Wellbeing Score Calculation ---
    # Simple algorithm: 
    # Mood: Happy(+20), Calm(+15), Neutral(+10), Sad(-10), Angry(-20)
    # Stress: Low(+20), Medium(+10), High(-20)
    # Base: 50
    
    score = 50
    mood_map = {
        "Happy": 20, "Excited": 20, "Calm": 15, "Relaxed": 15,
        "Neutral": 10,
        "Sad": -10, "Anxious": -15, "Angry": -20, "Frustrated": -15
    }
    stress_map = {
        "Low": 20, "low": 20,
        "Medium": 10, "medium": 10,
        "High": -20, "high": -20
    }
    
    # Calculate score based on last 5 entries to smooth it out
    recent_entries = entries[:5]
    if recent_entries:
        total_mood_pts = 0
        total_stress_pts = 0
        
        for e in recent_entries:
            m = e.get("mood", "Neutral")
            s = e.get("stress_level", "Medium")
            total_mood_pts += mood_map.get(m, 0)
            total_stress_pts += stress_map.get(s, 0)
            
        avg_mood = total_mood_pts / len(recent_entries)
        avg_stress = total_stress_pts / len(recent_entries)
        
        score = 50 + avg_mood + avg_stress
        
    # Clamp score 0-100
    analytics["wellbeing_score"] = max(0, min(100, int(score)))

    # --- Chart Data (Mood Trends - Last 7 Days) ---
    # Fetch detailed AI analysis if available
    chart_data = []
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # Try to fetch from emotional_analysis first (Module 6+)
    analysis_docs = list(mongo.db.emotional_analysis.find({
        "user_id": ObjectId(user_id),
        "created_at": {"$gte": seven_days_ago}
    }).sort("created_at", 1)) # Oldest to Newest
    
    if analysis_docs:
        # Use AI Scores (0-100)
        for doc in analysis_docs:
            date_str = doc.get("created_at").strftime("%d %b")
            score = doc.get("wellbeing_score", 50)
            analytics["history_labels"].append(date_str)
            analytics["history_data"].append(score)
            
        # Update current stats from latest analysis doc
        latest_doc = analysis_docs[-1]
        analytics["current_mood"] = latest_doc.get("ai_mood", analytics["current_mood"])
        analytics["stress_level"] = latest_doc.get("ai_stress", analytics["stress_level"])
        analytics["wellbeing_score"] = latest_doc.get("wellbeing_score", analytics["wellbeing_score"])
        
    else:
        # Fallback to Diary Entries (Legacy / Manual Input)
        # We want chronological order for the chart (Oldest -> Newest)
        # Taking last 7 entries
        chart_entries = entries[:7][::-1] 
        
        # Map mood to numeric value for chart (Legacy 1-5 scale mapped to 0-100 roughly)
        mood_chart_map = {
            "Happy": 90, "Excited": 90,
            "Calm": 75, "Relaxed": 75,
            "Neutral": 50,
            "Sad": 30, "Anxious": 25, "Frustrated": 25,
            "Angry": 10, "Stressed": 20
        }
        
        for e in chart_entries:
            date_str = e.get("created_at").strftime("%d %b")
            mood_val = mood_chart_map.get(e.get("mood", "Neutral"), 50)
            
            analytics["history_labels"].append(date_str)
            analytics["history_data"].append(mood_val)

    # --- 7-Day Growth Calculation ---
    # Logic: Compare AVG of First 3 Days vs AVG of Last 3 Days in the 7-day window.
    # entries are currently sorted Newest -> Oldest.
    
    # Filter entries strictly within last 7 days for growth calc
    growth_entries = [e for e in entries if e.get("created_at") >= seven_days_ago]
    
    # We need Chronological Order (Oldest -> Newest) for splitting
    growth_entries.sort(key=lambda x: x.get("created_at"))
    
    growth_percent = 0
    
    if len(growth_entries) >= 2:
        # Split into two groups
        # If < 6 entries, split in half. If >= 6, take first 3 and last 3.
        mid = len(growth_entries) // 2
        
        if len(growth_entries) >= 6:
            older_group = growth_entries[:3]
            newer_group = growth_entries[-3:]
        else:
            older_group = growth_entries[:mid]
            newer_group = growth_entries[mid:]
            
        def get_score_val(e):
            # Try to get a numeric score. 
            m = e.get("mood", "Neutral")
            s = e.get("stress_level", "Medium")
            
            # Simple score: 
            # Mood (0-50) + Stress (0-50, inverted)
            m_score = 25 # Neutral
            if m in ["Happy", "Excited", "Relaxed", "Calm"]: m_score = 45
            elif m in ["Sad", "Anxious", "Angry", "Frustrated"]: m_score = 10
            
            s_score = 25 # Medium
            if s in ["Low", "low"]: s_score = 45
            elif s in ["High", "high"]: s_score = 10
            
            return m_score + s_score

        # Calculate averages
        avg_old = sum(get_score_val(e) for e in older_group) / len(older_group)
        avg_new = sum(get_score_val(e) for e in newer_group) / len(newer_group)
        
        if avg_old > 0:
            change = avg_new - avg_old
            growth_percent = (change / avg_old) * 100
        else:
            growth_percent = 0 if avg_new == 0 else 100

    analytics["mood_growth_percent"] = round(growth_percent, 1)
        
    return analytics
