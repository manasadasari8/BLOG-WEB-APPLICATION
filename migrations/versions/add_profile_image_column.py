"""Add profile_image column to users

Revision ID: add_profile_image_column
Revises: 0787d465459b
Create Date: 2026-03-13 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_profile_image_column'
down_revision = '0787d465459b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('profile_image', sa.String(length=1024), nullable=True))


def downgrade():
    op.drop_column('users', 'profile_image')
