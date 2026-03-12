from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import mongo
from datetime import datetime
from bson import ObjectId
from utils.decorators import login_required, role_required

academic = Blueprint("academic", __name__)

# =========================
# ROOT ACADEMIC REDIRECT (🔥 ADD HERE)
# =========================
@academic.route("/academic")
@login_required
def academic_root():
    role = session.get("role")

    if role == "student":
        return redirect(url_for("academic.academic_student"))
    elif role == "company_employee":
        return redirect(url_for("academic.academic_employee"))
    else:
        return redirect(url_for("auth.login"))


# =========================
# STUDENT ACADEMIC
# =========================
@academic.route("/academic/student", methods=["GET", "POST"])
@login_required
def academic_student():
    db = mongo.db
    user_id = ObjectId(session["user_id"])
    user = db.users.find_one({"_id": user_id})

    if not user:
        return redirect(url_for("auth.login"))

    # --- Handle Form Submission ---
    if request.method == "POST":
        action = request.form.get("action")
        
        # 1. Subject Difficulty Report (Existing)
        if action == "report_difficulty":
            db.academic_reports.insert_one({
                "user_id": user_id, # Changed to user_id for consistency
                "user_email": user["email"],
                "role": "student",
                "subject": request.form.get("subject"),
                "difficulty_level": request.form.get("difficulty_level"),
                "remarks": request.form.get("remarks"),
                "created_at": datetime.utcnow()
            })
            flash("Academic difficulty submitted successfully", "success")
            
        # 2. Create Roadmap (New)
        elif action == "create_roadmap":
            from utils.roadmap_engine import generate_roadmap
            
            # Get latest mood/stress for adaptation
            latest_log = db.daily_logs.find_one(
                {"user_id": session["user_id"]},
                sort=[("created_at", -1)]
            )
            
            mood_data = {
                "stress_score": latest_log.get("stress_score", 50) if latest_log else 50,
                "stress_level": latest_log.get("stress_score", "Medium") if latest_log else "Medium",
                "mood": latest_log.get("emotion", "Neutral") if latest_log else "Neutral"
            }
            
            profile = {
                "subject": request.form.get("roadmap_subject"),
                "custom_subject": request.form.get("custom_subject"),
                "level": request.form.get("level"),
                "daily_hours": int(request.form.get("daily_hours")),
                "goal": request.form.get("goal"),
                "exam_date": request.form.get("exam_date")
            }
            
            # Generate Roadmap
            roadmap_result = generate_roadmap(profile, mood_data)
            
            # Save to DB
            db.academic_profiles.update_one(
                {"user_id": user_id},
                {"$set": {
                    "user_id": user_id, 
                    "profile": profile,
                    "roadmap": roadmap_result,
                    "updated_at": datetime.utcnow()
                }},
                upsert=True
            )
            
            flash("Your personalized study roadmap has been generated!", "success")
            
        return redirect(url_for("academic.academic_student"))

    # --- Fetch Data for GET Request ---
    reports = list(db.academic_reports.find(
        {"user_email": user["email"], "role": "student"}
    ).sort("created_at", -1))
    
    # Fetch existing roadmap
    academic_profile = db.academic_profiles.find_one({"user_id": user_id})

    return render_template(
        "academic_student.html",
        user=user,
        reports=reports,
        academic_profile=academic_profile
    )


