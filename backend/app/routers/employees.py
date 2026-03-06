import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_employee, require_role
from app.core.config import settings
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeDetail, EmployeeListItem, PaginatedEmployees
from app.services import employee_service

router = APIRouter()

UPLOAD_DIR = Path("/app/uploads/avatars")
ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB


@router.get("", response_model=PaginatedEmployees)
async def list_employees(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=1000),
    department_id: str | None = None,
    system_role: str | None = None,
    is_active: bool = True,
    q: str | None = None,
    keyword: str | None = None,
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(get_current_employee),
):
    # member ロールは社員一覧を閲覧不可
    if current.system_role == "member":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="この操作には manager 以上のロールが必要です")

    # keyword は q の別名（フロントエンド互換）
    search = keyword or q
    employees, total = await employee_service.list_employees(db, page, per_page, department_id, system_role, is_active, search)
    return PaginatedEmployees(
        items=[EmployeeListItem.model_validate(e) for e in employees],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.post("", response_model=EmployeeDetail, status_code=201)
async def create_employee(
    body: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(require_role("admin")),
):
    employee = await employee_service.create_employee(db, body)
    return EmployeeDetail.model_validate(employee)


@router.get("/{employee_id}", response_model=EmployeeDetail)
async def get_employee(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(get_current_employee),
):
    # member は自分のプロフィールのみ閲覧可
    if current.system_role == "member" and current.id != employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="他の社員のプロフィールは閲覧できません")

    employee = await employee_service.get_employee(db, employee_id)
    return EmployeeDetail.model_validate(employee)


@router.put("/{employee_id}", response_model=EmployeeDetail)
async def update_employee(
    employee_id: str,
    body: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(get_current_employee),
):
    # member は自分のプロフィールのみ更新可（ロール変更は不可）
    if current.system_role == "member":
        if current.id != employee_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="他の社員の情報は編集できません")
        body.system_role = None  # ロール変更を防止

    employee = await employee_service.update_employee(db, employee_id, body)
    return EmployeeDetail.model_validate(employee)


@router.delete("/{employee_id}", status_code=204)
async def delete_employee(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(require_role("admin")),
):
    """社員を無効化（論理削除）する。admin のみ実行可能。"""
    await employee_service.deactivate_employee(db, employee_id)


@router.post("/{employee_id}/avatar", response_model=EmployeeDetail)
async def upload_avatar(
    employee_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(get_current_employee),
):
    if current.system_role == "member" and current.id != employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="他の社員のアバターは変更できません")

    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="JPEG / PNG / WebP のみアップロード可能です")

    contents = await file.read()
    if len(contents) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ファイルサイズは 5MB 以下にしてください")

    # ローカルストレージに保存
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename or "avatar").suffix or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = UPLOAD_DIR / filename
    filepath.write_bytes(contents)
    avatar_url = f"/uploads/avatars/{filename}"

    employee = await employee_service.update_avatar(db, employee_id, avatar_url)
    return EmployeeDetail.model_validate(employee)
