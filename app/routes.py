# app/routes.py
import os, uuid, magic, shutil
from flask import Blueprint, request, jsonify, redirect, session, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import FileMeta, db
from .classifier import classify_image
from .storage import upload_file
from dotenv import load_dotenv

load_dotenv()

bp = Blueprint("api", __name__, url_prefix="/api")

BASE_UPLOAD_FOLDER = "uploads"
os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)

def detect_file_type(filepath):
    mime = magic.from_file(filepath, mime=True)
    if mime.startswith("image"):
        return "image"
    elif mime.startswith("video"):
        return "video"
    elif mime.startswith("text"):
        return "text"
    return "other"

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

        # Upload to selected backend
        try:
            file_url = upload_file(temp_filepath, category)
            current_app.logger.debug(f"File uploaded: {file_url}")
        except Exception as e:
            current_app.logger.error(f"Cloud upload failed: {e}")
            # keep local file for debugging; return helpful error
            return jsonify({"msg": "Cloud upload failed", "error": str(e)}), 500

        # Remove local temp file after successful upload (if backend is not 'local')
        if os.getenv("STORAGE_BACKEND", "s3") != "local":
            try:
                os.remove(temp_filepath)
            except OSError:
                pass

        meta = FileMeta(
            user_id=user_id,
            filename=file.filename,
            filepath=file_url,
            filetype=filetype,
            category=category
        )
        db.session.add(meta)
        db.session.commit()

        return jsonify({
            "msg": "File uploaded & analyzed",
            "file": {
                "id": meta.id,
                "name": meta.filename,
                "type": meta.filetype,
                "category": category,
                "confidence": confidence,
                "url": meta.filepath
            }
        }), 201

    except Exception as e:
        current_app.logger.error(f"Unexpected failure: {e}", exc_info=True)
        return jsonify({"msg": "Internal server error", "error": str(e)}), 500

# -------------------------
# Google Drive Web OAuth routes
# -------------------------
from google_auth_oauthlib.flow import Flow
from .gdrive_storage import CREDENTIALS_PATH, TOKEN_PATH, SCOPES  # note: CREDENTIALS_PATH defined in gdrive_storage

gdrive_bp = Blueprint("gdrive", __name__, url_prefix="/gdrive")
# store state in session - requires a secret key set in app config (JWT_SECRET_KEY is present)

@gdrive_bp.route("/authorize")
def gdrive_authorize():
    # Redirect user to Google for consent.
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
    # Google redirects here with ?code=...
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
    # save credentials to token file for server-side use
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())
    return "Google Drive authorization successful. You can close this page."

# Register gdrive blueprint on the same app
bp.register_blueprint(gdrive_bp)
