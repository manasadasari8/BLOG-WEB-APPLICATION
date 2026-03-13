"""Run entrypoint for the blog_app package.

This file allows starting the app from the repository root without requiring
"python -m blog_app.app" to be executed from the parent folder.
"""

from blog_app.app import create_app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
