from flask import Blueprint, jsonify, request

from blog_app.models import Notification
from blog_app.database import db

notification_bp = Blueprint("notifications", __name__)


@notification_bp.route("/", methods=["GET"])
def get_notifications():
    recipient_id = request.args.get("recipient_id")
    notifications = Notification.query.filter_by(recipient_id=recipient_id).order_by(
        Notification.created_at.desc()
    )
    return jsonify(
        [
            {
                "id": n.id,
                "message": n.message,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
            }
            for n in notifications
        ]
    )


@notification_bp.route("/", methods=["POST"])
def create_notification():
    data = request.get_json(force=True)
    notification = Notification(
        recipient_id=data.get("recipient_id"),
        message=data.get("message"),
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({"id": notification.id}), 201
