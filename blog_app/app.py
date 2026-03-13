import base64
import os

from flask import Flask, render_template, url_for

from blog_app.database import db
from flask_migrate import Migrate  # type: ignore

from blog_app.routes.auth_routes import auth_bp, login_required
from blog_app.routes.post_routes import post_bp
from blog_app.routes.comment_routes import comment_bp
from blog_app.routes.like_routes import like_bp
from blog_app.routes.notification_routes import notification_bp


def _ensure_default_avatar(static_folder: str) -> None:
    """Ensure the default avatar PNG exists."""
    default_dir = os.path.join(static_folder, "images")
    os.makedirs(default_dir, exist_ok=True)
    default_path = os.path.join(default_dir, "default-avatar.png")

    if os.path.exists(default_path):
        return

    # 1x1 transparent PNG
    png_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
    )
    with open(default_path, "wb") as f:
        f.write(base64.b64decode(png_base64))


def create_app(config_override: dict | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Ensure required static directories and default assets exist.
    uploads_dir = os.path.join(app.static_folder, "uploads", "profile_images")
    os.makedirs(uploads_dir, exist_ok=True)
    _ensure_default_avatar(app.static_folder)


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
                "postgresql+psycopg2://postgres:25032003@localhost:5432/blog_db",
            )
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Allow runtime override for testing / development
    if config_override:
        app.config.update(config_override)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)   
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(post_bp, url_prefix="/posts")
    app.register_blueprint(comment_bp, url_prefix="/comments")
    app.register_blueprint(like_bp, url_prefix="/likes")
    app.register_blueprint(notification_bp, url_prefix="/notifications")

    # Frontend routes
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/create")
    @login_required
    def create_page():
        return render_template("create.html")

    @app.route("/profile")
    @login_required
    def profile():
        return render_template("profile.html")

    @app.route("/profile/<username>")
    def profile_by_username(username: str):
        return render_template("profile.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
