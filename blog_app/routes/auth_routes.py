from functools import wraps

from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from blog_app.database import db
from blog_app.models import User

auth_bp = Blueprint("auth", __name__)


def login_required(func):
    """Decorator that ensures a user is logged in via session."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"message": "Authentication required"}), 401
        return func(*args, **kwargs)

    return wrapper


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True)
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password")

    if not username or not email or not password:
        return (
            jsonify({"message": "username, email, and password are required"}),
            400,
        )

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"message": "Username or email already taken"}), 409

    password_hash = generate_password_hash(password)
    user = User(username=username, email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id

    return jsonify({"id": user.id, "username": user.username, "email": user.email}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip()
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    session["user_id"] = user.id
    return jsonify({"message": "Logged in", "user_id": user.id}), 200


@auth_bp.route("/logout", methods=["GET"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out"}), 200
