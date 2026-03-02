"""
通知ルーター

- GET  /notifications             自分宛の通知一覧
- PATCH /notifications/{id}/read  既読にする
- PATCH /notifications/read-all   全件既読にする
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_employee
from app.models.employee import Employee
from app.schemas.notification import NotificationListResponse
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    is_read: bool | None = Query(None, description="既読フィルタ（true/false/未指定=全件）"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(get_current_employee),
) -> NotificationListResponse:
    """自分宛の通知一覧を返す。"""
    return await notification_service.get_notifications(
        db, current.id, is_read=is_read, page=page, per_page=per_page
    )


@router.patch("/read-all", status_code=204)
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(get_current_employee),
) -> None:
    """全通知を既読にする。"""
    await notification_service.mark_all_read(db, current.id)


@router.patch("/{notification_id}/read", status_code=204)
async def mark_notification_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(get_current_employee),
) -> None:
    """指定の通知を既読にする。"""
    await notification_service.mark_as_read(db, notification_id, current.id)
