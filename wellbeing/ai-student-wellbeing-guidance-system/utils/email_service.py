from flask_mail import Message, Mail
from flask import current_app


def send_emergency_email(user, stress_score, recent_logs, context="High Stress Detected"):

    mail = Mail(current_app)

    contact_email = user.get("emergency_email")

    if not contact_email:
        print("No emergency email found")
        return False

    msg = Message(
        subject=f"⚠️ URGENT: Wellbeing Alert for {user.get('name')}",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[contact_email]
    )

    msg.body = f"""
Emergency Alert

Student: {user.get('name')}
Stress Score: {stress_score}

The AI Student Wellbeing System detected high stress.

Please check on the student immediately.
"""

    try:
        mail.send(msg)
        print("REAL EMAIL SENT")
        return True

    except Exception as e:
        print("EMAIL ERROR:", e)
        return False