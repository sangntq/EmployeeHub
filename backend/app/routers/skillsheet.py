"""
スキルシートエクスポート ルーター

POST /skillsheet/export  — 生成してダウンロードURLを返す
GET  /skillsheet/download/{token}  — ファイルを返す（認証不要）
"""
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_role
from app.schemas.skillsheet import ExportRequest, ExportResponse
from app.services.skillsheet_service import export_skillsheet, EXPORTS_DIR

router = APIRouter()

# スキルシート出力を許可するロール
SKILLSHEET_ROLES = ("sales", "manager", "department_head", "director", "admin")


@router.post("/export", response_model=ExportResponse)
async def export_endpoint(
    body: ExportRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_role(*SKILLSHEET_ROLES)),
):
    """スキルシートを生成し、ダウンロードURLを返す。"""
    result = await export_skillsheet(
        db=db,
        employee_ids=body.employee_ids,
        format=body.format,
        output_style=body.output_style,
        filename_prefix=body.filename_prefix,
        include_salary=body.include_salary,
    )
    return ExportResponse(**result)


@router.get("/download/{token}")
async def download_endpoint(token: str):
    """
    トークンに対応するエクスポートファイルを返す。
    認証不要（トークン自体が認可の役割を担う）。
    """
    # token 内の .. や / を拒否してパストラバーサルを防止
    if "/" in token or "\\" in token or ".." in token:
        raise HTTPException(status_code=400, detail="Invalid token")

    # 拡張子を自動検出
    for ext in ("xlsx", "pdf", "zip"):
        candidate = EXPORTS_DIR / f"{token}.{ext}"
        if candidate.exists():
            media_types = {
                "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "pdf": "application/pdf",
                "zip": "application/zip",
            }
            return FileResponse(
                path=str(candidate),
                media_type=media_types[ext],
                filename=f"skillsheet.{ext}",
            )

    raise HTTPException(status_code=404, detail="File not found or expired")
