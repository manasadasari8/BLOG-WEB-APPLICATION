from flask import Blueprint, jsonify, request, session
from sqlalchemy.orm import joinedload

from blog_app.database import db
from blog_app.models import Comment, Like, Post
from blog_app.routes.auth_routes import login_required

post_bp = Blueprint("posts", __name__)


def _profile_image_url(profile_image: str | None) -> str:
    if profile_image:
        return f"/static/uploads/profile_images/{profile_image}"
    return "/static/images/default-avatar.png"


def _comment_to_dict(comment: Comment) -> dict:
    return {
        "id": comment.id,
        "text": comment.comment_text,
        "created_at": comment.created_at.isoformat(),
        "author": {
            "id": comment.author.id,
            "username": comment.author.username,
            "profile_pic": _profile_image_url(comment.author.profile_image),
        },
    }


def _post_to_dict(post: Post, current_user_id: int | None = None) -> dict:
    liked_by_me = False
    if current_user_id:
        liked_by_me = any(like.user_id == current_user_id for like in post.likes)

    return {
        "id": post.id,
        "content": post.content,
        "image_url": post.image_url,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat() if post.updated_at else None,
        "author": {
            "id": post.author.id,
            "username": post.author.username,
            "profile_pic": _profile_image_url(post.author.profile_image),
        },
        "likes_count": len(post.likes),
        "comments_count": len(post.comments),
        "liked_by_me": liked_by_me,
        "comments": [_comment_to_dict(c) for c in post.comments],
    }


@post_bp.route("/", methods=["GET"])
def list_posts():
    sort_by = request.args.get("sort", "newest")
    current_user_id = session.get("user_id")

    query = Post.query.options(
        joinedload(Post.author),
        joinedload(Post.likes),
        joinedload(Post.comments).joinedload(Comment.author),
    )

    if sort_by == "most_popular":
        # Order by likes count descending, then by created_at descending
        query = query.outerjoin(Like).group_by(Post.id).order_by(
            db.func.count(Like.id).desc(), Post.created_at.desc()
        )
    else:  # newest
        query = query.order_by(Post.created_at.desc())

    posts = query.all()
    return jsonify([_post_to_dict(p, current_user_id) for p in posts])


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
