# import os
# import shutil
# from flask import Flask, request, jsonify, session
# from datetime import timedelta
# from flask_cors import CORS
# from werkzeug.utils import secure_filename
# from config import Config
# from model_loader import get_image_tags
# from auth import auth_blueprint
# from gdrive import gdrive_blueprint

# # --- Initialize Flask App ---
# app = Flask(__name__)
# app.config.from_object(Config)
# # Update the CORS configuration to support credentials
# CORS(app, supports_credentials=True)

# # --- Register Blueprints ---
# app.register_blueprint(auth_blueprint, url_prefix='/auth')
# app.register_blueprint(gdrive_blueprint, url_prefix='/auth/gdrive')


# # --- App Configuration & Setup ---
# UPLOAD_FOLDER = 'temp_uploads'
# OUTPUT_FOLDER = 'sorted_output'
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)
# if not os.path.exists(OUTPUT_FOLDER):
#     os.makedirs(OUTPUT_FOLDER)

# # --- Make sessions permanent ---
# @app.before_request
# def make_session_permanent():
#     session.permanent = True
#     # Set the session to last for a long time, e.g., 30 days
#     app.permanent_session_lifetime = timedelta(days=30)


# # --- The Only Endpoint for Uploads ---
# @app.route('/api/process-upload', methods=['POST'])
# def process_upload():
#     """
#     Handles both single file and multiple file/folder uploads,
#     sorts them using the AI model, and saves them into categorized subdirectories.
#     """
#     # Use 'files' as the key to get the list of files from the frontend
#     uploaded_files = request.files.getlist('files')
    
#     if not uploaded_files or not uploaded_files[0].filename:
#         return jsonify({"error": "No files were selected or uploaded"}), 400

#     results = {}
#     for file in uploaded_files:
#         # Sanitize the filename to prevent path issues and for security
#         filename = secure_filename(os.path.basename(file.filename))
        
#         # 1. Save the file temporarily
#         temp_path = os.path.join(UPLOAD_FOLDER, filename)
#         file.save(temp_path)

#         # 2. Analyze the image with your YOLO model
#         tags = get_image_tags(temp_path)
        
#         # 3. Determine the destination folder
#         target_category = tags[0] if tags and tags[0] != "Error" else "Uncategorized"
#         results[filename] = tags
        
#         # 4. Create the new sorted folder if it doesn't exist
#         destination_folder = os.path.join(OUTPUT_FOLDER, target_category)
#         os.makedirs(destination_folder, exist_ok=True)
        
#         # 5. Move the file from the temporary location to the sorted folder
#         shutil.move(temp_path, os.path.join(destination_folder, filename))

#     return jsonify({"message": "Processing complete", "results": results})

# # --- Main Execution ---
# if __name__ == '__main__':
#     app.run(debug=True, port=5001)



import os
import shutil
from flask import Flask, request, jsonify, session
from datetime import timedelta
from flask_cors import CORS
from werkzeug.utils import secure_filename
from config import Config
from model_loader import get_image_tags
from auth import auth_blueprint
from gdrive import gdrive_blueprint, upload_file_to_gdrive # <-- Modified import
from google.oauth2.credentials import Credentials # <-- Added import
from googleapiclient.discovery import build # <-- Added import


# --- Initialize Flask App ---
app = Flask(__name__)
app.config.from_object(Config)
# Update the CORS configuration to support credentials
CORS(app, supports_credentials=True)

# --- Register Blueprints ---
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(gdrive_blueprint, url_prefix='/auth/gdrive')


# --- App Configuration & Setup ---
UPLOAD_FOLDER = 'temp_uploads'
OUTPUT_FOLDER = 'sorted_output'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# --- Make sessions permanent ---
@app.before_request
def make_session_permanent():
    session.permanent = True
    # Set the session to last for a long time, e.g., 30 days
    app.permanent_session_lifetime = timedelta(days=30)


# --- Endpoint for Uploads (Updated) ---
@app.route('/api/process-upload', methods=['POST'])
def process_upload():
    # Get the destination from the form data (default to 'local')
    destination = request.form.get('destination', 'local')
    
    # If destination is gdrive, check for credentials
    if destination == 'gdrive' and 'credentials' not in session:
        return jsonify({"error": "Google Drive not connected"}), 401
    
    uploaded_files = request.files.getlist('files')
    if not uploaded_files or not uploaded_files[0].filename:
        return jsonify({"error": "No files were selected"}), 400

    results = {}
    gdrive_service = None
    if destination == 'gdrive':
        creds = Credentials(**session['credentials'])
        gdrive_service = build('drive', 'v3', credentials=creds)

    for file in uploaded_files:
        filename = secure_filename(os.path.basename(file.filename))
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)

        tags = get_image_tags(temp_path)
        target_category = tags[0] if tags and tags[0] != "Error" else "Uncategorized"
        results[filename] = tags
        
        if destination == 'local':
            # Move to a local sorted folder
            destination_folder = os.path.join(OUTPUT_FOLDER, target_category)
            os.makedirs(destination_folder, exist_ok=True)
            shutil.move(temp_path, os.path.join(destination_folder, filename))
        elif destination == 'gdrive':
            # Upload to Google Drive
            upload_file_to_gdrive(gdrive_service, temp_path, target_category)
            os.remove(temp_path) # Clean up the temp file

    return jsonify({"message": "Processing complete", "results": results})

# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)