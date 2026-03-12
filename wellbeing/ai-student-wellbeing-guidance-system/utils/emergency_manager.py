from datetime import datetime
from extensions import mongo
from utils.email_service import send_emergency_email

def check_emergency(stress_score, user, emotion=None):
    """
    Checks emergency status using PATTERN-BASED Logic.
    
    Levels:
    1. Calm Mode (Single spike > 50) -> Motivational Quote
    2. Recommendation Mode (Persistent > 70) -> Counselor
    3. Critical Mode (Persistent > 85 OR Keywords) -> Email Alert
    
    Returns: dict with level, message, action, alert_sent
    """
    
    try:
        current_score = int(stress_score)
    except:
        current_score = 0
        
    user_id = user.get("_id")
    
    # --- 1. Fetch History (Pattern Recognition) ---
    # Get last 5 logs (including current if saved, but we might be pre-save or just saved)
    # We'll fetch last 5 *other* logs to see history + current
    recent_logs = list(mongo.db.daily_logs.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(5))
    
    # Calculate how many recent logs were high stress
    high_stress_count = 0
    critical_stress_count = 0
    
    # Add current entry to analysis effectively
    if current_score >= 70: high_stress_count += 1
    if current_score > 85: critical_stress_count += 1
    
    for log in recent_logs:
        # Avoid double counting if the current log is already in DB (likely is)
        # But for safety, simple counter is fine for "last N entries"
        try:
            s_score = int(log.get("stress_score", 0) if isinstance(log.get("stress_score"), (int, str)) else 0)
        except:
            s_score = 0
            
        if s_score >= 70: high_stress_count += 1
        if s_score > 85: critical_stress_count += 1

    # --- 2. Determine Level ---
    
    # LEVEL 3: CRITICAL (Persistent Severe Stress)
    # Rule: Current > 85 AND at least 2 others in recent history > 85
    # OR: Immediate DANGER keywords (handled by mood engine, but if mood is 'Distress' we can escalate)
    
        # Trigger Email
    # LEVEL 3: CRITICAL
    if current_score >= 9:
        email_sent = send_emergency_email(user, current_score, recent_logs, context="Critical Stress")
        return {
            "level": 3,
            "message": "⚠️ CRITICAL DISTRESS DETECTED",
            "category": "danger",
            "action": "contact_alert",
            "alert_sent": email_sent,
            "recommendation": "Emergency contact has been notified."
            }
    # LEVEL 2: HIGH STRESS
    elif current_score >= 7:
        return {
            "level": 2,
            "message": "You seem very stressed.",
            "category": "warning",
            "action": "recommend_counselor",
            "alert_sent": False,
            "recommendation": "Consider speaking with a counselor."
            }
    # LEVEL 1: MODERATE STRESS
    elif current_score >= 4:
        return {
            "level": 1,
            "message": "Take a moment to relax.",
            "category": "info",
            "action": "suggest_meditation",
            "alert_sent": False,
            "recommendation": "Try a breathing exercise."
            }
    # LEVEL 0: STABLE
    else:
        return {
            "level": 0,
            "message": "You are doing well.",
            "category": "success",
            "action": "none",
            "alert_sent": False,
            "recommendation": "Keep up the good work."
            }