"""
スケジューラーサービス（APScheduler）

毎日08:00 JSTに以下のジョブを実行する:
- ビザ期限チェック（60日/30日/7日前）
- 資格期限チェック（90日/30日前）
- アサイン終了チェック（7日前）
"""
import logging
from datetime import date, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.project import VisaInfo
from app.models.certification import EmployeeCertification
from app.models.work_status import Assignment
from app.models.notification import Notification
from app.models.employee import Employee
from app.services import notification_service
from app.services.email_service import send_email

logger = logging.getLogger(__name__)

# 既に通知済みかを確認する日数ウィンドウ（同日・同種・同受信者の重複防止）
_DEDUP_DAYS = 1


async def _already_notified(db, recipient_id: str, notif_type: str, entity_id: str) -> bool:
    """直近1日以内に同種・同エンティティの通知を送信済みかチェック。"""
    from datetime import datetime, UTC
    since = datetime.now(UTC) - timedelta(days=_DEDUP_DAYS)
    result = await db.execute(
        select(func.count()).select_from(Notification).where(
            Notification.recipient_id == recipient_id,
            Notification.type == notif_type,
            Notification.related_entity_id == entity_id,
            Notification.created_at >= since,
        )
    )
    return (result.scalar() or 0) > 0


async def job_check_visa_expiry() -> None:
    """ビザ期限が60日/30日/7日以内の社員に通知する。"""
    today = date.today()
    thresholds = [
        (7,  "【緊急】ビザ有効期限が7日以内です"),
        (30, "ビザ有効期限が30日以内です"),
        (60, "ビザ有効期限が60日以内です"),
    ]

    async with AsyncSessionLocal() as db:
        try:
            for days, title in thresholds:
                target_date = today + timedelta(days=days)
                result = await db.execute(
                    select(VisaInfo)
                    .options(selectinload(VisaInfo.employee))
                    .where(
                        VisaInfo.expires_at <= target_date,
                        VisaInfo.expires_at >= today,
                    )
                )
                visa_records = result.scalars().all()

                for vi in visa_records:
                    if not vi.employee or not vi.employee.is_active:
                        continue
                    if await _already_notified(db, vi.employee_id, "VISA_EXPIRY", vi.id):
                        continue

                    body = f"ビザ有効期限: {vi.expires_at} （あと{(vi.expires_at - today).days}日）"
                    notification_service._add_notification(
                        db,
                        recipient_id=vi.employee_id,
                        notif_type="VISA_EXPIRY",
                        title=title,
                        body=body,
                        related_entity_type="visa_info",
                        related_entity_id=vi.id,
                    )
                    # メール送信
                    if vi.employee.email:
                        await send_email(
                            to=vi.employee.email,
                            subject=f"[EmployeeHub] {title}",
                            body=body,
                        )

            await db.commit()
            logger.info("[Scheduler] visa_expiry job completed")
        except Exception as exc:
            await db.rollback()
            logger.error("[Scheduler] visa_expiry job failed: %s", exc)


async def job_check_cert_expiry() -> None:
    """資格期限が90日/30日以内の社員に通知する（APPROVED のみ）。"""
    today = date.today()
    thresholds = [
        (30, "資格の有効期限が30日以内です"),
        (90, "資格の有効期限が90日以内です"),
    ]

    async with AsyncSessionLocal() as db:
        try:
            for days, title in thresholds:
                target_date = today + timedelta(days=days)
                result = await db.execute(
                    select(EmployeeCertification)
                    .options(selectinload(EmployeeCertification.certification_master))
                    .where(
                        EmployeeCertification.status == "APPROVED",
                        EmployeeCertification.expires_at != None,
                        EmployeeCertification.expires_at <= target_date,
                        EmployeeCertification.expires_at >= today,
                    )
                )
                certs = result.scalars().all()

                for ec in certs:
                    if await _already_notified(db, ec.employee_id, "CERT_EXPIRY", ec.id):
                        continue

                    cert_name = (
                        ec.certification_master.name
                        if ec.certification_master
                        else ec.custom_name or "資格"
                    )
                    body = f"資格「{cert_name}」の有効期限: {ec.expires_at}"
                    notification_service._add_notification(
                        db,
                        recipient_id=ec.employee_id,
                        notif_type="CERT_EXPIRY",
                        title=title,
                        body=body,
                        related_entity_type="employee_certification",
                        related_entity_id=ec.id,
                    )

            await db.commit()
            logger.info("[Scheduler] cert_expiry job completed")
        except Exception as exc:
            await db.rollback()
            logger.error("[Scheduler] cert_expiry job failed: %s", exc)


async def job_check_assignment_ending() -> None:
    """アサイン終了が7日以内の社員に通知する。"""
    today = date.today()
    deadline = today + timedelta(days=7)

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Assignment)
                .where(
                    Assignment.is_active == True,
                    Assignment.ends_at != None,
                    Assignment.ends_at <= deadline,
                    Assignment.ends_at >= today,
                )
            )
            assignments = result.scalars().all()

            for asgn in assignments:
                if await _already_notified(db, asgn.employee_id, "ASSIGNMENT_ENDING", asgn.id):
                    continue

                body = f"アサイン終了予定日: {asgn.ends_at} （あと{(asgn.ends_at - today).days}日）"
                notification_service._add_notification(
                    db,
                    recipient_id=asgn.employee_id,
                    notif_type="ASSIGNMENT_ENDING",
                    title="アサインが終了間近です",
                    body=body,
                    related_entity_type="assignment",
                    related_entity_id=asgn.id,
                )

            await db.commit()
            logger.info("[Scheduler] assignment_ending job completed")
        except Exception as exc:
            await db.rollback()
            logger.error("[Scheduler] assignment_ending job failed: %s", exc)


def start_scheduler() -> AsyncIOScheduler:
    """スケジューラーを起動して返す。"""
    scheduler = AsyncIOScheduler(timezone="Asia/Tokyo")
    scheduler.add_job(job_check_visa_expiry,       "cron", hour=8, minute=0)
    scheduler.add_job(job_check_cert_expiry,        "cron", hour=8, minute=5)
    scheduler.add_job(job_check_assignment_ending,  "cron", hour=8, minute=10)
    scheduler.start()
    logger.info("[Scheduler] Started (visa, cert, assignment jobs at 08:00 JST)")
    return scheduler


def stop_scheduler(scheduler: AsyncIOScheduler) -> None:
    """スケジューラーを停止する。"""
    scheduler.shutdown(wait=False)
    logger.info("[Scheduler] Stopped")
