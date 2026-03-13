from flask import Blueprint, jsonify, request, session

from blog_app.database import db
from blog_app.models import Notification
from blog_app.routes.auth_routes import login_required

notification_bp = Blueprint("notifications", __name__)


@notification_bp.route("/", methods=["GET"])
@login_required
def get_notifications():
    user_id = session.get("user_id")
    notifications = Notification.query.filter_by(user_id=user_id).order_by(
        Notification.created_at.desc()
    ).all()

    result = []
    for n in notifications:
        message = ""
        if n.type == "like":
            message = f"{n.actor.username} liked your post"
        elif n.type == "comment":
            message = f"{n.actor.username} commented on your post"
        else:
            message = f"New notification from {n.actor.username}"

        result.append({
            "id": n.id,
            "type": n.type,
            "message": message,
            "actor": {"id": n.actor.id, "username": n.actor.username},
            "post_id": n.post_id,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
        })

    return jsonify(result)


@notification_bp.route("/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_as_read(notification_id: int):
    user_id = session.get("user_id")
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first_or_404()

    notification.is_read = True
    db.session.commit()

    return jsonify({"message": "Marked as read"}), 200
