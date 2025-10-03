# import os
# from app import create_app

# app = create_app()

# @app.route("/health")
# def health():
#     return {"status": "ok", "message": "Backend is running!"}

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port, debug=False)


#run.py

import os
from flask import redirect, session, request
from google_auth_oauthlib.flow import Flow
from app import create_app

app = create_app()
app.secret_key = "your_secret_key"   # required for session

# Allow http:// for local development
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

CLIENT_SECRETS_FILE = "app/client_secret.json"  # Download from GCP Console
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
REDIRECT_URI = "http://127.0.0.1:5000/gdrive/callback"


@app.route("/health")
def health():
    return {"status": "ok", "message": "Backend is running!"}


@app.route("/gdrive/authorize")
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )
    session["state"] = state
    return redirect(auth_url)


@app.route("/gdrive/callback")
def oauth2callback():
    state = session["state"]
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI,
    )
    flow.fetch_token(authorization_response=request.url)

    creds = flow.credentials
    with open("credentials.json", "w") as f:
        f.write(creds.to_json())

    return {"status": "ok", "message": "Authorization complete! credentials.json saved."}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
