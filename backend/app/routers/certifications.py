"""資格関連ルーター

エンドポイント:
  GET  /certification-masters                         資格マスタ一覧
  GET  /employees/{id}/certifications                 個人資格一覧
  POST /employees/{id}/certifications                 資格申請（本人のみ）
  PATCH /certifications/{id}/approve                  承認（manager以上）
  PATCH /certifications/{id}/reject                   差し戻し（manager以上）
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_employee, require_role
from app.models.employee import Employee
from app.schemas.certification import (
    CertificationMasterResponse,
    EmployeeCertCreate,
    EmployeeCertResponse,
    ApproveCertRequest,
    RejectCertRequest,
)
from app.services import certification_service

router = APIRouter()


@router.get("/certification-masters", response_model=list[CertificationMasterResponse])
async def list_cert_masters(
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(get_current_employee),
):
    """資格マスタ一覧。認証済みユーザー全員が閲覧可能。"""
    masters = await certification_service.get_cert_masters(db)
    return [CertificationMasterResponse.model_validate(m) for m in masters]


@router.get("/employees/{employee_id}/certifications", response_model=list[EmployeeCertResponse])
async def list_employee_certifications(
    employee_id: str,
    status: str | None = Query(None, description="PENDING / APPROVED / REJECTED"),
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(get_current_employee),
):
    """個人資格一覧。本人または manager 以上が閲覧可能。"""
    if current.system_role == "member" and current.id != employee_id:
        raise HTTPException(
            status_code=403, detail="他の社員の資格は閲覧できません"
        )
    certs = await certification_service.get_employee_certs(db, employee_id, status)
    return [EmployeeCertResponse.model_validate(c) for c in certs]


@router.post("/employees/{employee_id}/certifications", response_model=EmployeeCertResponse, status_code=201)
async def apply_certification(
    employee_id: str,
    body: EmployeeCertCreate,
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(get_current_employee),
):
    """資格申請。本人のみ。"""
    if current.id != employee_id:
        raise HTTPException(status_code=403, detail="自分の資格のみ申請できます")
    emp_cert = await certification_service.apply_cert(db, employee_id, body, current)
    return EmployeeCertResponse.model_validate(emp_cert)


@router.patch("/certifications/{cert_record_id}/approve", response_model=EmployeeCertResponse)
async def approve_certification(
    cert_record_id: str,
    body: ApproveCertRequest,
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(require_role("manager", "department_head", "admin")),
):
    """資格承認。manager / department_head / admin のみ。"""
    emp_cert = await certification_service.approve_cert(db, cert_record_id, body, current)
    return EmployeeCertResponse.model_validate(emp_cert)


@router.patch("/certifications/{cert_record_id}/reject", response_model=EmployeeCertResponse)
async def reject_certification(
    cert_record_id: str,
    body: RejectCertRequest,
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(require_role("manager", "department_head", "admin")),
):
    """資格差し戻し。manager / department_head / admin のみ。"""
    emp_cert = await certification_service.reject_cert(db, cert_record_id, body, current)
    return EmployeeCertResponse.model_validate(emp_cert)
