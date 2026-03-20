"""資格マトリクスサービス"""
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.models.employee import Employee
from app.models.certification import CertificationMaster, EmployeeCertification
from app.models.work_status import WorkStatus
from app.schemas.employee import EmployeeListItem
from app.schemas.certmatrix import (
    CertInfo,
    EngineerCertEntry,
    CertMatrixCategory,
    CertEngineerRow,
    CertMatrixResponse,
)

# カテゴリの表示順序
CATEGORY_ORDER = ["LANGUAGE", "CLOUD", "PM", "NETWORK", "SECURITY", "OTHER"]


def _expiry_status(expires_at: date | None) -> str:
    """有効期限ステータスを判定する。"""
    if expires_at is None:
        return "NO_EXPIRY"
    if expires_at <= date.today() + timedelta(days=60):
        return "SOON"
    return "VALID"


async def get_cert_matrix(
    db: AsyncSession,
    location: str | None = None,
    category: str | None = None,
    free_only: bool = False,
    search: str | None = None,
) -> CertMatrixResponse:
    """資格マトリクスを返す。

    Args:
        db: DBセッション
        location: office_location フィルター
        category: 資格カテゴリフィルター (LANGUAGE, CLOUD, etc.)
        free_only: True の場合、FREE_IMMEDIATE / FREE_PLANNED のみ
        search: 社員名・番号の部分一致検索
    """
    # ── アクティブ社員を取得 ────────────────────────────────────────────────
    emp_query = (
        select(Employee)
        .where(Employee.is_active == True)
        .options(selectinload(Employee.department))
        .order_by(Employee.employee_number)
    )
    if location:
        emp_query = emp_query.where(Employee.office_location == location)
    if search:
        like_pattern = f"%{search}%"
        emp_query = emp_query.where(
            or_(
                Employee.name_ja.ilike(like_pattern),
                Employee.name_en.ilike(like_pattern),
                Employee.employee_number.ilike(like_pattern),
            )
        )
    if free_only:
        free_subq = (
            select(WorkStatus.employee_id)
            .where(WorkStatus.status.in_(["FREE_IMMEDIATE", "FREE_PLANNED"]))
            .scalar_subquery()
        )
        emp_query = emp_query.where(Employee.id.in_(free_subq))

    emp_result = await db.execute(emp_query)
    employees = list(emp_result.scalars().all())

    if not employees:
        return CertMatrixResponse(categories=[], engineers=[])

    employee_ids = [e.id for e in employees]

    # ── 全資格マスタを取得 ────────────────────────────────────────────────
    cert_master_query = select(CertificationMaster).where(
        CertificationMaster.is_active == True
    )
    if category:
        cert_master_query = cert_master_query.where(
            CertificationMaster.category == category
        )

    cert_master_result = await db.execute(cert_master_query)
    all_masters = list(cert_master_result.scalars().all())

    master_map: dict[str, CertificationMaster] = {m.id: m for m in all_masters}

    # ── APPROVED 資格を一括取得 ───────────────────────────────────────────
    cert_query = (
        select(EmployeeCertification)
        .where(
            EmployeeCertification.employee_id.in_(employee_ids),
            EmployeeCertification.status == "APPROVED",
            EmployeeCertification.certification_master_id.isnot(None),
        )
    )
    if category:
        cert_query = cert_query.where(
            EmployeeCertification.certification_master_id.in_(list(master_map.keys()))
        )

    cert_result = await db.execute(cert_query)
    cert_rows = cert_result.scalars().all()

    # ── データ集計 ──────────────────────────────────────────────────────────
    emp_cert_map: dict[str, dict[str, EngineerCertEntry]] = {
        eid: {} for eid in employee_ids
    }

    for ec in cert_rows:
        if ec.certification_master_id not in master_map:
            continue
        emp_cert_map[ec.employee_id][ec.certification_master_id] = EngineerCertEntry(
            cert_id=ec.certification_master_id,
            obtained_at=ec.obtained_at.isoformat() if ec.obtained_at else None,
            expires_at=ec.expires_at.isoformat() if ec.expires_at else None,
            expiry_status=_expiry_status(ec.expires_at),
        )

    # ── カテゴリ・資格構造を構築（全マスタを含む） ────────────────────────
    cat_groups: dict[str, list[CertificationMaster]] = {}
    for m in all_masters:
        cat_groups.setdefault(str(m.category), []).append(m)

    categories: list[CertMatrixCategory] = []
    for cat_key in CATEGORY_ORDER:
        masters = cat_groups.get(cat_key, [])
        if not masters:
            continue
        # 名前順でソート
        masters.sort(key=lambda m: m.name)
        cert_infos = [CertInfo(id=m.id, name=m.name) for m in masters]
        categories.append(
            CertMatrixCategory(category=cat_key, certifications=cert_infos)
        )

    # ── エンジニア行を構築 ─────────────────────────────────────────────────
    engineers: list[CertEngineerRow] = []
    for emp in employees:
        emp_item = EmployeeListItem.model_validate(emp)
        engineers.append(
            CertEngineerRow(
                employee=emp_item,
                certs=emp_cert_map.get(emp.id, {}),
            )
        )

    return CertMatrixResponse(categories=categories, engineers=engineers)
