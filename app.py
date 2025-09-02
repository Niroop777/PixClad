import json
import os
import sqlite3
import boto3
import shutil
import time
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_session import Session
from itsdangerous import URLSafeTimedSerializer
import config
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from flask import Flask, request, jsonify  # Ensure request is imported

from concurrent.futures import ThreadPoolExecutor
from googleapiclient.http import MediaIoBaseUpload
from flask import Flask, request, jsonify, session, Request
import google.oauth2.credentials



import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.http
from flask_sqlalchemy import SQLAlchemy
from googleapiclient.http import MediaIoBaseUpload
from google.api_core import retry

#  Load Environment Variables
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")
S3_UPLOAD_PATH = os.getenv("S3_UPLOAD_PATH")

app = Flask(__name__)
app.config.from_object(config)

# Configuring SQL database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Creating database model
class GoogleDriveURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)

#  Configure Flask Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#  Initialize Bcrypt & Mail
bcrypt = Bcrypt(app)
mail = Mail(app)

#  Serializer for Password Reset Tokens
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

#  Function to Connect to SQLite Database
def get_db_connection():
    conn = sqlite3.connect(config.DATABASE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

# @app.route("/")
# def home():
#     return "Flask and SQLite are connected!"

#  Forgot Password Route
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            token = serializer.dumps(email, salt="password-reset")
            reset_link = url_for("reset_password", token=token, _external=True)

            try:
                msg = Message("Password Reset Request", recipients=[email])
                msg.body = f"Click the link to reset your password: {reset_link}"
                mail.send(msg)
                flash("Password reset link has been sent to your email.", "info")
            except Exception as e:
                flash(f"Error sending email: {str(e)}", "danger")
        else:
            flash("No account found with that email.", "danger")

    return render_template("forgot_password.html")

#  Reset Password Route
@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = serializer.loads(token, salt="password-reset", max_age=3600)
    except:
        flash("The password reset link is invalid or has expired.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("reset_password", token=token))

        hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, email))
        conn.commit()
        conn.close()

        flash("Your password has been reset successfully!", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html")

#  Registration Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, name, email, password) VALUES (?, ?, ?, ?)",
                (username, name, email, hashed_password),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Username or email already exists!", "danger")
        finally:
            conn.close()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

#  Login Route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.check_password_hash(user["password"], password):
            session["logged_in"] = True
            session["username"] = user["username"]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")

#  Dashboard Route
@app.route("/dashboard")
def dashboard():
    if "logged_in" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    
    return render_template("dashboard.html", username=session.get("username"))

# Google Drive Authentication
# Google Drive Authentication
# Add these at the top of your app.py
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Only for development
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True



@app.route("/google_drive_auth")
def google_drive_auth():
    if 'credentials' in session:
        return redirect(url_for('google_drive'))
        
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=[
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive.metadata.readonly"
        ]
    )
    flow.redirect_uri = url_for("oauth_callback", _external=True)
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    session["oauth_state"] = state
    return redirect(authorization_url)

@app.route("/oauth_callback")
def oauth_callback():
    if 'oauth_state' not in session:
        flash("OAuth state missing. Please try again.", "danger")
        return redirect(url_for("google_drive_auth"))

    state = session['oauth_state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=[
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive.metadata.readonly"
        ],
        state=state
    )
    flow.redirect_uri = url_for("oauth_callback", _external=True)

    try:
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        
        session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        flash("Successfully connected to Google Drive!", "success")
        return redirect(url_for('google_drive'))
    except Exception as e:
        print(f"OAuth callback error: {str(e)}")
        flash("Failed to authenticate with Google Drive. Please try again.", "danger")
        return redirect(url_for("google_drive_auth"))

@app.route("/upload_to_drive", methods=["POST"])
def upload_to_drive():
    if 'credentials' not in session:
        return jsonify({
            "success": False,
            "message": "Not authenticated with Google Drive"
        }), 401

    try:
        credentials = google.oauth2.credentials.Credentials(
            **session['credentials']
        )

        # Check if credentials are expired
        if credentials.expired:
            if credentials.refresh_token:
                request_obj = google.auth.transport.requests.Request()
                credentials.refresh(request_obj)
                
                # Update session with new credentials
                session['credentials'] = {
                    'token': credentials.token,
                    'refresh_token': credentials.refresh_token,
                    'token_uri': credentials.token_uri,
                    'client_id': credentials.client_id,
                    'client_secret': credentials.client_secret,
                    'scopes': credentials.scopes
                }
            else:
                return jsonify({
                    "success": False,
                    "message": "Credentials expired. Please re-authenticate."
                }), 401

        drive_service = googleapiclient.discovery.build('drive', 'v3', credentials=credentials)

        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "message": "No file provided"
            }), 400

        files = request.files.getlist('file')
        
        if len(files) > 10:
            return jsonify({
                "success": False,
                "message": "Maximum 10 files allowed"
            }), 400

        responses = []
        for file in files:
            if file.filename:
                try:
                    file_metadata = {'name': secure_filename(file.filename)}
                    media = MediaIoBaseUpload(
                        file,
                        mimetype=file.content_type or 'application/octet-stream',
                        resumable=True
                    )
                    
                    file = drive_service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()
                    
                    responses.append({
                        'filename': file.filename,
                        'id': file.get('id'),
                        'success': True
                    })
                except Exception as e:
                    print(f"Error uploading {file.filename}: {str(e)}")
                    responses.append({
                        'filename': file.filename,
                        'success': False,
                        'error': str(e)
                    })

        if not responses:
            return jsonify({
                "success": False,
                "message": "No files were uploaded"
            }), 400

        return jsonify({
            "success": True,
            "message": "Files uploaded successfully",
            "files": responses
        })

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error during upload: {str(e)}"
        }), 500

