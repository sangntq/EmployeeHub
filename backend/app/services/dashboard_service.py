"""
ダッシュボード集計サービス

全エンドポイントのビジネスロジック（SQL集計）を実装する。
注意: 日付演算はPython timedelta を使用（PostgreSQL INTERVALはSQLiteテストで動作しない）。
"""
import calendar
from datetime import date, timedelta

from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.skill import Skill, SkillCategory, EmployeeSkill
from app.models.certification import EmployeeCertification
from app.models.work_status import WorkStatus, Assignment
from app.models.project import VisaInfo
from app.schemas.dashboard import (
    AlertCounts,
    AlertEmployeeEmbed,
    AlertItem,
    AlertListResponse,
    DashboardOverviewResponse,
    DistributionItem,
    FreeForecastMonth,
    FreeForecastResponse,
    HeadcountTrendItem,
    HeadcountTrendResponse,
    LocationDistributionResponse,
    SkillDistributionItem,
    SkillHeatmapCell,
    SkillHeatmapResponse,
    SkillsDistributionResponse,
    UtilizationMonth,
    UtilizationTrendResponse,
)


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    """指定年月の初日・末日を返す。"""
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def _add_months(d: date, n: int) -> date:
    """n ヶ月後の月初を返す（月をまたぐ加算）。"""
    month = d.month - 1 + n
    year = d.year + month // 12
    month = month % 12 + 1
    return date(year, month, 1)


async def get_overview(db: AsyncSession) -> DashboardOverviewResponse:
    """ダッシュボード概要（KPI4件＋アラート件数）を返す。"""
    today = date.today()
    thirty_days = today + timedelta(days=30)

    # ── 総社員数 ──────────────────────────────────────────────────────────
    total_result = await db.execute(
        select(func.count(Employee.id)).where(Employee.is_active == True)
    )
    total = total_result.scalar() or 0

    # ── 稼働状況別カウント ──────────────────────────────────────────────
    status_result = await db.execute(
        select(WorkStatus.status, func.count(WorkStatus.id))
        .join(Employee, WorkStatus.employee_id == Employee.id)
        .where(Employee.is_active == True)
        .group_by(WorkStatus.status)
    )
    status_counts = {row[0]: row[1] for row in status_result.all()}

    assigned = status_counts.get("ASSIGNED", 0)
    free_immediate = status_counts.get("FREE_IMMEDIATE", 0)
    free_planned = status_counts.get("FREE_PLANNED", 0)
    utilization_rate = round(assigned / total * 100, 1) if total > 0 else 0.0

    # ── 承認待ち件数 ──────────────────────────────────────────────────────
    pending_skills_result = await db.execute(
        select(func.count(EmployeeSkill.id)).where(EmployeeSkill.status == "PENDING")
    )
    pending_skills = pending_skills_result.scalar() or 0

    pending_certs_result = await db.execute(
        select(func.count(EmployeeCertification.id)).where(
            EmployeeCertification.status == "PENDING"
        )
    )
    pending_certs = pending_certs_result.scalar() or 0
    pending_approvals = pending_skills + pending_certs

    # ── ビザ期限 30日以内 ──────────────────────────────────────────────
    visa_result = await db.execute(
        select(func.count(VisaInfo.id))
        .join(Employee, VisaInfo.employee_id == Employee.id)
        .where(
            VisaInfo.expires_at != None,
            VisaInfo.expires_at >= today,
            VisaInfo.expires_at <= thirty_days,
            Employee.is_active == True,
        )
    )
    visa_expiry_30d = visa_result.scalar() or 0

    # ── 資格期限 30日以内（APPROVED のみ）────────────────────────────
    cert_result = await db.execute(
        select(func.count(EmployeeCertification.id))
        .join(Employee, EmployeeCertification.employee_id == Employee.id)
        .where(
            EmployeeCertification.expires_at != None,
            EmployeeCertification.expires_at >= today,
            EmployeeCertification.expires_at <= thirty_days,
            EmployeeCertification.status == "APPROVED",
            Employee.is_active == True,
        )
    )
    cert_expiry_30d = cert_result.scalar() or 0

    return DashboardOverviewResponse(
        total_employees=total,
        assigned=assigned,
        free_immediate=free_immediate,
        free_planned=free_planned,
        utilization_rate=utilization_rate,
        pending_approvals=pending_approvals,
        alerts=AlertCounts(
            visa_expiry_30d=visa_expiry_30d,
            cert_expiry_30d=cert_expiry_30d,
        ),
    )


