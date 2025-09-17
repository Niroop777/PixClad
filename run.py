# run.py
import os
from app import create_app, db

app = create_app()

@app.route("/health")
def health():
    return {"status": "ok", "message": "Backend is running!"}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    # listen on 0.0.0.0 so Render can reach it
    app.run(host="0.0.0.0", port=port, debug=False)
