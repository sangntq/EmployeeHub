"""
通知サービス

- CRUD: 一覧取得・既読マーク
- イベントヘルパー: スキル/資格 承認・差し戻し・申請時に呼ぶ（commit なし、呼び出し元でcommit）
"""
import uuid
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from fastapi import HTTPException, status

from app.models.notification import Notification
from app.models.employee import Employee
from app.schemas.notification import NotificationListResponse, NotificationResponse


# ── CRUD ──────────────────────────────────────────────────────────────────────

async def get_notifications(
    db: AsyncSession,
    employee_id: str,
    is_read: bool | None = None,
    page: int = 1,
    per_page: int = 20,
) -> NotificationListResponse:
    """自分宛の通知一覧（ページネーション付き）。"""
    base_q = select(Notification).where(Notification.recipient_id == employee_id)
    if is_read is not None:
        base_q = base_q.where(Notification.is_read == is_read)

    # 未読件数
    unread_result = await db.execute(
        select(func.count()).select_from(Notification).where(
            Notification.recipient_id == employee_id,
            Notification.is_read == False,
        )
    )
    unread_count = unread_result.scalar() or 0

    # 全件数
    count_result = await db.execute(
        select(func.count()).select_from(base_q.subquery())
    )
    total = count_result.scalar() or 0

    # ページネーション
    offset = (page - 1) * per_page
    result = await db.execute(
        base_q.order_by(Notification.created_at.desc()).offset(offset).limit(per_page)
    )
    items = list(result.scalars().all())

    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in items],
        total=total,
        unread_count=unread_count,
        page=page,
        per_page=per_page,
    )


async def mark_as_read(db: AsyncSession, notification_id: str, employee_id: str) -> None:
    """指定の通知を既読にする（本人のみ）。"""
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="通知が見つかりません")
    if notif.recipient_id != employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="他人の通知は操作できません")
    notif.is_read = True
    await db.commit()


async def mark_all_read(db: AsyncSession, employee_id: str) -> None:
    """全通知を既読にする（本人のみ）。"""
    await db.execute(
        update(Notification)
        .where(Notification.recipient_id == employee_id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.commit()


# ── 内部ヘルパー（commit なし） ───────────────────────────────────────────────

def _add_notification(
    db: AsyncSession,
    recipient_id: str,
    notif_type: str,
    title: str,
    body: str | None = None,
    related_entity_type: str | None = None,
    related_entity_id: str | None = None,
) -> None:
    """通知レコードをセッションに追加する（commitは呼び出し元に委譲）。"""
    db.add(Notification(
        id=str(uuid.uuid4()),
        recipient_id=recipient_id,
        type=notif_type,
        title=title,
        body=body,
        is_read=False,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        created_at=datetime.now(UTC),
    ))


# ── スキル系イベントヘルパー ──────────────────────────────────────────────────

def notify_skill_approved(db: AsyncSession, emp_skill) -> None:
    """スキル承認 → 申請者に通知（commit なし）。"""
    skill_name = emp_skill.skill.name if emp_skill.skill else "スキル"
    _add_notification(
        db,
        recipient_id=emp_skill.employee_id,
        notif_type="SKILL_APPROVED",
        title=f"スキル「{skill_name}」が承認されました",
        body=f"承認レベル: {emp_skill.approved_level}",
        related_entity_type="employee_skill",
        related_entity_id=emp_skill.id,
    )


def notify_skill_rejected(db: AsyncSession, emp_skill, comment: str | None) -> None:
    """スキル差し戻し → 申請者に通知（commit なし）。"""
    skill_name = emp_skill.skill.name if emp_skill.skill else "スキル"
    _add_notification(
        db,
        recipient_id=emp_skill.employee_id,
        notif_type="SKILL_REJECTED",
        title=f"スキル「{skill_name}」が差し戻されました",
        body=comment,
        related_entity_type="employee_skill",
        related_entity_id=emp_skill.id,
    )


# ── 資格系イベントヘルパー ────────────────────────────────────────────────────

def notify_cert_approved(db: AsyncSession, emp_cert) -> None:
    """資格承認 → 申請者に通知（commit なし）。"""
    if emp_cert.certification_master:
        cert_name = emp_cert.certification_master.name
    else:
        cert_name = emp_cert.custom_name or "資格"
    _add_notification(
        db,
        recipient_id=emp_cert.employee_id,
        notif_type="CERT_APPROVED",
        title=f"資格「{cert_name}」が承認されました",
        related_entity_type="employee_certification",
        related_entity_id=emp_cert.id,
    )


def notify_cert_rejected(db: AsyncSession, emp_cert, comment: str | None) -> None:
    """資格差し戻し → 申請者に通知（commit なし）。"""
    if emp_cert.certification_master:
        cert_name = emp_cert.certification_master.name
    else:
        cert_name = emp_cert.custom_name or "資格"
    _add_notification(
        db,
        recipient_id=emp_cert.employee_id,
        notif_type="CERT_REJECTED",
        title=f"資格「{cert_name}」が差し戻されました",
        body=comment,
        related_entity_type="employee_certification",
        related_entity_id=emp_cert.id,
    )


# ── 申請時ヘルパー（承認者への通知 — 非同期クエリあり） ─────────────────────

async def notify_approval_requested(
    db: AsyncSession,
    employee: Employee,
    entity_type: str,
    entity_name: str,
    entity_id: str,
) -> None:
    """スキル/資格申請 → 同部署の manager/department_head/admin に通知（commit なし）。"""
    q = select(Employee).where(
        Employee.system_role.in_(["manager", "department_head", "admin"]),
        Employee.is_active == True,
        Employee.id != employee.id,
    )
    if employee.department_id:
        q = q.where(Employee.department_id == employee.department_id)

    result = await db.execute(q)
    approvers = result.scalars().all()

    submitter_name = employee.name_ja or employee.name_en or "社員"
    type_label = "スキル" if entity_type == "skill" else "資格"
    entity_table = "employee_skill" if entity_type == "skill" else "employee_certification"

    for approver in approvers:
        _add_notification(
            db,
            recipient_id=approver.id,
            notif_type="APPROVAL_REQUESTED",
            title="承認申請が届いています",
            body=f"{submitter_name}さんが{type_label}「{entity_name}」を申請しました。",
            related_entity_type=entity_table,
            related_entity_id=entity_id,
        )
