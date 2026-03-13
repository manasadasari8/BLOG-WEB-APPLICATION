from flask import Blueprint, jsonify, request

from blog_app.models import Comment
from blog_app.database import db

comment_bp = Blueprint("comments", __name__)


@comment_bp.route("/", methods=["POST"])
def create_comment():
    data = request.get_json(force=True)
    comment = Comment(
        body=data.get("body"),
        author_id=data.get("author_id"),
        post_id=data.get("post_id"),
    )
    db.session.add(comment)
    db.session.commit()

    return jsonify({"id": comment.id}), 201
