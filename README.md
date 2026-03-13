# Blog Web Application (Flask + PostgreSQL)

## Setup

1. Create a Python virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure your PostgreSQL connection string:

```bash
export DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/blogdb"
# Windows PowerShell:
# $env:DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/blogdb"
```

3. Run the app:

```bash
python -m blog_app.app
```

## Project structure

- `blog_app/app.py`: Flask app factory and blueprint registration
- `blog_app/database.py`: SQLAlchemy initialization
- `blog_app/models.py`: SQLAlchemy ORM models
- `blog_app/routes/`: API routes for auth, posts, comments, likes, notifications
- `templates/` and `static/`: frontend assets
