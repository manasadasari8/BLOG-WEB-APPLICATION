from flask import Blueprint, jsonify, request, session

from blog_app.database import db
from blog_app.models import Post
from blog_app.routes.auth_routes import login_required

post_bp = Blueprint("posts", __name__)


def _post_to_dict(post: Post) -> dict:
    return {
        "id": post.id,
        "content": post.content,
        "image_url": post.image_url,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat() if post.updated_at else None,
        "author": {
            "id": post.author.id,
            "username": post.author.username,
        },
        "likes_count": len(post.likes),
        "comments_count": len(post.comments),
    }


@post_bp.route("/", methods=["GET"])
def list_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return jsonify([_post_to_dict(p) for p in posts])


@post_bp.route("/", methods=["POST"])
@login_required
def create_post():
    user_id = session.get("user_id")
    data = request.get_json(force=True)
    content = (data.get("content") or "").strip()
    image_url = data.get("image_url")

    if not content:
        return jsonify({"message": "content is required"}), 400

    post = Post(user_id=user_id, content=content, image_url=image_url)
    db.session.add(post)
    db.session.commit()

    return jsonify(_post_to_dict(post)), 201


@post_bp.route("/<int:post_id>", methods=["PUT"])
@login_required
def edit_post(post_id: int):
    user_id = session.get("user_id")
    post = Post.query.get_or_404(post_id)

    if post.user_id != user_id:
        return jsonify({"message": "Forbidden"}), 403

    data = request.get_json(force=True)
    content = data.get("content")
    if content is not None:
        post.content = content

    if "image_url" in data:
        post.image_url = data.get("image_url")

    db.session.commit()

    return jsonify(_post_to_dict(post)), 200


@post_bp.route("/<int:post_id>", methods=["DELETE"])
@login_required
def delete_post(post_id: int):
    user_id = session.get("user_id")
    post = Post.query.get_or_404(post_id)

    if post.user_id != user_id:
        return jsonify({"message": "Forbidden"}), 403

    db.session.delete(post)
    db.session.commit()

    return jsonify({"message": "Post deleted"}), 200
