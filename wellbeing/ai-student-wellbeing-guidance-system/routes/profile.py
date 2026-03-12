from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import mongo
from bson import ObjectId
from utils.decorators import login_required

profile = Blueprint("profile", __name__)

@profile.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    user = mongo.db.users.find_one({"_id": ObjectId(session["user_id"])})
    
    if request.method == "POST":
        update_data = {}
        
        # Common fields
        update_data["name"] = request.form.get("name")
        update_data["phone"] = request.form.get("phone")
        
        # Module 8: Emergency Contact
        update_data["emergency_contact_name"] = request.form.get("emergency_contact_name")
        update_data["emergency_phone"] = request.form.get("emergency_phone")
        update_data["emergency_email"] = request.form.get("emergency_email")
        
        # Role-specific fields
        if user["role"] == "student":
            update_data["education_level"] = request.form.get("education_level") # Class/Grade
            update_data["school_name"] = request.form.get("school_name")
            update_data["board"] = request.form.get("board")
            
            # College specific
            if user.get("education_level") not in ['10th', '11th', '12th']:
                 update_data["college_name"] = request.form.get("college_name")
                 update_data["degree"] = request.form.get("degree")
                 update_data["year"] = request.form.get("year")

        elif user["role"] == "company_employee":
            update_data["company_name"] = request.form.get("company_name")
            update_data["designation"] = request.form.get("designation")
            update_data["department"] = request.form.get("department")
            update_data["experience_years"] = request.form.get("experience_years")

        elif user["role"] == "counselor":
             update_data["specialization"] = request.form.get("specialization")
             update_data["experience_years"] = request.form.get("experience_years")

        # Update in DB
        mongo.db.users.update_one(
            {"_id": ObjectId(session["user_id"])},
            {"$set": update_data}
        )
        
        # Update session name if changed
        if update_data.get("name"):
            session["user_name"] = update_data["name"]

        flash("Profile updated successfully!", "success")
        
        # Redirect back to respective dashboard
        if user["role"] == "student":
            return redirect(url_for("dashboard_student"))
        elif user["role"] == "company_employee":
            return redirect(url_for("dashboard_employee"))
        elif user["role"] == "counselor":
            return redirect(url_for("dashboard_counselor"))
            
    return render_template("profile_edit.html", user=user)
