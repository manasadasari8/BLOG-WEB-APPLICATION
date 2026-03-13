from flask_sqlalchemy import SQLAlchemy

# The SQLAlchemy instance used throughout the app.
# The actual database URL is configured in app.py via Flask config.
db = SQLAlchemy()
