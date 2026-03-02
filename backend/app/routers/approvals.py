"""承認キュールーター

エンドポイント:
  GET  /approvals/pending    PENDING 状態のスキル・資格申請一覧（manager以上）
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.models.employee import Employee
from app.schemas.certification import PendingApprovalsResponse, PendingCertItem
from app.schemas.skill import PendingSkillItem
from app.services import skill_service, certification_service

router = APIRouter()


@router.get("/approvals/pending", response_model=PendingApprovalsResponse)
async def list_pending_approvals(
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(require_role("manager", "department_head", "admin")),
):
    """PENDING 状態のスキル・資格申請一覧。manager / department_head / admin のみ。"""
    pending_skills = await skill_service.get_pending_skills(db)
    pending_certs = await certification_service.get_pending_certs(db)

    return PendingApprovalsResponse(
        skills=[
            PendingSkillItem(
                id=s.id,
                employee_id=s.employee_id,
                employee_name_ja=s.employee.name_ja,
                employee_number=s.employee.employee_number,
                skill_name=s.skill.name,
                self_level=s.self_level,
                experience_years=float(s.experience_years) if s.experience_years else None,
                evidence_file_url=s.evidence_file_url,
                self_comment=s.self_comment,
                submitted_at=s.created_at,
            )
            for s in pending_skills
        ],
        certifications=[
            PendingCertItem(
                id=c.id,
                employee_id=c.employee_id,
                employee_name_ja=c.employee.name_ja,
                employee_number=c.employee.employee_number,
                cert_name=c.certification_master.name if c.certification_master else (c.custom_name or ""),
                obtained_at=c.obtained_at,
                expires_at=c.expires_at,
                score=c.score,
                file_url=c.file_url,
                submitted_at=c.created_at,
            )
            for c in pending_certs
        ],
    )
