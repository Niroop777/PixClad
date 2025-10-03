
# app/config.py
import os
from dotenv import load_dotenv
load_dotenv()

# Storage configs
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "s3")  # s3 | gdrive | local
GDRIVE_REDIRECT_URI = os.getenv("GDRIVE_REDIRECT_URI")  # e.g., https://your-app.onrender.com/gdrive/callback

# Database configs
SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:SuperBase123%23123@db.dwmpziyuqugfjgacegpc.supabase.co:5432/postgres"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