async def get_utilization_trend(
    db: AsyncSession,
    months: int = 6,
) -> UtilizationTrendResponse:
    """過去 N ヶ月の稼働率推移を返す。

    アサイン記録（assignments テーブル）を使って各月に稼働していた人数を集計する。
    """
    today = date.today()
    result_months: list[UtilizationMonth] = []

    for i in range(months - 1, -1, -1):
        # 対象月を計算（0=今月, 1=先月, ...）
        target_month_start = _add_months(date(today.year, today.month, 1), -i)
        _, last = _month_bounds(target_month_start.year, target_month_start.month)
        first = target_month_start
        month_label = first.strftime("%Y-%m")

        # その月末時点での在籍社員数
        total_result = await db.execute(
            select(func.count(Employee.id)).where(
                Employee.is_active == True,
                Employee.joined_at <= last,
            )
        )
        total = total_result.scalar() or 0

        # その月に稼働していた（アサインされていた）社員数
        assigned_result = await db.execute(
            select(func.count(distinct(Assignment.employee_id)))
            .join(Employee, Assignment.employee_id == Employee.id)
            .where(
                Employee.is_active == True,
                Assignment.started_at <= last,
                (Assignment.ends_at == None) | (Assignment.ends_at >= first),
            )
        )
        assigned = assigned_result.scalar() or 0

        util_rate = round(assigned / total * 100, 1) if total > 0 else 0.0
        result_months.append(
            UtilizationMonth(
                month=month_label,
                assigned=assigned,
                total=total,
                utilization_rate=util_rate,
            )
        )

    return UtilizationTrendResponse(months=result_months)


async def get_free_forecast(db: AsyncSession) -> FreeForecastResponse:
    """今後3ヶ月のフリー人材数予測を返す。

    現在 FREE_IMMEDIATE + 各月末までに FREE_PLANNED になる人数の累計。
    """
    today = date.today()

    # 現在のフリー（即時）
    free_now_result = await db.execute(
        select(func.count(WorkStatus.id))
        .join(Employee, WorkStatus.employee_id == Employee.id)
        .where(
            WorkStatus.status == "FREE_IMMEDIATE",
            Employee.is_active == True,
        )
    )
    free_now = free_now_result.scalar() or 0

    forecast: list[FreeForecastMonth] = []
    for i in range(1, 4):  # 1〜3ヶ月後
        month_start = _add_months(date(today.year, today.month, 1), i)
        _, month_end = _month_bounds(month_start.year, month_start.month)
        month_label = month_start.strftime("%Y-%m")

        # その月末までにフリーになる予定の人数（FREE_PLANNED で free_from が月末以前）
        becoming_result = await db.execute(
            select(func.count(WorkStatus.id))
            .join(Employee, WorkStatus.employee_id == Employee.id)
            .where(
                WorkStatus.status == "FREE_PLANNED",
                WorkStatus.free_from != None,
                WorkStatus.free_from <= month_end,
                Employee.is_active == True,
            )
        )
        becoming = becoming_result.scalar() or 0

        forecast.append(
            FreeForecastMonth(
                month=month_label,
                free_count=free_now + becoming,
            )
        )

    return FreeForecastResponse(forecast=forecast)


async def get_skills_distribution(db: AsyncSession) -> SkillsDistributionResponse:
    """フリー人材のスキル分布（上位10件）を返す。"""
    result = await db.execute(
        select(Skill.name, func.count(distinct(EmployeeSkill.employee_id)).label("cnt"))
        .join(EmployeeSkill, EmployeeSkill.skill_id == Skill.id)
        .join(WorkStatus, WorkStatus.employee_id == EmployeeSkill.employee_id)
        .join(Employee, Employee.id == EmployeeSkill.employee_id)
        .where(
            EmployeeSkill.status == "APPROVED",
            WorkStatus.status.in_(["FREE_IMMEDIATE", "FREE_PLANNED"]),
            Employee.is_active == True,
        )
        .group_by(Skill.id, Skill.name)
        .order_by(func.count(distinct(EmployeeSkill.employee_id)).desc())
        .limit(10)
    )
    items = [
        SkillDistributionItem(skill_name=row[0], free_count=row[1])
        for row in result.all()
    ]
    return SkillsDistributionResponse(items=items)


