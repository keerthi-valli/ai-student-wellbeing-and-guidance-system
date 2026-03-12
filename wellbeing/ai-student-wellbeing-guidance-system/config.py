import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supersecretkey_change_this_in_production"
    MONGO_URI = os.environ.get("MONGO_URI")
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") or "AIzaSyAtCf7gOICW0K6Uoma65y5XSeM8t0KR_AY"
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour session lifetime
    SESSION_PERMANENT = True
