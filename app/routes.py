# app/routes.py
import os, uuid, magic
from flask import Blueprint, request, jsonify, redirect, session, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from dotenv import load_dotenv

from .classifier import classify_image
from .storage import upload_file
from . import supabase
load_dotenv()

bp = Blueprint("api", __name__, url_prefix="/api")

BASE_UPLOAD_FOLDER = "uploads"
os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)

import magic  # make sure this import is at the top of the file

def detect_file_type(filepath):
    # Windows-compatible magic
    try:
        ms = magic.Magic(mime=True)
        mime = ms.from_file(filepath)
    except Exception as e:
        # fallback
        print(f"[WARN] magic detection failed: {e}")
        mime = ""

    if mime.startswith("image"):
        return "image"
    elif mime.startswith("video"):
        return "video"
    elif mime.startswith("text"):
        return "text"
    return "other"


# -------------------------
# Upload Route
# -------------------------
@bp.route("/upload", methods=["POST"])
@jwt_required()
def upload():
    try:
        user_id = int(get_jwt_identity())
        file = request.files.get("file")
        if not file:
            return jsonify({"msg": "No file uploaded"}), 400

        temp_filename = f"{uuid.uuid4().hex}_{file.filename}"
        temp_filepath = os.path.join(BASE_UPLOAD_FOLDER, temp_filename)
        file.save(temp_filepath)
        current_app.logger.debug(f"File saved: {temp_filepath}")

        filetype = detect_file_type(temp_filepath)
        current_app.logger.debug(f"Detected filetype: {filetype}")

        category, confidence = "unclassified", None
        if filetype == "image":
            try:
                category, confidence = classify_image(temp_filepath)
                current_app.logger.debug(f"Classified: {category} ({confidence})")
            except Exception as e:
                current_app.logger.error(f"Classification failed: {e}")
                category = "unclassified"

        # Upload to storage backend
        try:
            file_url = upload_file(temp_filepath, category)
            current_app.logger.debug(f"File uploaded: {file_url}")
        except Exception as e:
            current_app.logger.error(f"Cloud upload failed: {e}")
            return jsonify({"msg": "Cloud upload failed", "error": str(e)}), 500

        # Remove local temp file after upload (if not local backend)
        if os.getenv("STORAGE_BACKEND", "s3") != "local":
            try:
                os.remove(temp_filepath)
            except OSError:
                pass

        # Insert file metadata into Supabase
        meta_data = {
            "user_id": user_id,
            "filename": file.filename,
            "filepath": file_url,
            "filetype": filetype,
            "category": category
        }
        res = supabase.table("file_meta").insert(meta_data).execute()
        meta_id = res.data[0]["id"]

        return jsonify({
            "msg": "File uploaded & analyzed",
            "file": {
                "id": meta_id,
                "name": file.filename,
                "type": filetype,
                "category": category,
                "confidence": confidence,
                "url": file_url
            }
        }), 201

    except Exception as e:
        current_app.logger.error(f"Unexpected failure: {e}", exc_info=True)
        return jsonify({"msg": "Internal server error", "error": str(e)}), 500


# -------------------------
# List Files Route
# -------------------------
@bp.route("/files", methods=["GET"])
@jwt_required()
def list_files():
    try:
        user_id = int(get_jwt_identity())
        files_res = supabase.table("file_meta").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        data = files_res.data
        return jsonify({"files": data}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to list files: {e}", exc_info=True)
        return jsonify({"msg": "Internal server error", "error": str(e)}), 500


# -------------------------
# Google Drive OAuth Routes
# -------------------------
from google_auth_oauthlib.flow import Flow
from .gdrive_storage import CREDENTIALS_PATH, TOKEN_PATH, SCOPES

gdrive_bp = Blueprint("gdrive", __name__, url_prefix="/gdrive")

@gdrive_bp.route("/authorize")
def gdrive_authorize():
    if not os.path.exists(CREDENTIALS_PATH):
        return "Google credentials.json not found on server. Place it at app/credentials.json", 500

    redirect_uri = os.getenv("GDRIVE_REDIRECT_URI")
    if not redirect_uri:
        return "GDRIVE_REDIRECT_URI not set in environment", 500

    flow = Flow.from_client_secrets_file(
        CREDENTIALS_PATH,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    auth_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")
    session["gdrive_oauth_state"] = state
    return redirect(auth_url)

@gdrive_bp.route("/callback")
def gdrive_callback():
    state = session.get("gdrive_oauth_state", None)
    redirect_uri = os.getenv("GDRIVE_REDIRECT_URI")
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_PATH,
        scopes=SCOPES,
        state=state,
        redirect_uri=redirect_uri
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())
    return "Google Drive authorization successful. You can close this page."

bp.register_blueprint(gdrive_bp)
