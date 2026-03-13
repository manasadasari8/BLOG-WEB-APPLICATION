import os
from functools import wraps

from flask import Blueprint, jsonify, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from blog_app.database import db
from blog_app.models import Like, Post, User


auth_bp = Blueprint("auth", __name__)


def _profile_image_url(profile_image: str | None) -> str:
    if profile_image:
        return url_for("static", filename=f"uploads/profile_images/{profile_image}")
    return url_for("static", filename="images/default-avatar.png")


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

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "profile_pic": _profile_image_url(user.profile_image),
    }), 201


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


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    user_posts = Post.query.filter_by(user_id=user.id).all()
    total_likes = sum(len(p.likes) for p in user_posts)

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "bio": user.bio,
        "profile_pic":  _profile_image_url(user.profile_image),
        "post_count": len(user_posts),
        "likes_count": total_likes,
    }), 200

@auth_bp.route("/upload-profile-image", methods=["POST"])
@login_required
def upload_profile_image():
    if "profile_image" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["profile_image"]
    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    filename = secure_filename(file.filename)
    if not filename:
        return jsonify({"message": "Invalid filename"}), 400

    user_id = session.get("user_id")
    user = User.query.get(user_id)

    upload_folder = "uploads/profile_images"
    file_path = f"{upload_folder}/{filename}"

    # Save file to static folder
    full_path = os.path.join(os.path.dirname(__file__), "..", "static", file_path)
    full_path = os.path.abspath(full_path)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    file.save(full_path)

    user.profile_image = filename
    db.session.commit()

    return jsonify({
        "message": "Uploaded",
        "profile_pic": _profile_image_url(user.profile_image),
    }), 201

@auth_bp.route("/logout", methods=["GET"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out"}), 200


@auth_bp.route("/users/<string:username>", methods=["GET"])
def get_user(username: str):
    user = User.query.filter_by(username=username).first_or_404()
    user_posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    total_likes = sum(len(p.likes) for p in user_posts)

    posts_data = [
        {
            "id": p.id,
            "content": p.content,
            "image_url": p.image_url,
            "created_at": p.created_at.isoformat(),
            "likes_count": len(p.likes),
            "comments_count": len(p.comments),
        }
        for p in user_posts
    ]

    return jsonify({
        "id": user.id,
        "username": user.username,
        "bio": user.bio,
        "profile_pic": _profile_pic_for_username(user.username),
        "post_count": len(user_posts),
        "likes_count": total_likes,
        "posts": posts_data,
    }), 200
