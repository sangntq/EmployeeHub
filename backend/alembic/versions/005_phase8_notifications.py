"""Phase 8: notifications テーブル作成

Revision ID: 005
Revises: 004
Create Date: 2026-03-02
"""
from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    notification_type_enum = sa.Enum(
        "VISA_EXPIRY",
        "CERT_EXPIRY",
        "SKILL_APPROVED",
        "SKILL_REJECTED",
        "CERT_APPROVED",
        "CERT_REJECTED",
        "ASSIGNMENT_ENDING",
        "PROFILE_STALE",
        "APPROVAL_REQUESTED",
        name="notification_type",
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "recipient_id",
            sa.String(36),
            sa.ForeignKey("employees.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", notification_type_enum, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("related_entity_type", sa.String(50), nullable=True),
        sa.Column("related_entity_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_notifications_recipient", "notifications", ["recipient_id", "is_read"])
    op.create_index("ix_notifications_created", "notifications", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_notifications_created", table_name="notifications")
    op.drop_index("ix_notifications_recipient", table_name="notifications")
    op.drop_table("notifications")
    sa.Enum(name="notification_type").drop(op.get_bind(), checkfirst=True)
