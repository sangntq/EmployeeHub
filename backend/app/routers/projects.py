"""
プロジェクト経歴・ビザ情報ルーター

- GET    /employees/{employee_id}/projects
- POST   /employees/{employee_id}/projects
- PUT    /employee-projects/{project_id}
- DELETE /employee-projects/{project_id}
- PATCH  /employees/{employee_id}/projects/reorder
- GET    /employees/{employee_id}/visa
- PUT    /employees/{employee_id}/visa
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_employee, require_role
from app.models.employee import Employee
from app.schemas.project import (
    EmployeeProjectCreate,
    EmployeeProjectUpdate,
    EmployeeProjectResponse,
    ProjectReorderRequest,
    VisaInfoResponse,
    VisaInfoUpdate,
)
from app.services.project_service import (
    list_employee_projects,
    add_employee_project,
    update_employee_project,
    delete_employee_project,
    reorder_employee_projects,
    get_visa_info,
    upsert_visa_info,
)

router = APIRouter()


@router.get("/employees/{employee_id}/projects", response_model=list[EmployeeProjectResponse])
async def get_employee_projects(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(get_current_employee),
):
    """プロジェクト経歴一覧を取得する（sort_order 順）。"""
    projects = await list_employee_projects(db, employee_id)
    return projects


@router.post("/employees/{employee_id}/projects", response_model=EmployeeProjectResponse, status_code=201)
async def post_employee_project(
    employee_id: str,
    data: EmployeeProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    """プロジェクト経歴を追加する。権限: 本人 / manager / admin"""
    if current_employee.id != employee_id and current_employee.system_role not in ("manager", "department_head", "admin"):
        raise HTTPException(status_code=403, detail="権限が不足しています")
    emp_project = await add_employee_project(db, employee_id, data, creator_id=current_employee.id)
    return emp_project


@router.put("/employee-projects/{project_id}", response_model=EmployeeProjectResponse)
async def put_employee_project(
    project_id: str,
    data: EmployeeProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    """プロジェクト経歴を更新する。権限: 本人 / manager / admin"""
    from app.models.project import EmployeeProject
    emp_proj = await db.get(EmployeeProject, project_id)
    if emp_proj is None:
        raise HTTPException(status_code=404, detail="Project record not found")
    if current_employee.id != emp_proj.employee_id and current_employee.system_role not in ("manager", "department_head", "admin"):
        raise HTTPException(status_code=403, detail="権限が不足しています")
    return await update_employee_project(db, project_id, data, employee_id=emp_proj.employee_id)


@router.delete("/employee-projects/{project_id}", status_code=204)
async def delete_emp_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    """プロジェクト経歴を削除する。権限: 本人 / manager / admin"""
    from app.models.project import EmployeeProject
    emp_proj = await db.get(EmployeeProject, project_id)
    if emp_proj is None:
        raise HTTPException(status_code=404, detail="Project record not found")
    if current_employee.id != emp_proj.employee_id and current_employee.system_role not in ("manager", "department_head", "admin"):
        raise HTTPException(status_code=403, detail="権限が不足しています")
    await delete_employee_project(db, project_id, employee_id=emp_proj.employee_id)


@router.patch("/employees/{employee_id}/projects/reorder", response_model=list[EmployeeProjectResponse])
async def reorder_projects(
    employee_id: str,
    data: ProjectReorderRequest,
    db: AsyncSession = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    """プロジェクト経歴の表示順を変更する。"""
    if current_employee.id != employee_id and current_employee.system_role not in ("manager", "department_head", "admin"):
        raise HTTPException(status_code=403, detail="権限が不足しています")
    return await reorder_employee_projects(db, employee_id, data.ordered_ids)


@router.get("/employees/{employee_id}/visa", response_model=VisaInfoResponse | None)
async def get_visa(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    """ビザ情報を取得する。権限: 本人 / department_head / admin"""
    if (
        current_employee.id != employee_id
        and current_employee.system_role not in ("department_head", "director", "admin")
    ):
        raise HTTPException(status_code=403, detail="権限が不足しています")
    return await get_visa_info(db, employee_id)


@router.put("/employees/{employee_id}/visa", response_model=VisaInfoResponse)
async def put_visa(
    employee_id: str,
    data: VisaInfoUpdate,
    db: AsyncSession = Depends(get_db),
    current_employee: Employee = Depends(require_role("department_head", "director", "admin")),
):
    """ビザ情報を更新する（upsert）。権限: department_head / admin"""
    return await upsert_visa_info(db, employee_id, data, updater_id=current_employee.id)
