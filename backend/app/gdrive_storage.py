# app/gdrive_storage.py
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request



BASE_DIR = os.path.dirname(__file__)
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")  # ensure this exists in repo
TOKEN_PATH = os.path.join(BASE_DIR, "gdrive_token.json")       # will be created after OAuth
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def get_gdrive_service():
    """
    Build a Google Drive service using saved credentials (gdrive_token.json).
    Raises an exception if token not present or invalid — caller should make user authorize.
    """
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError("GDrive token not found. Authorize via /gdrive/authorize first.")

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        # Try to refresh if refresh_token present
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, "w") as f:
                f.write(creds.to_json())
        else:
            raise Exception("GDrive credentials invalid or expired. Re-authorize at /gdrive/authorize")

    service = build("drive", "v3", credentials=creds)
    return service

def upload_to_gdrive(filepath, folder_id=None):
    """Uploads file to Google Drive and returns webViewLink (may require sharing settings)."""
    service = get_gdrive_service()
    file_metadata = {"name": os.path.basename(filepath)}
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaFileUpload(filepath, resumable=True)
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink"
    ).execute()

    # Optionally set file permission to anyoneWithLink (uncomment if needed)
    # service.permissions().create(fileId=uploaded_file['id'],
    #                              body={"role": "reader", "type": "anyone"}).execute()

    return uploaded_file.get("webViewLink")
