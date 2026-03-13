import os

from flask import Flask

from blog_app.database import db
from flask_migrate import Migrate  # type: ignore

from blog_app.routes.auth_routes import auth_bp
from blog_app.routes.post_routes import post_bp
from blog_app.routes.comment_routes import comment_bp
from blog_app.routes.like_routes import like_bp
from blog_app.routes.notification_routes import notification_bp


def create_app(config_override: dict | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Load configuration
    app.config.from_mapping(
        SECRET_KEY="change-me",
        SQLALCHEMY_DATABASE_URI=(
            # Use an environment variable first (e.g. DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/blogdb")
            # Fallback to a local development connection string.
            os.environ.get(
                "DATABASE_URL",
                "postgresql+psycopg2://user:password@localhost:5432/blogdb",
            )
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Allow runtime override for testing / development
    if config_override:
        app.config.update(config_override)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(post_bp, url_prefix="/posts")
    app.register_blueprint(comment_bp, url_prefix="/comments")
    app.register_blueprint(like_bp, url_prefix="/likes")
    app.register_blueprint(notification_bp, url_prefix="/notifications")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
