"""稼働可否スケジュールルーター

エンドポイント:
  GET /availability   稼働可否カレンダー取得
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.models.employee import Employee
from app.schemas.availability import AvailabilityResponse
from app.services import availability_service

router = APIRouter()

# アクセス可能なロール
AVAILABILITY_ROLES = ("sales", "manager", "department_head", "director", "admin")


@router.get("/availability", response_model=AvailabilityResponse)
async def get_availability(
    months: int = Query(6, ge=1, le=24, description="表示月数"),
    offset_months: int = Query(0, ge=-12, le=12, description="今月からのオフセット月数"),
    location: str | None = Query(None, description="オフィス拠点フィルター"),
    search: str | None = Query(None, description="社員名・番号の検索"),
    status: str | None = Query(None, description="FREE | PARTIAL | BUSY"),
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(require_role(*AVAILABILITY_ROLES)),
):
    """稼働可否カレンダーを返す。sales / manager / department_head / director / admin が利用可能。"""
    return await availability_service.get_availability(
        db=db,
        months=months,
        offset_months=offset_months,
        location=location,
        search=search,
        status_filter=status,
    )