@app.route("/google_drive")
def google_drive():
    if 'credentials' not in session:
        return render_template('google_drive.html', authenticated=False)
    return render_template('google_drive.html', authenticated=True)

    
# Upload URL to SQLite
@app.route("/upload_url", methods=["POST"])
def upload_url():
    url = request.form.get("url")

    if not url:
        return jsonify({"success": False, "message": "Please enter a valid URL!"}), 400

    new_url = GoogleDriveURL(url=url)
    db.session.add(new_url)
    db.session.commit()

    return jsonify({"success": True, "message": "URL saved successfully!"})

#  Logout Route
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

#  Google Drive Route
# @app.route("/google_drive")
# def google_drive():
#     return render_template("google_drive.html")

# Amazon S3 Connection
@app.route("/amazon_s3", methods=["GET", "POST"])
def amazon_s3():
    if request.method == "POST":
        access_key = request.form.get("access_key")
        secret_key = request.form.get("secret_key")

        if not access_key or not secret_key:
            flash("Please enter both Access Key and Secret Key!", "danger")
            return redirect(url_for("amazon_s3"))

        try:
            # Initialize S3 Client
            s3 = boto3.client(
                "s3",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=AWS_REGION
            )

            # Test authentication
            s3.head_bucket(Bucket=AWS_BUCKET_NAME)

            # Store credentials in session
            session["s3_access_key"] = access_key
            session["s3_secret_key"] = secret_key

            flash("Amazon S3 connected successfully!", "success")
            return redirect(url_for("s3_connected"))

        except ClientError as e:
            flash(f"AWS Authentication Failed: {e.response['Error']['Message']}", "danger")

    return render_template("amazon_s3.html")

# File Upload Route
@app.route("/upload_file", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("No file part!", "danger")
        return redirect(url_for("s3_connected"))

    files = request.files.getlist("file")  # Get multiple files
    upload_option = request.form.get("upload_option")

    if not files or all(file.filename == "" for file in files):
        flash("No selected files!", "danger")
        return redirect(url_for("s3_connected"))

    if len(files) > 10:
        flash("You can only upload up to 10 files at a time!", "danger")
        return redirect(url_for("s3_connected"))

    s3 = boto3.client(
        "s3",
        aws_access_key_id=session.get("s3_access_key"),
        aws_secret_access_key=session.get("s3_secret_key"),
        region_name=AWS_REGION
    )

    messages = []  # Store messages to prevent duplicate flashes

    def upload_single_file(file):
        """Uploads a single file to S3 (Multi-Part Upload for Large Files)"""
        if file:
            filename = secure_filename(file.filename)
            s3_path = f"{S3_UPLOAD_PATH}{filename}"

            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            try:
                if file_size > 100 * 1024 * 1024:  # If file > 100MB, use Multi-Part Upload
                    upload_large_file(s3, file, filename, s3_path)
                else:
                    # Direct Upload for Small Files
                    s3.upload_fileobj(file, AWS_BUCKET_NAME, s3_path, ExtraArgs={"ServerSideEncryption": "AES256"})

                return f"File {filename} uploaded successfully!", "success"
            except ClientError as e:
                return f"Error uploading {filename}: {str(e)}", "danger"

    # Multi-Threaded Upload for Batch Files
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(upload_single_file, files))

    # Flash messages once to avoid duplicates
    for message, category in results:
        messages.append((message, category))

    for message, category in messages:
        flash(message, category)

    return redirect(url_for("s3_connected"))

def upload_large_file(s3, file, filename, s3_path):
    """Multi-Part Upload for Large Files with Server-Side Encryption"""
    try:
        # Step 1: Create Multipart Upload (Include Server-Side Encryption)
        multipart_upload = s3.create_multipart_upload(
            Bucket=AWS_BUCKET_NAME,
            Key=s3_path,
            ServerSideEncryption="AES256"  # Correct way to set encryption
        )

        parts = []
        chunk_size = 50 * 1024 * 1024  # 50MB per part
        part_number = 1

        while chunk := file.read(chunk_size):
            part = s3.upload_part(
                Bucket=AWS_BUCKET_NAME,
                Key=s3_path,
                PartNumber=part_number,
                UploadId=multipart_upload["UploadId"],
                Body=chunk
            )
            parts.append({"ETag": part["ETag"], "PartNumber": part_number})
            part_number += 1

        # Step 2: Complete multi-part upload
        s3.complete_multipart_upload(
            Bucket=AWS_BUCKET_NAME,
            Key=s3_path,
            UploadId=multipart_upload["UploadId"],
            MultipartUpload={"Parts": parts}
        )

    except ClientError as e:
        # Step 3: Abort upload if an error occurs (prevents incomplete files)
        s3.abort_multipart_upload(
            Bucket=AWS_BUCKET_NAME,
            Key=s3_path,
            UploadId=multipart_upload["UploadId"]
        )
        flash(f"Error uploading {filename}: {str(e)}", "danger")

# S3 Connected Page
@app.route("/s3_connected")
def s3_connected():
    if "logged_in" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    return render_template("s3_connect.html", username=session.get("username"))

if __name__ == "__main__":
    app.run(host="localhost", port=5000, ssl_context=("cert.pem", "key.pem"), debug=True)