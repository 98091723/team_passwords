import os

class Config:
    SECRET_KEY = os.environ.get('%aaNdQYB3Xz:at6') or 'change-this-secret-key'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_SECURE = False  # Set to True in production (HTTPS)
    PERMANENT_SESSION_LIFETIME = 7200  # 2 hours in seconds
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    DATABASE = os.path.join(os.path.dirname(__file__), 'team_passwords.db')