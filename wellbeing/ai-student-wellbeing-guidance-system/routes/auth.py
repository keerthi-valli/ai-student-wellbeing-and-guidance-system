from flask import Blueprint, request, render_template, redirect, url_for, flash, session
import bcrypt
from extensions import mongo

auth = Blueprint("auth", __name__)

# =========================
# REGISTER
# =========================
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        if mongo.db.users.find_one({"email": email}):
            flash("Email already exists", "danger")
            return redirect(url_for("auth.register"))

        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Module 8: Emergency System Redesign
        emergency_contact_name = request.form.get("emergency_contact_name")
        emergency_phone = request.form.get("emergency_phone")
        emergency_email = request.form.get("emergency_email")

        mongo.db.users.insert_one({
            "name": name,
            "email": email,
            "password": hashed_pw,
            "role": role,
            "emergency_contact_name": emergency_contact_name,
            "emergency_phone": emergency_phone,
            "emergency_email": emergency_email
        })

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# =========================
# LOGIN
# =========================
@auth.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, redirect to dashboard
    if "user_id" in session:
        role = session.get("role")
        if role == "student":
            return redirect(url_for("dashboard_student"))
        elif role == "company_employee":
            return redirect(url_for("dashboard_employee"))
        elif role == "counselor":
            return redirect(url_for("counselor.dashboard"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = mongo.db.users.find_one({"email": email})

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):

            # ✅ SESSION STORAGE (FINAL & CORRECT)
            session.permanent = True
            session["user_id"] = str(user["_id"])
            session["user_email"] = user["email"]
            session["role"] = user["role"]
            session["user_name"] = user["name"] # Useful for templates

            if user["role"] == "student":
                return redirect(url_for("dashboard_student"))
            elif user["role"] == "company_employee":
                return redirect(url_for("dashboard_employee"))
            elif user["role"] == "company_manager":
                return redirect(url_for("company.dashboard_company"))
            elif user["role"] == "counselor":
                return redirect(url_for("counselor.dashboard"))

        flash("Invalid email or password", "danger")

    return render_template("login.html")


# =========================
# LOGOUT
# =========================
@auth.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))