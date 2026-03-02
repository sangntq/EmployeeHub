"""
通知スキーマ
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    body: str | None
    is_read: bool
    related_entity_type: str | None
    related_entity_id: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    unread_count: int
    page: int
    per_page: int
