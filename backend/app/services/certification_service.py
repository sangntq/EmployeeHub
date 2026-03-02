"""資格関連サービス"""
import uuid
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.certification import CertificationMaster, EmployeeCertification
from app.models.employee import Employee
from app.models.approval_history import ApprovalHistory
from app.schemas.certification import EmployeeCertCreate, ApproveCertRequest, RejectCertRequest
from app.services import notification_service


async def get_cert_masters(db: AsyncSession) -> list[CertificationMaster]:
    """資格マスタ一覧を返す。"""
    result = await db.execute(
        select(CertificationMaster)
        .where(CertificationMaster.is_active == True)
        .order_by(CertificationMaster.category, CertificationMaster.name)
    )
    return list(result.scalars().all())


async def get_employee_certs(
    db: AsyncSession, employee_id: str, status_filter: str | None = None
) -> list[EmployeeCertification]:
    """個人資格一覧を返す。"""
    query = (
        select(EmployeeCertification)
        .where(EmployeeCertification.employee_id == employee_id)
        .options(selectinload(EmployeeCertification.certification_master))
        .order_by(EmployeeCertification.obtained_at.desc())
    )
    if status_filter:
        query = query.where(EmployeeCertification.status == status_filter)
    result = await db.execute(query)
    return list(result.scalars().all())


async def apply_cert(
    db: AsyncSession, employee_id: str, data: EmployeeCertCreate, current_employee: Employee
) -> EmployeeCertification:
    """資格申請（本人のみ）。"""
    # マスタIDが指定されている場合は存在チェック
    if data.certification_master_id:
        master_result = await db.execute(
            select(CertificationMaster).where(
                CertificationMaster.id == data.certification_master_id,
                CertificationMaster.is_active == True,
            )
        )
        if not master_result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="資格マスタが見つかりません")

    now = datetime.now(UTC)
    emp_cert = EmployeeCertification(
        id=str(uuid.uuid4()),
        employee_id=employee_id,
        certification_master_id=data.certification_master_id,
        custom_name=data.custom_name,
        score=data.score,
        obtained_at=data.obtained_at,
        expires_at=data.expires_at,
        file_url=data.file_url,
        status="PENDING",
        created_at=now,
        updated_at=now,
    )
    db.add(emp_cert)

    db.add(ApprovalHistory(
        id=str(uuid.uuid4()),
        entity_type="employee_certification",
        entity_id=emp_cert.id,
        action="SUBMITTED",
        actor_id=current_employee.id,
        created_at=now,
    ))
    # 同部署の承認権限者に申請通知
    cert_name = data.custom_name or "資格"
    if data.certification_master_id:
        # apply_cert の先頭でマスタを取得済みなら渡したい。ここでは汎用名を使う
        cert_name = data.custom_name or "資格（マスタ）"
    await notification_service.notify_approval_requested(
        db, current_employee, "certification", cert_name, emp_cert.id
    )
    await db.commit()
    await db.refresh(emp_cert)
    return emp_cert


async def approve_cert(
    db: AsyncSession, cert_id: str, data: ApproveCertRequest, approver: Employee
) -> EmployeeCertification:
    """資格承認（manager / department_head / admin）。"""
    result = await db.execute(
        select(EmployeeCertification)
        .options(selectinload(EmployeeCertification.certification_master))
        .where(EmployeeCertification.id == cert_id)
    )
    emp_cert = result.scalar_one_or_none()
    if not emp_cert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="資格申請が見つかりません")
    if emp_cert.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="PENDING 状態の資格のみ承認できます")

    now = datetime.now(UTC)
    emp_cert.status = "APPROVED"
    emp_cert.approver_id = approver.id
    emp_cert.approver_comment = data.approver_comment
    emp_cert.approved_at = now
    emp_cert.updated_at = now

    db.add(ApprovalHistory(
        id=str(uuid.uuid4()),
        entity_type="employee_certification",
        entity_id=emp_cert.id,
        action="APPROVED",
        actor_id=approver.id,
        comment=data.approver_comment,
        created_at=now,
    ))
    # 申請者に承認通知
    notification_service.notify_cert_approved(db, emp_cert)
    await db.commit()
    await db.refresh(emp_cert)
    return emp_cert


async def reject_cert(
    db: AsyncSession, cert_id: str, data: RejectCertRequest, approver: Employee
) -> EmployeeCertification:
    """資格差し戻し（manager / department_head / admin）。"""
    result = await db.execute(
        select(EmployeeCertification)
        .options(selectinload(EmployeeCertification.certification_master))
        .where(EmployeeCertification.id == cert_id)
    )
    emp_cert = result.scalar_one_or_none()
    if not emp_cert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="資格申請が見つかりません")
    if emp_cert.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="PENDING 状態の資格のみ差し戻せます")

    now = datetime.now(UTC)
    emp_cert.status = "REJECTED"
    emp_cert.approver_id = approver.id
    emp_cert.approver_comment = data.approver_comment
    emp_cert.approved_at = now
    emp_cert.updated_at = now

    db.add(ApprovalHistory(
        id=str(uuid.uuid4()),
        entity_type="employee_certification",
        entity_id=emp_cert.id,
        action="REJECTED",
        actor_id=approver.id,
        comment=data.approver_comment,
        created_at=now,
    ))
    # 申請者に差し戻し通知
    notification_service.notify_cert_rejected(db, emp_cert, data.approver_comment)
    await db.commit()
    await db.refresh(emp_cert)
    return emp_cert


async def get_pending_certs(db: AsyncSession) -> list[EmployeeCertification]:
    """PENDING 状態の資格申請一覧（承認キュー用）。"""
    result = await db.execute(
        select(EmployeeCertification)
        .options(
            selectinload(EmployeeCertification.certification_master),
            selectinload(EmployeeCertification.employee),
        )
        .where(EmployeeCertification.status == "PENDING")
        .order_by(EmployeeCertification.created_at.asc())
    )
    return list(result.scalars().all())
