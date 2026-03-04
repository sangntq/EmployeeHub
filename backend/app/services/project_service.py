"""
プロジェクト経歴・ビザ情報管理サービス
"""
import uuid
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.project import Project, EmployeeProject, VisaInfo
from app.schemas.project import EmployeeProjectCreate, EmployeeProjectUpdate, VisaInfoUpdate


async def list_employee_projects(db: AsyncSession, employee_id: str) -> list[EmployeeProject]:
    """プロジェクト経歴一覧（sort_order 昇順）。"""
    result = await db.execute(
        select(EmployeeProject)
        .where(EmployeeProject.employee_id == employee_id)
        .order_by(EmployeeProject.sort_order, EmployeeProject.started_at.desc())
    )
    return list(result.scalars().all())


async def add_employee_project(
    db: AsyncSession,
    employee_id: str,
    data: EmployeeProjectCreate,
    creator_id: str,
) -> EmployeeProject:
    """プロジェクト経歴を追加する。プロジェクトマスタに自動作成する。"""
    project = Project(
        id=str(uuid.uuid4()),
        name=data.project_name,
        client_name=data.client_name,
        industry=data.industry,
        started_at=data.started_at,
        ended_at=data.ended_at,
        created_by=creator_id,
        created_at=datetime.now(UTC),
    )
    db.add(project)
    await db.flush()

    result = await db.execute(
        select(EmployeeProject.sort_order)
        .where(EmployeeProject.employee_id == employee_id)
        .order_by(EmployeeProject.sort_order.desc())
        .limit(1)
    )
    max_order = result.scalar_one_or_none() or -1

    emp_project = EmployeeProject(
        id=str(uuid.uuid4()),
        employee_id=employee_id,
        project_id=project.id,
        role=data.role,
        started_at=data.started_at,
        ended_at=data.ended_at,
        tech_stack=data.tech_stack,
        team_size=data.team_size,
        responsibilities=data.responsibilities,
        achievements=data.achievements,
        process_phases=data.process_phases,
        lessons_learned=data.lessons_learned,
        sort_order=max_order + 1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(emp_project)
    await db.commit()
    await db.refresh(emp_project)
    return emp_project


async def update_employee_project(
    db: AsyncSession,
    project_id: str,
    data: EmployeeProjectUpdate,
    employee_id: str,
) -> EmployeeProject:
    """プロジェクト経歴を更新する。"""
    emp_proj = await db.get(EmployeeProject, project_id)
    if emp_proj is None or emp_proj.employee_id != employee_id:
        raise HTTPException(status_code=404, detail="Project record not found")

    proj = await db.get(Project, emp_proj.project_id)
    if proj and data.project_name is not None:
        proj.name = data.project_name
    if proj and data.client_name is not None:
        proj.client_name = data.client_name
    if proj and data.industry is not None:
        proj.industry = data.industry

    if data.role is not None:
        emp_proj.role = data.role
    if data.started_at is not None:
        emp_proj.started_at = data.started_at
    if data.ended_at is not None:
        emp_proj.ended_at = data.ended_at
    if data.tech_stack is not None:
        emp_proj.tech_stack = data.tech_stack
    if data.team_size is not None:
        emp_proj.team_size = data.team_size
    if data.responsibilities is not None:
        emp_proj.responsibilities = data.responsibilities
    if data.achievements is not None:
        emp_proj.achievements = data.achievements
    if data.process_phases is not None:
        emp_proj.process_phases = data.process_phases
    if data.lessons_learned is not None:
        emp_proj.lessons_learned = data.lessons_learned
    emp_proj.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(emp_proj)
    return emp_proj


async def delete_employee_project(
    db: AsyncSession,
    project_id: str,
    employee_id: str,
) -> None:
    """プロジェクト経歴を削除する。"""
    emp_proj = await db.get(EmployeeProject, project_id)
    if emp_proj is None or emp_proj.employee_id != employee_id:
        raise HTTPException(status_code=404, detail="Project record not found")
    await db.delete(emp_proj)
    await db.commit()


async def reorder_employee_projects(
    db: AsyncSession,
    employee_id: str,
    ordered_ids: list[str],
) -> list[EmployeeProject]:
    """プロジェクト経歴の表示順を変更する。"""
    for i, proj_id in enumerate(ordered_ids):
        emp_proj = await db.get(EmployeeProject, proj_id)
        if emp_proj and emp_proj.employee_id == employee_id:
            emp_proj.sort_order = i
    await db.commit()
    return await list_employee_projects(db, employee_id)


async def get_visa_info(db: AsyncSession, employee_id: str) -> VisaInfo | None:
    """ビザ情報を取得する。"""
    result = await db.execute(
        select(VisaInfo).where(VisaInfo.employee_id == employee_id)
    )
    return result.scalar_one_or_none()


async def upsert_visa_info(
    db: AsyncSession,
    employee_id: str,
    data: VisaInfoUpdate,
    updater_id: str,
) -> VisaInfo:
    """ビザ情報を作成または更新する。"""
    result = await db.execute(
        select(VisaInfo).where(VisaInfo.employee_id == employee_id)
    )
    visa = result.scalar_one_or_none()
    now = datetime.now(UTC)

    if visa is None:
        visa = VisaInfo(
            id=str(uuid.uuid4()),
            employee_id=employee_id,
            visa_type=data.visa_type,
            residence_card_number=data.residence_card_number,
            expires_at=data.expires_at,
            notes=data.notes,
            updated_by=updater_id,
            updated_at=now,
        )
        db.add(visa)
    else:
        if data.visa_type is not None:
            visa.visa_type = data.visa_type
        if data.residence_card_number is not None:
            visa.residence_card_number = data.residence_card_number
        if data.expires_at is not None:
            visa.expires_at = data.expires_at
        if data.notes is not None:
            visa.notes = data.notes
        visa.updated_by = updater_id
        visa.updated_at = now

    await db.commit()
    await db.refresh(visa)
    return visa
