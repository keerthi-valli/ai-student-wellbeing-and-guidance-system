from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from extensions import mongo
from bson import ObjectId
from utils.emergency_manager import check_emergency
from utils.email_service import send_emergency_email

emergency = Blueprint("emergency", __name__)

@emergency.route("/emergency")
def emergency_page():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    user = mongo.db.users.find_one({"_id": ObjectId(session["user_id"])})
    
    # Get latest log for current status
    latest_log = mongo.db.daily_logs.find_one(
        {"user_id": session["user_id"]},
        sort=[("created_at", -1)]
    )
    
    stress_value = latest_log.get("stress_score", 0) if latest_log else 0
    # Convert text stress levels to numbers
    stress_map = {
        "Low": 3,
        "Medium": 6,
        "High": 9
        }
    if isinstance(stress_value, str):
        stress_score = stress_map.get(stress_value, 0)
    else:
        stress_score = int(stress_value)
    print("DEBUG Stress Score:", stress_score)
    emotion = latest_log.get("emotion", "Neutral") if latest_log else "Neutral"
    
    # Calculate Risk Status
    risk_status = check_emergency(stress_score, user, emotion)
    
    return render_template(
        "emergency.html", 
        user=user,
        risk_status=risk_status,
        latest_log=latest_log
    )

@emergency.route("/emergency/send_alert", methods=["POST"])
def send_alert():
    print("DEBUG: send_alert route triggered") # Debug
    if "user_id" not in session:
        print("DEBUG: User not in session") # Debug
        return redirect(url_for("auth.login"))
        
    user = mongo.db.users.find_one({"_id": ObjectId(session["user_id"])})
    print(f"DEBUG: User found: {user.get('email')}") # Debug
    
    # Fetch recent history for the email
    recent_logs = list(mongo.db.daily_logs.find(
        {"user_id": session["user_id"]}
    ).sort("created_at", -1).limit(5))
    
    current_score = recent_logs[0].get("stress_score", 0) if recent_logs else 0
    current_emotion = recent_logs[0].get("emotion", "Neutral") if recent_logs else "Neutral"
    
    print(f"DEBUG: Current Score: {current_score}") # Debug
    
    # Check Risk Level
    risk_status = check_emergency(current_score, user, current_emotion)
    print(f"DEBUG: Calculated Risk Level: {risk_status.get('level')}")
    
    if risk_status.get("level") == 3:
        # Trigger Email
        print("DEBUG: Critical Risk detected. Sending email...") # Debug
        send_emergency_email(user, current_score, recent_logs, context="User Initiated Alert (Critical)")
        flash("Emergency Support Email has been sent to your contacts and counselor.", "success")
    else:
        print("DEBUG: Risk not Critical. Email skipped.") # Debug
        flash("Alert not sent. Your current stress level does not meet the critical threshold for automated external alerts. Please use the helpline numbers if you need immediate assistance.", "warning")
        
    return redirect(url_for("emergency.emergency_page"))
