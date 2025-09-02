# config.py (Updated for SQLite)
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "users.db")

SECRET_KEY = "your-secret-key"

# Flask-Mail Configuration
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = "punith.dataclad@gmail.com"
MAIL_PASSWORD = "mbdmvatasjognpzg"
MAIL_DEFAULT_SENDER = "punith.dataclad@gmail.com"
