# app/auth.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from dotenv import load_dotenv
import os

from . import supabase

load_dotenv()

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# -------------------------
# Register
# -------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"msg": "Missing email or password"}), 400

    # Check if user already exists
    existing = supabase.table("users").select("*").eq("email", data["email"]).execute()
    if existing.data and len(existing.data) > 0:
        return jsonify({"msg": "User already exists"}), 400

    hashed_password = generate_password_hash(data["password"])

    # Insert new user into Supabase
    user_data = {"email": data["email"], "password_hash": hashed_password}
    res = supabase.table("users").insert(user_data).execute()
    if not res.data:
        return jsonify({"msg": "Failed to create user"}), 500

    return jsonify({"msg": "User created successfully"}), 201

# -------------------------
# Login
# -------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"msg": "Missing email or password"}), 400

    # Fetch user from Supabase
    res = supabase.table("users").select("*").eq("email", data["email"]).execute()
    if not res.data or len(res.data) == 0:
        return jsonify({"msg": "Invalid credentials"}), 401

    user = res.data[0]
    if not check_password_hash(user["password_hash"], data["password"]):
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user["id"]))
    return jsonify({"access_token": access_token}), 200
