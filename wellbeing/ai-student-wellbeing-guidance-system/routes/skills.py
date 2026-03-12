from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from extensions import mongo
from bson import ObjectId
from datetime import datetime
from utils.decorators import login_required

skills = Blueprint("skills", __name__)

def init_default_skills():
    """
    Initializes the skills collection with default data if empty.
    """
    if mongo.db.skills.count_documents({}) == 0:
        default_skills = [
            {
                "name": "Time Management",
                "description": "Learn to prioritize tasks and manage your time effectively.",
                "total_modules": 5,
                "icon": "fas fa-clock",
                "color": "primary"
            },
            {
                "name": "Stress Management",
                "description": "Techniques to handle stress and maintain mental peace.",
                "total_modules": 8,
                "icon": "fas fa-spa",
                "color": "success"
            },
            {
                "name": "Communication Skills",
                "description": "Improve your verbal and non-verbal communication.",
                "total_modules": 6,
                "icon": "fas fa-comments",
                "color": "info"
            },
            {
                "name": "Emotional Intelligence",
                "description": "Understand and manage your own emotions and others.",
                "total_modules": 4,
                "icon": "fas fa-brain",
                "color": "warning"
            },
            {
                "name": "Python Basics",
                "description": "Introduction to Python programming language.",
                "total_modules": 10,
                "icon": "fab fa-python",
                "color": "danger"
            }
        ]
        mongo.db.skills.insert_many(default_skills)

@skills.route("/skills")
@login_required
def skills_dashboard():
    # Ensure default skills exist
    init_default_skills()
    
    user_id = session["user_id"]
    
    # Fetch all available skills
    all_skills = list(mongo.db.skills.find({}))
    
    # Fetch user's progress
    user_progress = list(mongo.db.user_skills.find({"user_id": ObjectId(user_id)}))
    
    # Create a map for easy lookup: skill_id -> progress_doc
    progress_map = {str(p["skill_id"]): p for p in user_progress}
    
    final_skills = []
    
    for skill in all_skills:
        skill_id = str(skill["_id"])
        
        # Get progress or default
        prog = progress_map.get(skill_id, {})
        completed = prog.get("completed_modules", 0)
        total = skill["total_modules"]
        
        # Calculate Percentage
        percent = int((completed / total) * 100) if total > 0 else 0
        
        # Enhance skill object for template
        skill["user_completed"] = completed
        skill["user_percent"] = percent
        skill["is_completed"] = (completed >= total)
        
        final_skills.append(skill)
        
    return render_template("skills.html", skills=final_skills, user=mongo.db.users.find_one({"_id": ObjectId(user_id)}))

@skills.route("/skills/update/<skill_id>", methods=["POST"])
@login_required
def update_progress(skill_id):
    user_id = session["user_id"]
    action = request.json.get("action") # 'increment' or 'reset'
    
    skill = mongo.db.skills.find_one({"_id": ObjectId(skill_id)})
    if not skill:
        return jsonify({"error": "Skill not found"}), 404
        
    total = skill["total_modules"]
    
    # Get current progress
    progress = mongo.db.user_skills.find_one({
        "user_id": ObjectId(user_id), 
        "skill_id": ObjectId(skill_id)
    })
    
    current_completed = progress["completed_modules"] if progress else 0
    
    new_completed = current_completed
    
    if action == "increment":
        if current_completed < total:
            new_completed += 1
    elif action == "reset":
        new_completed = 0
        
    # Update or Insert
    mongo.db.user_skills.update_one(
        {"user_id": ObjectId(user_id), "skill_id": ObjectId(skill_id)},
        {
            "$set": {
                "completed_modules": new_completed,
                "last_updated": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    # Calculate new percentage for response
    new_percent = int((new_completed / total) * 100) if total > 0 else 0
    is_completed = (new_completed >= total)
    
    return jsonify({
        "success": True, 
        "new_completed": new_completed,
        "total": total,
        "new_percent": new_percent,
        "is_completed": is_completed
    })
