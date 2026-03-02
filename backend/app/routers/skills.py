"""スキル関連ルーター

エンドポイント:
  GET  /skills                              スキルマスタ一覧（カテゴリ別）
  GET  /employees/{id}/skills              個人スキル一覧
  POST /employees/{id}/skills              スキル申請（本人のみ）
  PATCH /employee-skills/{id}/approve      承認（manager以上）
  PATCH /employee-skills/{id}/reject       差し戻し（manager以上）
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_employee, require_role
from app.models.employee import Employee
from app.schemas.skill import (
    SkillMasterListResponse,
    EmployeeSkillCreate,
    EmployeeSkillResponse,
    ApproveSkillRequest,
    RejectSkillRequest,
)
from app.services import skill_service

router = APIRouter()


@router.get("/skills", response_model=SkillMasterListResponse)
async def list_skills(
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(get_current_employee),
):
    """スキルマスタ一覧（カテゴリ別グループ化）。認証済みユーザー全員が閲覧可能。"""
    categories = await skill_service.get_skill_categories(db)
    return SkillMasterListResponse(categories=categories)


@router.get("/employees/{employee_id}/skills", response_model=list[EmployeeSkillResponse])
async def list_employee_skills(
    employee_id: str,
    status: str | None = Query(None, description="PENDING / APPROVED / REJECTED"),
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(get_current_employee),
):
    """個人スキル一覧。本人または manager 以上が閲覧可能。"""
    if current.system_role == "member" and current.id != employee_id:
        raise HTTPException(
            status_code=403, detail="他の社員のスキルは閲覧できません"
        )
    skills = await skill_service.get_employee_skills(db, employee_id, status)
    return [EmployeeSkillResponse.model_validate(s) for s in skills]


@router.post("/employees/{employee_id}/skills", response_model=EmployeeSkillResponse, status_code=201)
async def apply_skill(
    employee_id: str,
    body: EmployeeSkillCreate,
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(get_current_employee),
):
    """スキル申請。本人のみ。"""
    if current.id != employee_id:
        raise HTTPException(status_code=403, detail="自分のスキルのみ申請できます")
    emp_skill = await skill_service.apply_skill(db, employee_id, body, current)
    return EmployeeSkillResponse.model_validate(emp_skill)


@router.patch("/employee-skills/{skill_record_id}/approve", response_model=EmployeeSkillResponse)
async def approve_skill(
    skill_record_id: str,
    body: ApproveSkillRequest,
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(require_role("manager", "department_head", "admin")),
):
    """スキル承認。manager / department_head / admin のみ。"""
    emp_skill = await skill_service.approve_skill(db, skill_record_id, body, current)
    return EmployeeSkillResponse.model_validate(emp_skill)


@router.patch("/employee-skills/{skill_record_id}/reject", response_model=EmployeeSkillResponse)
async def reject_skill(
    skill_record_id: str,
    body: RejectSkillRequest,
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(require_role("manager", "department_head", "admin")),
):
    """スキル差し戻し。manager / department_head / admin のみ。"""
    emp_skill = await skill_service.reject_skill(db, skill_record_id, body, current)
    return EmployeeSkillResponse.model_validate(emp_skill)
