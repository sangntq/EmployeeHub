"""
稼働状況・アサイン管理サービス
"""
import uuid
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException

from app.models.work_status import WorkStatus, Assignment
from app.models.project import Project
from app.schemas.work_status import WorkStatusUpdate, AssignmentCreate, AssignmentUpdate


async def get_or_create_work_status(db: AsyncSession, employee_id: str) -> WorkStatus:
    """社員の稼働状況を取得する。存在しない場合は FREE_IMMEDIATE で作成する。"""
    result = await db.execute(
        select(WorkStatus).where(WorkStatus.employee_id == employee_id)
    )
    ws = result.scalar_one_or_none()
    if ws is None:
        ws = WorkStatus(
            id=str(uuid.uuid4()),
            employee_id=employee_id,
            status="FREE_IMMEDIATE",
            updated_at=datetime.now(UTC),
        )
        db.add(ws)
        await db.flush()
    return ws


async def update_work_status(
    db: AsyncSession,
    employee_id: str,
    data: WorkStatusUpdate,
    updater_id: str,
) -> WorkStatus:
    """稼働状況を更新する。"""
    ws = await get_or_create_work_status(db, employee_id)
    ws.status = data.status
    ws.free_from = data.free_from
    ws.note = data.note
    ws.updated_by = updater_id
    ws.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(ws)
    return ws


async def list_assignments(db: AsyncSession, employee_id: str) -> list[Assignment]:
    """社員のアサイン一覧を取得する（アクティブなもの優先）。"""
    result = await db.execute(
        select(Assignment)
        .where(Assignment.employee_id == employee_id)
        .order_by(Assignment.is_active.desc(), Assignment.started_at.desc())
    )
    return list(result.scalars().all())


async def create_assignment(
    db: AsyncSession,
    employee_id: str,
    data: AssignmentCreate,
    creator_id: str,
) -> Assignment:
    """アサインを登録する。"""
    # プロジェクト存在確認
    proj = await db.get(Project, data.project_id)
    if proj is None:
        raise HTTPException(status_code=404, detail="Project not found")

    assignment = Assignment(
        id=str(uuid.uuid4()),
        employee_id=employee_id,
        project_id=data.project_id,
        allocation_percent=data.allocation_percent,
        started_at=data.started_at,
        ends_at=data.ends_at,
        is_active=True,
        created_by=creator_id,
        created_at=datetime.now(UTC),
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return assignment


async def update_assignment(
    db: AsyncSession,
    assignment_id: str,
    data: AssignmentUpdate,
) -> Assignment:
    """アサイン情報を更新する。"""
    assignment = await db.get(Assignment, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if data.allocation_percent is not None:
        assignment.allocation_percent = data.allocation_percent
    if data.ends_at is not None:
        assignment.ends_at = data.ends_at
    if data.is_active is not None:
        assignment.is_active = data.is_active

    await db.commit()
    await db.refresh(assignment)
    return assignment
