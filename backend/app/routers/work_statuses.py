"""
稼働状況・アサイン管理ルーター

- GET  /employees/{employee_id}/work-status
- PATCH /employees/{employee_id}/work-status
- GET  /employees/{employee_id}/assignments
- POST /employees/{employee_id}/assignments
- PATCH /assignments/{assignment_id}
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_employee, require_role
from app.models.employee import Employee
from app.models.work_status import WorkStatus, Assignment
from app.models.project import Project
from app.schemas.work_status import (
    WorkStatusResponse,
    WorkStatusUpdate,
    AssignmentCreate,
    AssignmentResponse,
    AssignmentUpdate,
)
from app.services.work_status_service import (
    get_or_create_work_status,
    update_work_status,
    list_assignments,
    create_assignment,
    update_assignment,
)

router = APIRouter()


@router.get("/employees/{employee_id}/work-status", response_model=WorkStatusResponse)
async def get_work_status(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(get_current_employee),
):
    """稼働状況を取得する。存在しない場合は FREE_IMMEDIATE を返す。"""
    ws = await get_or_create_work_status(db, employee_id)
    return ws


@router.patch("/employees/{employee_id}/work-status", response_model=WorkStatusResponse)
async def patch_work_status(
    employee_id: str,
    data: WorkStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_employee: Employee = Depends(require_role("manager", "department_head", "admin")),
):
    """稼働状況を更新する。権限: manager / department_head / admin"""
    ws = await update_work_status(db, employee_id, data, updater_id=current_employee.id)
    return ws


@router.get("/employees/{employee_id}/assignments", response_model=list[AssignmentResponse])
async def get_assignments(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(get_current_employee),
):
    """社員のアサイン一覧を取得する。"""
    assignments = await list_assignments(db, employee_id)
    result = []
    for a in assignments:
        proj = await db.get(Project, a.project_id)
        result.append(AssignmentResponse(
            id=a.id,
            employee_id=a.employee_id,
            project_id=a.project_id,
            project_name=proj.name if proj else None,
            allocation_percent=a.allocation_percent,
            started_at=a.started_at,
            ends_at=a.ends_at,
            is_active=a.is_active,
            created_at=a.created_at,
        ))
    return result


@router.post("/employees/{employee_id}/assignments", response_model=AssignmentResponse, status_code=201)
async def post_assignment(
    employee_id: str,
    data: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_employee: Employee = Depends(require_role("manager", "department_head", "admin")),
):
    """アサインを登録する。権限: manager / department_head / admin"""
    assignment = await create_assignment(db, employee_id, data, creator_id=current_employee.id)
    proj = await db.get(Project, assignment.project_id)
    return AssignmentResponse(
        id=assignment.id,
        employee_id=assignment.employee_id,
        project_id=assignment.project_id,
        project_name=proj.name if proj else None,
        allocation_percent=assignment.allocation_percent,
        started_at=assignment.started_at,
        ends_at=assignment.ends_at,
        is_active=assignment.is_active,
        created_at=assignment.created_at,
    )


@router.patch("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def patch_assignment(
    assignment_id: str,
    data: AssignmentUpdate,
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(require_role("manager", "department_head", "admin")),
):
    """アサイン情報を更新する。権限: manager / department_head / admin"""
    assignment = await update_assignment(db, assignment_id, data)
    proj = await db.get(Project, assignment.project_id)
    return AssignmentResponse(
        id=assignment.id,
        employee_id=assignment.employee_id,
        project_id=assignment.project_id,
        project_name=proj.name if proj else None,
        allocation_percent=assignment.allocation_percent,
        started_at=assignment.started_at,
        ends_at=assignment.ends_at,
        is_active=assignment.is_active,
        created_at=assignment.created_at,
    )
