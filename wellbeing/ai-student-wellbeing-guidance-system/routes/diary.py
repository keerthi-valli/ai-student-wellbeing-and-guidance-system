from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import mongo
from datetime import datetime
from bson import ObjectId

diary = Blueprint("diary", __name__)

from utils.sentiment import analyze_sentiment

@diary.route("/diary", methods=["GET", "POST"])
def digital_diary():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = mongo.db.users.find_one(
        {"_id": ObjectId(session["user_id"])}
    )

    # Determine dashboard route
    dashboard_route = "dashboard_student" # Default
    if user.get("role") == "company_employee":
        dashboard_route = "dashboard_employee"
    elif user.get("role") == "counselor":
        dashboard_route = "dashboard_counselor"

    if request.method == "POST":
        # Handle Input Type
        input_type = request.form.get("input_type", "text")
        
        # Initialize fields
        text_content = ""
        audio_path = None
        transcript_text = None
        transcript_confidence = 0.0
        
        # Logic for Voice vs Text
        if input_type == "voice":
            from utils.voice_handler import process_voice_entry
            voice_data = request.form.get("voice_data")
            
            # Process voice (save + transcribe)
            processed = process_voice_entry(voice_data)
            
            if processed:
                transcript_text = processed["text"]
                transcript_confidence = processed["confidence"]
                audio_path = processed["audio_path"] # Relative path
                flash("Voice entry processed successfully!", "info")
            else:
                flash("Failed to process voice entry.", "danger")
                return redirect(url_for("diary.digital_diary"))
        else:
            # Text Mode
            text_content = request.form.get("diary_content")

        # Determine Content for Analysis
        analysis_content = ""
        if input_type == "text":
            analysis_content = text_content
        elif input_type == "voice" and transcript_text:
            analysis_content = transcript_text
            
        # Call AI Engine
        from utils.mood_engine import calculate_mood_and_stress
        
        # Default values if analysis is skipped (empty content)
        ai_analysis = {
            "mood": "Neutral",
            "stress_level": "Low",
            "score": 50,
            "breakdown": {}
        }
        
        if analysis_content:
             ai_analysis = calculate_mood_and_stress(analysis_content)
        
        # User manual overrides (optional)
        final_mood = request.form.get("mood")
        final_stress = request.form.get("stress_level")

        if not final_mood:
            final_mood = ai_analysis["mood"]
        
        if not final_stress:
            final_stress = ai_analysis["stress_level"]

        # Prepare Data for daily_logs
        # Schema: user_id, input_type, text_content, audio_path, transcript_text, transcript_confidence, emotion, sentiment_score, stress_score, pleasure_score, capacity_score, created_at
        
        entry_data = {
            "user_id": session["user_id"],
            "input_type": input_type,
            "text_content": text_content,
            "audio_path": audio_path,
            "transcript_text": transcript_text,
            "transcript_confidence": transcript_confidence,
            
            # Analysis Fields
            "emotion": final_mood, # Using 'emotion' field as requested, mapping to mood
            "stress_score": final_stress, # Storing string level as requested or could be mapped to score? User schema says 'stress_score', let's use the level string for consistency with UI or 0-100 if available. 
            # flexible handling: if stress_level is 'High', maybe we want a number? 
            # The user requested 'stress_score', 'pleasure_score', 'capacity_score'.
            # Existing AI analysis returns 'score' (wellbeing).
            # I will map AI 'score' to 'sentiment_score' and keep 'stress_level' string in 'stress_score' for now to match UI, 
            # OR I should check if calculate_mood_and_stress returns numbers. 
            # Checking code... it returns 'mood', 'stress_level', 'score'.
            
            "sentiment_score": ai_analysis.get("score", 0),
            
            # Placeholders for others not currently calculated by simple engine
            "pleasure_score": 0, 
            "capacity_score": 0,
            
            "created_at": datetime.utcnow()
        }
        
        mongo.db.daily_logs.insert_one(entry_data)
        
        # --- Module 8: Emergency Level Check ---
        from utils.emergency_manager import check_emergency
        
        # Get full user object for contact details
        full_user = mongo.db.users.find_one({"_id": ObjectId(session["user_id"])})
        
        emergency_result = check_emergency(entry_data["stress_score"], full_user, entry_data["emotion"])
        
        if emergency_result["level"] > 0:
            flash(emergency_result["message"], emergency_result["category"])
            flash(f"Recommendation: {emergency_result['recommendation']}", "info")
            if emergency_result["alert_sent"]:
                 flash("Emergency contact has been notified (Simulated).", "warning")
        else:
            # Standard Feedback
            if not request.form.get("mood") and analysis_content:
                 flash(f"AI Analysis: Mood detected as {final_mood}", "info")
            flash("Diary entry saved successfully", "success")
            
        return redirect(url_for("diary.digital_diary"))

    entries = list(
        mongo.db.daily_logs.find(
            {"user_id": session["user_id"]}
        ).sort("created_at", -1)
    )

    return render_template(
        "diary.html",
        user=user,
        entries=entries,
        dashboard_route=dashboard_route
    )
