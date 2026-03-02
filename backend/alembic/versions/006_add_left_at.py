"""employees.left_at カラム追加

Revision ID: 006
Revises: 005
Create Date: 2026-03-02
"""
from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("employees", sa.Column("left_at", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("employees", "left_at")
