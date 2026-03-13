from flask import Blueprint, jsonify, request, session

from blog_app.database import db
from blog_app.models import Like, Notification, Post
from blog_app.routes.auth_routes import login_required

like_bp = Blueprint("likes", __name__)


@like_bp.route("/", methods=["POST"])
@login_required
def like_post():
    user_id = session.get("user_id")
    data = request.get_json(force=True)
    post_id = data.get("post_id")

    if not post_id:
        return jsonify({"message": "post_id is required"}), 400

    like = Like(user_id=user_id, post_id=post_id)
    db.session.add(like)
    db.session.commit()

    # Create notification for post owner
    post = Post.query.get(post_id)
    if post and post.user_id != user_id:
        notification = Notification(
            user_id=post.user_id,
            actor_id=user_id,
            post_id=post_id,
            type="like",
        )
        db.session.add(notification)
        db.session.commit()

    return jsonify({"id": like.id}), 201
