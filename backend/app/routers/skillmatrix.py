"""スキルマトリクスルーター

エンドポイント:
  GET /skills/matrix   スキルマトリクス取得
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.models.employee import Employee
from app.schemas.skillmatrix import SkillMatrixResponse
from app.services import skillmatrix_service

router = APIRouter()

# アクセス可能なロール
MATRIX_ROLES = ("manager", "department_head", "director", "admin")


@router.get("/skills/matrix", response_model=SkillMatrixResponse)
async def get_skill_matrix(
    location: str | None = Query(None, description="オフィス拠点フィルター"),
    level_min: int | None = Query(None, ge=1, le=5, description="承認スキルレベルの下限"),
    category_id: str | None = Query(None, description="スキルカテゴリ ID フィルター"),
    free_only: bool = Query(False, description="空きエンジニアのみ"),
    search: str | None = Query(None, description="社員名・番号の検索"),
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(require_role(*MATRIX_ROLES)),
):
    """スキルマトリクスを返す。manager / department_head / director / admin が利用可能。"""
    return await skillmatrix_service.get_skill_matrix(
        db=db,
        location=location,
        level_min=level_min,
        category_id=category_id,
        free_only=free_only,
        search=search,
    )
