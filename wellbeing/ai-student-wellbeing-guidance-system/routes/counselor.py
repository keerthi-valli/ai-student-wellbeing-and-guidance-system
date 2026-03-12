from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from extensions import mongo
from bson import ObjectId
from datetime import datetime, timedelta
# Import decorators
from utils.decorators import login_required, role_required

counselor = Blueprint("counselor", __name__)

@counselor.route("/dashboard/counselor")
@login_required
# @role_required("counselor") # Uncomment if role_required is implemented
def dashboard():
    if session.get("role") != "counselor":
        return redirect(url_for("home"))

    user = mongo.db.users.find_one({"_id": ObjectId(session["user_id"])})
    
    # 1. Alert Notification Panel Logic
    # In a real app, this would query based on assigned students. 
    # For now, we'll simulate or query all students if none assigned.
    
    # Mocking/Fetching High Risk Students
    # Logic: Students with stress_level 'High' or recent negative moods
    # We will use a placeholder query until we have real risk data populated
    high_risk_students = list(mongo.db.users.find({"role": "student", "risk_level": "High"}).limit(5))
    medium_risk_students = list(mongo.db.users.find({"role": "student", "risk_level": "Medium"}).limit(5))
    low_risk_students = list(mongo.db.users.find({"role": "student", "risk_level": "Low"}).limit(5))
    
    high_risk_count = mongo.db.users.count_documents({"role": "student", "risk_level": "High"})
    medium_risk_count = mongo.db.users.count_documents({"role": "student", "risk_level": "Medium"})
    low_risk_count = mongo.db.users.count_documents({"role": "student", "risk_level": "Low"})
    
    # 2. Assigned Students List
    # For demo, just fetch any students
    assigned_students = list(mongo.db.users.find({"role": "student"}).limit(10)) 
    
    # 3. Emergency Cases (Severe)
    emergency_cases = list(mongo.db.users.find({"role": "student", "risk_level": "Critical"}).limit(3))

    return render_template(
        "dashboard_counselor_v3.html",
        user=user,
        high_risk_students=high_risk_students,
        medium_risk_students=medium_risk_students,
        low_risk_students=low_risk_students,
        high_risk_count=high_risk_count,
        medium_risk_count=medium_risk_count,
        low_risk_count=low_risk_count,
        assigned_students=assigned_students,
        emergency_cases=emergency_cases
    )

@counselor.route("/counselor/student/<student_id>")
@login_required
def student_report(student_id):
    if session.get("role") != "counselor":
        return redirect(url_for("home"))
        
    student = mongo.db.users.find_one({"_id": ObjectId(student_id)})
    if not student:
        flash("Student not found", "error")
        return redirect(url_for("counselor.dashboard"))
        
    # Mental Health Stats
    # Fetch AI summaries (NOT full text) - assuming a collection exists or using diary_entries for now
    # Ideally should use: mongo.db.diary_summaries.find(...)
    # For now, let's fetch diary entries but only show mood/keywords, NOT content
    recent_entries = list(mongo.db.diary_entries.find({"user_id": ObjectId(student_id)}).sort("created_at", -1).limit(5))
    
    # Mocking chart data for now if no analytics exist
    analytics_data = {
        "dates": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "scores": [65, 59, 80, 81, 56, 55, 40] # Mock data
    }
    
    return render_template("student_report.html", student=student, recent_entries=recent_entries, analytics=analytics_data)

@counselor.route("/counselor/profile")
@login_required
def profile():
    if session.get("role") != "counselor":
        return redirect(url_for("home"))
    
    user = mongo.db.users.find_one({"_id": ObjectId(session["user_id"])})
    return render_template("profile_counselor.html", user=user)

@counselor.route("/counselor/intervene/<student_id>", methods=["POST"])
@login_required
def add_intervention(student_id):
    if session.get("role") != "counselor":
        return redirect(url_for("home"))

    note = request.form.get("note")
    action = request.form.get("action") # e.g., "Schedule Session", "Send Message"
    
    if note or action:
        intervention = {
            "student_id": ObjectId(student_id),
            "counselor_id": ObjectId(session["user_id"]),
            "note": note,
            "action": action,
            "created_at": datetime.utcnow(),
            "status": "Pending"
        }
        mongo.db.interventions.insert_one(intervention)
        flash("Intervention recorded successfully.", "success")
        
    return redirect(url_for("counselor.student_report", student_id=student_id))
