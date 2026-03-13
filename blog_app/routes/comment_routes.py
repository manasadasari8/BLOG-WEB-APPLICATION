from flask import Blueprint, jsonify, request, session, url_for

from blog_app.database import db
from blog_app.models import Comment, Notification, Post
from blog_app.routes.auth_routes import login_required

comment_bp = Blueprint("comments", __name__)


def _profile_image_url(profile_image: str | None) -> str:
    if profile_image:
        return url_for("static", filename=f"uploads/profile_images/{profile_image}")
    return url_for("static", filename="images/default-avatar.png")


@comment_bp.route("/", methods=["GET"])
def list_comments():
    post_id = request.args.get("post_id")
    if not post_id:
        return jsonify({"message": "post_id is required"}), 400

    comments = (
        Comment.query.filter_by(post_id=post_id)
        .order_by(Comment.created_at.asc())
        .all()
    )

    return jsonify(
        [
            {
                "id": c.id,
                "text": c.comment_text,
                "created_at": c.created_at.isoformat(),
                "author": {
                    "id": c.author.id,
                    "username": c.author.username,
                    "profile_pic": _profile_image_url(c.author.profile_image),
                },
            }
            for c in comments
        ]
    )


@comment_bp.route("/", methods=["POST"])
@login_required
def create_comment():
    user_id = session.get("user_id")
    data = request.get_json(force=True)
    post_id = data.get("post_id")
    comment_text = (data.get("comment_text") or data.get("body") or "").strip()

    if not post_id or not comment_text:
        return jsonify({"message": "post_id and comment_text are required"}), 400

    comment = Comment(user_id=user_id, post_id=post_id, comment_text=comment_text)
    db.session.add(comment)
    db.session.commit()

    # Create notification for post owner
    post = Post.query.get(post_id)
    if post and post.user_id != user_id:
        notification = Notification(
            user_id=post.user_id,
            actor_id=user_id,
            post_id=post_id,
            type="comment",
        )
        db.session.add(notification)
        db.session.commit()

    return jsonify({"id": comment.id}), 201
