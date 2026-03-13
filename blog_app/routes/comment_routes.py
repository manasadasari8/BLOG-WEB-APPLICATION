from flask import Blueprint, jsonify, request, session

from blog_app.database import db
from blog_app.models import Comment
from blog_app.routes.auth_routes import login_required

comment_bp = Blueprint("comments", __name__)


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

    return jsonify({"id": comment.id}), 201
