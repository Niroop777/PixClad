# app/storage.py
import os
from dotenv import load_dotenv
load_dotenv()

STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "s3")  # "s3" | "gdrive" | "local"

if STORAGE_BACKEND == "gdrive":
    from .gdrive_storage import upload_to_gdrive

import boto3

def upload_file(filepath, category):
    """Uploads file based on selected backend and returns public URL or file path."""
    if STORAGE_BACKEND == "gdrive":
        # raise exceptions up to caller if not authorized
        return upload_to_gdrive(filepath)

    elif STORAGE_BACKEND == "s3":
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
        )
        bucket = os.getenv("AWS_S3_BUCKET")
        if not bucket:
            raise RuntimeError("AWS_S3_BUCKET not set in environment")

        # object key (folders simulated by key)
        s3_key = f"{category}/{os.path.basename(filepath)}"
        s3_client.upload_file(filepath, bucket, s3_key)
        region = os.getenv("AWS_REGION", "us-east-1")
        # Public URL pattern (works if object public or bucket policy allows)
        return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"

    else:
        # Local storage fallback: return path (caller removes or keeps file)
        return filepath
