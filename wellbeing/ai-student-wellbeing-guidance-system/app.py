from flask import Flask, render_template, session, redirect, url_for, request, flash
from dotenv import load_dotenv
import os
from flask_mail import Mail,Message
load_dotenv()
from config import Config
from extensions import mongo
from bson import ObjectId
from datetime import datetime
from utils.decorators import login_required, role_required

app = Flask(__name__)
app.secret_key = "mysecretkey123"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yourgmail@gmail.com'
app.config['MAIL_PASSWORD'] = 'googleapppassword'

mail = Mail(app)

app.config["MONGO_URI"] = "mongodb://localhost:27017/student_wellbeing"

mongo.init_app(app)

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("home.html")

# =========================
# AUTH BLUEPRINT
# =========================
from routes.auth import auth
app.register_blueprint(auth)

# =========================
# ACADEMIC BLUEPRINT (🔥 REQUIRED)
# =========================
from routes.academic import academic
app.register_blueprint(academic)

# =========================
# PROFILE BLUEPRINT (🔥 ADDED)
# =========================
from routes.profile import profile
app.register_blueprint(profile)

# =========================
# WELLBEING & EMERGENCY (🔥 NEW)
# =========================
from routes.wellbeing import wellbeing
from routes.emergency import emergency
app.register_blueprint(wellbeing)
app.register_blueprint(emergency)

# Module 9: Skills
from routes.skills import skills
app.register_blueprint(skills)

# Module 10: Company Dashboard
from routes.company import company
app.register_blueprint(company)

# Module 11: Counselor Dashboard
from routes.counselor import counselor
app.register_blueprint(counselor)

from utils.analytics import get_user_analytics

# =========================
# DASHBOARDS
# =========================
@app.route("/dashboard/student")
@login_required # Use decorator
def dashboard_student():
    if session.get("role") != "student": # Keep role check or use @role_required
         return redirect(url_for("home"))

    user = mongo.db.users.find_one({"_id": ObjectId(session["user_id"])})
    analytics = get_user_analytics(session["user_id"])
    return render_template("dashboard_student.html", user=user, analytics=analytics)


@app.route("/dashboard/employee")
@login_required
def dashboard_employee():
    if session.get("role") != "company_employee":
        return redirect(url_for("home"))

    user = mongo.db.users.find_one({"_id": ObjectId(session["user_id"])})
    analytics = get_user_analytics(session["user_id"])
    return render_template("dashboard_employee.html", user=user, analytics=analytics)




# =========================
# OTHER MODULES
# =========================
# =========================
# OTHER MODULES
# =========================
from routes.diary import diary
app.register_blueprint(diary)

@app.route("/diary-redirect")
def diary_redirect():
    return redirect(url_for("diary.digital_diary"))

@app.route("/send_emergency")
@login_required
def send_emergency():

    user = mongo.db.users.find_one({"_id": ObjectId(session["user_id"])})
    emergency_email = user.get("emergency_email")

    print("DEBUG: emergency email =", emergency_email)

    try:
        msg = Message(
            subject="Emergency Alert",
            sender=app.config['MAIL_USERNAME'],
            recipients=[emergency_email]
        )

        msg.body = "Emergency alert! Please check the student immediately."

        mail.send(msg)

        print("DEBUG: EMAIL SENT")

    except Exception as e:
        print("EMAIL ERROR:", e)

    return redirect(url_for("dashboard_student"))
@app.route("/wellbeing")
@login_required
def wellbeing():
    user = mongo.db.users.find_one({"_id": ObjectId(session["user_id"])})
    return render_template("wellbeing.html", user=user)

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)