@academic.route("/academic/update_progress", methods=["POST"])
@login_required
def update_roadmap_progress():
    from flask import jsonify
    db = mongo.db
    user_id = ObjectId(session["user_id"])
    data = request.json
    
    topic_name = data.get("topic")
    week_num = int(data.get("week"))
    completed = data.get("completed")
    
    # Determine collection based on role
    role = session.get("role", "student")
    collection = db.academic_profiles if role == "student" else db.skill_profiles
    
    # 1. Fetch current profile
    profile_doc = collection.find_one({"user_id": user_id})
    if not profile_doc or "roadmap" not in profile_doc:
        return jsonify({"error": "Roadmap not found"}), 404
        
    roadmap_data = profile_doc["roadmap"]
    weeks = roadmap_data.get("roadmap", [])
    
    # 2. Update specific topic
    total_topics = 0
    completed_topics = 0
    
    for week in weeks:
        if week["week"] == week_num:
            for t in week["topics"]:
                if t["topic"] == topic_name:
                    t["completed"] = completed
                    
    # 3. Recalculate totals
    for week in weeks:
        for t in week["topics"]:
            total_topics += 1
            if t.get("completed"):
                completed_topics += 1
                
    progress_percentage = int((completed_topics / total_topics) * 100) if total_topics > 0 else 0
    
    # 4. Update DB
    collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "roadmap.roadmap": weeks,
            "roadmap.completed_topics": completed_topics,
            "roadmap.progress": progress_percentage,
            "updated_at": datetime.utcnow()
        }}
    )
    
    # 5. Update User Semester/Skill Progress
    field_to_update = "semester_progress" if role == "student" else "skill_progress"
    db.users.update_one(
        {"_id": user_id},
        {"$set": {field_to_update: progress_percentage}}
    )

    return jsonify({
        "success": True, 
        "progress": progress_percentage,
        "completed_topics": completed_topics,
        "total_topics": total_topics
    })


# =========================
# EMPLOYEE ACADEMIC
# =========================
@academic.route("/academic/employee", methods=["GET", "POST"])
@login_required
@role_required("company_employee")
def academic_employee():
    db = mongo.db
    user_id = ObjectId(session["user_id"])
    user = db.users.find_one({"_id": user_id})

    if not user:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        action = request.form.get("action")
        
        # 1. Skill Gap Report (Existing)
        if action == "report_skill_gap":
            db.academic_reports.insert_one({
                "user_id": user_id,
                "user_email": user["email"],
                "role": "employee",
                "skill_name": request.form.get("skill_name"),
                "difficulty_level": request.form.get("difficulty_level"),
                "remarks": request.form.get("remarks"),
                "created_at": datetime.utcnow()
            })
            flash("Skill gap submitted successfully", "success")
            
        # 2. Start Skill Journey (New)
        elif action == "create_skill_roadmap":
            from utils.roadmap_engine import generate_roadmap
            
            # Get latest mood/stress
            latest_log = db.daily_logs.find_one(
                {"user_id": user_id},
                sort=[("created_at", -1)]
            )
            
            mood_data = {
                "stress_score": latest_log.get("stress_score", 50) if latest_log else 50,
                "mood": latest_log.get("emotion", "Neutral") if latest_log else "Neutral"
            }
            
            skill_name = request.form.get("skill_name")
            
            profile = {
                "subject": "other", # Use "other" to trigger custom subject logic
                "custom_subject": skill_name,
                "level": request.form.get("current_level"),
                "daily_hours": int(request.form.get("daily_time_commitment", 1)),
                "goal": request.form.get("goal"),
                "start_date": datetime.utcnow().strftime("%Y-%m-%d")
            }
            
            # Generate Roadmap
            roadmap_result = generate_roadmap(profile, mood_data)
            
            # Save to skill_profiles
            db.skill_profiles.update_one(
                {"user_id": user_id},
                {"$set": {
                    "user_id": user_id,
                    "profile": profile,
                    "roadmap": roadmap_result,
                    "updated_at": datetime.utcnow()
                }},
                upsert=True
            )
            
            flash(f"Your skill development roadmap for '{skill_name}' has been created!", "success")

        return redirect(url_for("academic.academic_employee"))

    # GET Request
    reports = list(db.academic_reports.find(
        {"user_id": user_id, "role": "employee"}
    ).sort("created_at", -1))
    
    # Fetch existing skill profile
    skill_profile = db.skill_profiles.find_one({"user_id": user_id})

    return render_template(
        "academic_employee.html",
        user=user,
        reports=reports,
        skill_profile=skill_profile
    )