async def get_alerts(
    db: AsyncSession,
    alert_type: str | None,
    days: int,
) -> AlertListResponse:
    """期限アラート一覧（ビザ期限・資格期限）を返す。"""
    today = date.today()
    deadline = today + timedelta(days=days)
    items: list[AlertItem] = []

    # ── ビザ期限 ────────────────────────────────────────────────────────
    if alert_type is None or alert_type == "VISA_EXPIRY":
        visa_result = await db.execute(
            select(VisaInfo, Employee)
            .join(Employee, VisaInfo.employee_id == Employee.id)
            .where(
                VisaInfo.expires_at != None,
                VisaInfo.expires_at >= today,
                VisaInfo.expires_at <= deadline,
                Employee.is_active == True,
            )
            .order_by(VisaInfo.expires_at)
        )
        for visa, emp in visa_result.all():
            items.append(
                AlertItem(
                    type="VISA_EXPIRY",
                    employee=AlertEmployeeEmbed(
                        id=emp.id,
                        name_ja=emp.name_ja,
                        employee_number=emp.employee_number,
                    ),
                    expires_at=visa.expires_at,
                    days_remaining=(visa.expires_at - today).days,
                )
            )

    # ── 資格期限（APPROVED のみ）────────────────────────────────────────
    if alert_type is None or alert_type == "CERT_EXPIRY":
        cert_result = await db.execute(
            select(EmployeeCertification, Employee)
            .join(Employee, EmployeeCertification.employee_id == Employee.id)
            .where(
                EmployeeCertification.expires_at != None,
                EmployeeCertification.expires_at >= today,
                EmployeeCertification.expires_at <= deadline,
                EmployeeCertification.status == "APPROVED",
                Employee.is_active == True,
            )
            .order_by(EmployeeCertification.expires_at)
        )
        for cert, emp in cert_result.all():
            items.append(
                AlertItem(
                    type="CERT_EXPIRY",
                    employee=AlertEmployeeEmbed(
                        id=emp.id,
                        name_ja=emp.name_ja,
                        employee_number=emp.employee_number,
                    ),
                    expires_at=cert.expires_at,
                    days_remaining=(cert.expires_at - today).days,
                )
            )

    # 期限日順にソート
    items.sort(key=lambda x: x.expires_at)
    return AlertListResponse(items=items)


async def get_skill_heatmap(db: AsyncSession) -> SkillHeatmapResponse:
    """全社スキルヒートマップ（カテゴリ × 承認済みレベル × 人数）を返す。"""
    result = await db.execute(
        select(
            SkillCategory.name_ja,
            EmployeeSkill.approved_level,
            func.count(distinct(EmployeeSkill.employee_id)).label("cnt"),
        )
        .join(Skill, EmployeeSkill.skill_id == Skill.id)
        .join(SkillCategory, Skill.category_id == SkillCategory.id)
        .where(
            EmployeeSkill.status == "APPROVED",
            EmployeeSkill.approved_level != None,  # noqa: E711
        )
        .group_by(SkillCategory.name_ja, SkillCategory.sort_order, EmployeeSkill.approved_level)
        .order_by(SkillCategory.sort_order, EmployeeSkill.approved_level)
    )
    rows = result.all()

    # カテゴリ一覧（order_by の順を保持、重複なし）
    seen: set[str] = set()
    categories: list[str] = []
    for row in rows:
        if row[0] not in seen:
            categories.append(row[0])
            seen.add(row[0])

    items = [
        SkillHeatmapCell(category=row[0], level=row[1], count=row[2])
        for row in rows
    ]
    return SkillHeatmapResponse(categories=categories, items=items)


async def get_headcount_trend(db: AsyncSession, months: int = 12) -> HeadcountTrendResponse:
    """過去 N ヶ月の入退社人数推移を返す。"""
    today = date.today()
    result_months: list[HeadcountTrendItem] = []

    for i in range(months - 1, -1, -1):
        target_start = _add_months(date(today.year, today.month, 1), -i)
        _, last = _month_bounds(target_start.year, target_start.month)
        first = target_start
        month_label = first.strftime("%Y-%m")

        joined_result = await db.execute(
            select(func.count(Employee.id)).where(
                Employee.joined_at >= first,
                Employee.joined_at <= last,
            )
        )
        joined = joined_result.scalar() or 0

        left_result = await db.execute(
            select(func.count(Employee.id)).where(
                Employee.left_at != None,  # noqa: E711
                Employee.left_at >= first,
                Employee.left_at <= last,
            )
        )
        left_count = left_result.scalar() or 0

        result_months.append(
            HeadcountTrendItem(month=month_label, joined=joined, left=left_count)
        )

    return HeadcountTrendResponse(months=result_months)


async def get_location_distribution(db: AsyncSession) -> LocationDistributionResponse:
    """拠点別在籍人数を返す。"""
    result = await db.execute(
        select(Employee.office_location, func.count(Employee.id).label("cnt"))
        .where(Employee.is_active == True)  # noqa: E712
        .group_by(Employee.office_location)
        .order_by(func.count(Employee.id).desc())
    )
    items = [
        DistributionItem(label=row[0], count=row[1])
        for row in result.all()
    ]
    return LocationDistributionResponse(items=items)
