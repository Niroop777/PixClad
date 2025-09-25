# # app/__init__.py
# import os
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_jwt_extended import JWTManager
# from flask_cors import CORS
# from dotenv import load_dotenv

# load_dotenv()

# db = SQLAlchemy()
# jwt = JWTManager()

# def create_app():
#     app = Flask(__name__)
#     CORS(app)

#     # Config
#     database_url = os.getenv("DATABASE_URL", "sqlite:///pixclad.db")
#     app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB max
#     app.config["SQLALCHEMY_DATABASE_URI"] = database_url
#     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#     app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret")

#     # Init extensions
#     db.init_app(app)
#     jwt.init_app(app)
#     CORS(app)

#     # Register blueprints
#     from .auth import auth_bp
#     app.register_blueprint(auth_bp)

#     from .routes import bp as api_bp
#     app.register_blueprint(api_bp)

#     # gdrive routes are inside routes.py and registered there as a blueprint
#     return app



# app/__init__.py
import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

jwt = JWTManager()
supabase: Client = None  # global Supabase client

def create_app():
    app = Flask(__name__)
    CORS(app)

    global supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    supabase = create_client(supabase_url, supabase_key)

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret")
    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB max

    jwt.init_app(app)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .routes import bp as api_bp
    app.register_blueprint(api_bp)

    return app
