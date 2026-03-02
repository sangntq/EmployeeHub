"""Phase 4: japanese_level列追加 + search_logs テーブル

Revision ID: 004
Revises: 003
Create Date: 2026-03-01
"""
from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime, UTC

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # employees テーブルに日本語レベル列を追加
    op.add_column(
        "employees",
        sa.Column("japanese_level", sa.String(10), nullable=True),
    )

    # search_logs テーブル（検索ログ + 保存済み検索を兼用）
    op.create_table(
        "search_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("searcher_id", sa.String(36), sa.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_ai_search", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("raw_input", sa.Text, nullable=True),
        sa.Column("criteria", sa.JSON, nullable=True),
        sa.Column("result_count", sa.Integer, nullable=True),
        sa.Column("saved_name", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_search_logs_searcher", "search_logs", ["searcher_id"])
    op.create_index("idx_search_logs_created", "search_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_search_logs_created", table_name="search_logs")
    op.drop_index("idx_search_logs_searcher", table_name="search_logs")
    op.drop_table("search_logs")
    op.drop_column("employees", "japanese_level")
