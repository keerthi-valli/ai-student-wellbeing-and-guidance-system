from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("auth.login"))
            
            # Check if role matches (allow list of roles if needed in future)
            if session.get("role") != required_role:
                flash("Unauthorized access!", "danger")
                return redirect(url_for("home")) # Or a generic dashboard
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
