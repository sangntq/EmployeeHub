"""スキル関連サービス"""
import uuid
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.skill import SkillCategory, Skill, EmployeeSkill
from app.models.employee import Employee
from app.models.approval_history import ApprovalHistory
from app.schemas.skill import EmployeeSkillCreate, ApproveSkillRequest, RejectSkillRequest
from app.services import notification_service


async def get_skill_categories(db: AsyncSession) -> list[SkillCategory]:
    """全スキルカテゴリとスキル一覧を返す（カテゴリ別グループ化）。"""
    result = await db.execute(
        select(SkillCategory)
        .options(selectinload(SkillCategory.skills))
        .order_by(SkillCategory.sort_order)
    )
    categories = list(result.scalars().all())
    # アクティブスキルのみに絞り込む
    for cat in categories:
        cat.skills = [s for s in cat.skills if s.is_active]
    return categories


async def get_employee_skills(
    db: AsyncSession, employee_id: str, status_filter: str | None = None
) -> list[EmployeeSkill]:
    """個人スキル一覧を返す。"""
    query = (
        select(EmployeeSkill)
        .where(EmployeeSkill.employee_id == employee_id)
        .options(selectinload(EmployeeSkill.skill))
        .order_by(EmployeeSkill.created_at.desc())
    )
    if status_filter:
        query = query.where(EmployeeSkill.status == status_filter)
    result = await db.execute(query)
    return list(result.scalars().all())


async def apply_skill(
    db: AsyncSession, employee_id: str, data: EmployeeSkillCreate, current_employee: Employee
) -> EmployeeSkill:
    """スキル申請（本人のみ）。"""
    # スキルが存在するか確認
    skill_result = await db.execute(select(Skill).where(Skill.id == data.skill_id, Skill.is_active == True))
    skill = skill_result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="スキルが見つかりません")

    # 既存申請チェック
    existing = await db.execute(
        select(EmployeeSkill).where(
            EmployeeSkill.employee_id == employee_id,
            EmployeeSkill.skill_id == data.skill_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="このスキルはすでに申請済みです")

    now = datetime.now(UTC)
    emp_skill = EmployeeSkill(
        id=str(uuid.uuid4()),
        employee_id=employee_id,
        skill_id=data.skill_id,
        self_level=data.self_level,
        experience_years=data.experience_years,
        last_used_at=data.last_used_at,
        self_comment=data.self_comment,
        status="PENDING",
        created_at=now,
        updated_at=now,
    )
    db.add(emp_skill)

    # 承認履歴に SUBMITTED を記録
    db.add(ApprovalHistory(
        id=str(uuid.uuid4()),
        entity_type="employee_skill",
        entity_id=emp_skill.id,
        action="SUBMITTED",
        actor_id=current_employee.id,
        comment=data.self_comment,
        created_at=now,
    ))
    # 同部署の承認権限者に申請通知
    await notification_service.notify_approval_requested(
        db, current_employee, "skill", skill.name, emp_skill.id
    )
    await db.commit()
    await db.refresh(emp_skill)
    return emp_skill


async def approve_skill(
    db: AsyncSession, skill_record_id: str, data: ApproveSkillRequest, approver: Employee
) -> EmployeeSkill:
    """スキル承認（manager / department_head / admin）。"""
    result = await db.execute(
        select(EmployeeSkill)
        .options(selectinload(EmployeeSkill.skill))
        .where(EmployeeSkill.id == skill_record_id)
    )
    emp_skill = result.scalar_one_or_none()
    if not emp_skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="スキル申請が見つかりません")
    if emp_skill.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="PENDING 状態のスキルのみ承認できます")

    now = datetime.now(UTC)
    emp_skill.status = "APPROVED"
    emp_skill.approved_level = data.approved_level
    emp_skill.approver_id = approver.id
    emp_skill.approver_comment = data.approver_comment
    emp_skill.approved_at = now
    emp_skill.updated_at = now

    db.add(ApprovalHistory(
        id=str(uuid.uuid4()),
        entity_type="employee_skill",
        entity_id=emp_skill.id,
        action="APPROVED",
        actor_id=approver.id,
        comment=data.approver_comment,
        created_at=now,
    ))
    # 申請者に承認通知
    notification_service.notify_skill_approved(db, emp_skill)
    await db.commit()
    await db.refresh(emp_skill)
    return emp_skill


async def reject_skill(
    db: AsyncSession, skill_record_id: str, data: RejectSkillRequest, approver: Employee
) -> EmployeeSkill:
    """スキル差し戻し（manager / department_head / admin）。"""
    result = await db.execute(
        select(EmployeeSkill)
        .options(selectinload(EmployeeSkill.skill))
        .where(EmployeeSkill.id == skill_record_id)
    )
    emp_skill = result.scalar_one_or_none()
    if not emp_skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="スキル申請が見つかりません")
    if emp_skill.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="PENDING 状態のスキルのみ差し戻せます")

    now = datetime.now(UTC)
    emp_skill.status = "REJECTED"
    emp_skill.approver_id = approver.id
    emp_skill.approver_comment = data.approver_comment
    emp_skill.approved_at = now
    emp_skill.updated_at = now

    db.add(ApprovalHistory(
        id=str(uuid.uuid4()),
        entity_type="employee_skill",
        entity_id=emp_skill.id,
        action="REJECTED",
        actor_id=approver.id,
        comment=data.approver_comment,
        created_at=now,
    ))
    # 申請者に差し戻し通知
    notification_service.notify_skill_rejected(db, emp_skill, data.approver_comment)
    await db.commit()
    await db.refresh(emp_skill)
    return emp_skill


async def get_pending_skills(db: AsyncSession) -> list[EmployeeSkill]:
    """PENDING 状態のスキル申請一覧（承認キュー用）。"""
    result = await db.execute(
        select(EmployeeSkill)
        .options(selectinload(EmployeeSkill.skill), selectinload(EmployeeSkill.employee))
        .where(EmployeeSkill.status == "PENDING")
        .order_by(EmployeeSkill.created_at.asc())
    )
    return list(result.scalars().all())
