"""
検索ログモデル

SearchLog: 検索実行ログ（saved_name が NULL でないものが保存済み検索）
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class SearchLog(Base):
    __tablename__ = "search_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    searcher_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    is_ai_search: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    raw_input: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    result_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    saved_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    searcher: Mapped["Employee | None"] = relationship("Employee", foreign_keys=[searcher_id])  # type: ignore[name-defined]
