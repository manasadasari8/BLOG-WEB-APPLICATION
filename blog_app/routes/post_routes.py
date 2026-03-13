from flask import Blueprint, jsonify, request

from blog_app.models import Post
from blog_app.database import db

post_bp = Blueprint("posts", __name__)


@post_bp.route("/", methods=["GET"])
def list_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return jsonify([
        {
            "id": p.id,
            "title": p.title,
            "body": p.body,
            "author_id": p.author_id,
            "created_at": p.created_at.isoformat(),
        }
        for p in posts
    ])


@post_bp.route("/", methods=["POST"])
def create_post():
    data = request.get_json(force=True)
    post = Post(
        title=data.get("title"),
        body=data.get("body"),
        author_id=data.get("author_id"),
    )
    db.session.add(post)
    db.session.commit()

    return jsonify({"id": post.id}), 201
