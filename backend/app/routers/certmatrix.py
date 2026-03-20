"""資格マトリクスルーター

エンドポイント:
  GET /certifications/matrix   資格マトリクス取得
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.models.employee import Employee
from app.schemas.certmatrix import CertMatrixResponse
from app.services import certmatrix_service

router = APIRouter()

# アクセス可能なロール
MATRIX_ROLES = ("manager", "department_head", "director", "admin")


@router.get("/certifications/matrix", response_model=CertMatrixResponse)
async def get_cert_matrix(
    location: str | None = Query(None, description="オフィス拠点フィルター"),
    category: str | None = Query(None, description="資格カテゴリフィルター"),
    free_only: bool = Query(False, description="空きエンジニアのみ"),
    search: str | None = Query(None, description="社員名・番号の検索"),
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(require_role(*MATRIX_ROLES)),
):
    """資格マトリクスを返す。manager / department_head / director / admin が利用可能。"""
    return await certmatrix_service.get_cert_matrix(
        db=db,
        location=location,
        category=category,
        free_only=free_only,
        search=search,
    )
