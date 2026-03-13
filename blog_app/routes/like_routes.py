from flask import Blueprint, jsonify, request

from blog_app.models import Like
from blog_app.database import db

like_bp = Blueprint("likes", __name__)


@like_bp.route("/", methods=["POST"])
def like_post():
    data = request.get_json(force=True)
    like = Like(
        user_id=data.get("user_id"),
        post_id=data.get("post_id"),
    )
    db.session.add(like)
    db.session.commit()

    return jsonify({"id": like.id}), 201
