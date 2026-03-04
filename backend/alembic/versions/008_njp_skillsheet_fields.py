"""008: NJP職務経歴書フィールド追加

- employee_projects: process_phases (JSON), lessons_learned (TEXT) を追加
- employees: self_pr (TEXT) を追加

Revision ID: 008
Revises: 007
Create Date: 2026-03-04
"""
from alembic import op
import sqlalchemy as sa

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("employee_projects", sa.Column("process_phases", sa.JSON, nullable=True))
    op.add_column("employee_projects", sa.Column("lessons_learned", sa.Text, nullable=True))
    op.add_column("employees", sa.Column("self_pr", sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column("employee_projects", "process_phases")
    op.drop_column("employee_projects", "lessons_learned")
    op.drop_column("employees", "self_pr")
