from flask import Blueprint, render_template, session, redirect, url_for, flash
from extensions import mongo
from bson import ObjectId

company = Blueprint("company", __name__)

@company.route("/dashboard/company")
def dashboard_company():
    if "user_id" not in session or session.get("role") != "company_manager":
        return redirect(url_for("auth.login"))

    # 1. Get Manager's Company
    manager = mongo.db.users.find_one({"_id": ObjectId(session["user_id"])})
    company_name = manager.get("company_name")

    if not company_name:
        flash("Company profile incomplete.", "warning")
        return redirect(url_for("profile.edit_profile"))

    # 2. Get All Employees of this company
    employees = list(mongo.db.users.find({
        "role": "company_employee",
        "company_name": company_name
    }))

    # 3. Aggregate Data
    total_employees = len(employees)
    active_concerns = 0
    total_wellbeing_score = 0
    wellbeing_count = 0
    
    dept_distribution = {}
    risk_employees = []

    for emp in employees:
        # Department Count
        dept = emp.get("department", "Other")
        dept_distribution[dept] = dept_distribution.get(dept, 0) + 1

        # Get Latest Wellbeing Data
        latest_entry = mongo.db.emotional_analysis.find_one(
            {"user_id": str(emp["_id"])},
            sort=[("created_at", -1)]
        )

        emp_status = {
            "name": emp["name"],
            "department": dept,
            "status": "Unknown",
            "score": 0,
            "last_checkin": "Never"
        }

        if latest_entry:
            score = latest_entry.get("wellbeing_score", 0)
            stress = latest_entry.get("ai_stress", "Medium")
            
            emp_status["score"] = score
            emp_status["status"] = stress
            emp_status["last_checkin"] = latest_entry["created_at"].strftime("%Y-%m-%d")

            total_wellbeing_score += score
            wellbeing_count += 1

            # Risk Logic
            if score < 40 or stress == "High":
                active_concerns += 1
                risk_employees.append(emp_status)
        
        # If we have basic diary entry but not emotional analysis (legacy)
        elif mongo.db.diary_entries.find_one({"user_id": str(emp["_id"])}):
             # Just fallback if needed, but emotional_analysis is better
             pass

    avg_score = int(total_wellbeing_score / wellbeing_count) if wellbeing_count > 0 else 0

    return render_template(
        "dashboard_company.html",
        user=manager,
        company_name=company_name,
        total_employees=total_employees,
        active_concerns=active_concerns,
        avg_score=avg_score,
        dept_distribution=dept_distribution,
        risk_employees=risk_employees
    )
