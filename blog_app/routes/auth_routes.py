from flask import Blueprint, jsonify, request

from blog_app.models import User
from blog_app.database import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # TODO: Add password hashing
    user = User(username=username, email=email, password_hash=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"id": user.id, "username": user.username, "email": user.email}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or user.password_hash != password:
        return jsonify({"message": "Invalid credentials"}), 401

    return jsonify({"message": "Logged in", "user_id": user.id}), 200
