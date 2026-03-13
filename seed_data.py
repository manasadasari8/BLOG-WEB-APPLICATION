"""Seed script for the blog web application.

Run:
    python seed_data.py

This script inserts demo users, posts, likes, and comments into the configured PostgreSQL database.
"""

import random

from werkzeug.security import generate_password_hash

from blog_app.app import create_app
from blog_app.database import db
from blog_app.models import Comment, Like, Post, User


def seed():
    app = create_app()

    with app.app_context():
        # Clear existing data so this can be re-run safely.
        # NOTE: In a production system you would not do this.
        try:
            db.session.execute("TRUNCATE TABLE likes, comments, posts, users RESTART IDENTITY CASCADE;")
            db.session.commit()
        except Exception:
            # Fallback: delete via ORM if TRUNCATE is not supported.
            Comment.query.delete()
            Like.query.delete()
            Post.query.delete()
            User.query.delete()
            db.session.commit()

        users_data = [
            {
                "username": "alex_dev",
                "email": "alex@example.com",
                "bio": "Full-stack developer building user-friendly web apps.",
                "profile_pic": "https://i.pravatar.cc/150?img=5",
            },
            {
                "username": "sarah_writer",
                "email": "sarah@example.com",
                "bio": "Writer exploring tech, culture, and product design.",
                "profile_pic": "https://i.pravatar.cc/150?img=10",
            },
            {
                "username": "tech_guru",
                "email": "guru@example.com",
                "bio": "Sharing tips and tricks from the world of software engineering.",
                "profile_pic": "https://i.pravatar.cc/150?img=12",
            },
            {
                "username": "daily_coder",
                "email": "daily@example.com",
                "bio": "Coding every day and learning something new.",
                "profile_pic": "https://i.pravatar.cc/150?img=20",
            },
            {
                "username": "travel_blog",
                "email": "travel@example.com",
                "bio": "Adventures, coffee shops, and remote work in new cities.",
                "profile_pic": "https://i.pravatar.cc/150?img=25",
            },
        ]

        users = []
        for u in users_data:
            user = User(
                username=u["username"],
                email=u["email"],
                password_hash=generate_password_hash("password123"),
                bio=f"{u['bio']}\nProfile picture: {u['profile_pic']}",
            )
            users.append(user)
            db.session.add(user)

        db.session.commit()

        post_texts = [
            "Just finished building my Flask blog platform!",
            "Learning Python and backend development today.",
            "Sharing my favorite productivity tips.",
            "Debugged a tricky SQLAlchemy issue — feels great!",
            "Working on a responsive UI for my web app.",
            "Writing about developer workflows and best practices.",
            "Refactoring code is my new favorite hobby.",
            "Deploying a Flask app to Heroku was way easier than expected.",
            "Looking for advice on API design and versioning.",
            "Exploring the latest Python 3.12 features today.",
        ]

        posts = []
        for idx, text in enumerate(post_texts):
            author = random.choice(users)
            post = Post(
                user_id=author.id,
                content=text,
                image_url=("https://picsum.photos/seed/" + str(idx) + "/600/300"),
            )
            posts.append(post)
            db.session.add(post)

        db.session.commit()

        # Add random likes
        for post in posts:
            like_count = random.randint(1, 5)
            likers = random.sample([u for u in users if u.id != post.user_id], k=min(like_count, len(users) - 1))
            for liker in likers:
                like = Like(user_id=liker.id, post_id=post.id)
                db.session.add(like)

        db.session.commit()

        # Add random comments
        comment_templates = [
            "Awesome work!",
            "This is so helpful, thanks for sharing.",
            "Love this! Keep it up.",
            "Great explanation — I learned a lot.",
            "Can you share more details about your setup?",
        ]

        for post in posts:
            comment_count = random.randint(1, 4)
            commenters = random.choices([u for u in users if u.id != post.user_id], k=comment_count)
            for commenter in commenters:
                comment = Comment(
                    user_id=commenter.id,
                    post_id=post.id,
                    comment_text=random.choice(comment_templates),
                )
                db.session.add(comment)

        db.session.commit()

        print("✅ Seed data inserted successfully!")


if __name__ == "__main__":
    seed()
