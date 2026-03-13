"""Run entrypoint for the blog_app package.

This file allows starting the app from inside the `blog_app/` folder.

Usage:
    cd blog_app
    python run.py
"""

import os
import sys

# Ensure the project root is on sys.path so `import blog_app` works
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from blog_app.app import create_app
app = create_app()



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
