"""稼働可否スケジュールサービス"""
import calendar
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.models.employee import Employee
from app.models.work_status import Assignment
from app.models.project import Project
from app.schemas.employee import EmployeeListItem
from app.schemas.availability import AvailabilityMonth, EmployeeAvailability, AvailabilityResponse


def _build_month_range(months: int, offset_months: int) -> list[str]:
    """今月 + offset_months から months ヶ月分の "YYYY-MM" リストを生成する。"""
    today = date.today()
    # オフセット込みの開始月を計算
    start_year = today.year
    start_month = today.month + offset_months
    # 月のオーバーフロー処理（relativedelta 不使用）
    while start_month > 12:
        start_month -= 12
        start_year += 1
    while start_month < 1:
        start_month += 12
        start_year -= 1

    result = []
    y, m = start_year, start_month
    for _ in range(months):
        result.append(f"{y:04d}-{m:02d}")
        m += 1
        if m > 12:
            m = 1
            y += 1
    return result


def _month_range_dates(month_str: str) -> tuple[date, date]:
    """'YYYY-MM' から (月初, 月末) の date タプルを返す。"""
    y, m = int(month_str[:4]), int(month_str[5:7])
    last_day = calendar.monthrange(y, m)[1]
    return date(y, m, 1), date(y, m, last_day)


async def get_availability(
    db: AsyncSession,
    months: int = 6,
    offset_months: int = 0,
    location: str | None = None,
    search: str | None = None,
    status_filter: str | None = None,
) -> AvailabilityResponse:
    """稼働可否カレンダーを返す。

    Args:
        db: DBセッション
        months: 表示月数（デフォルト 6）
        offset_months: 今月からのオフセット（デフォルト 0）
        location: office_location フィルター
        search: 社員名・番号の部分一致検索
        status_filter: FREE | PARTIAL | BUSY — 1ヶ月以上一致する社員のみ返す
    """
    month_list = _build_month_range(months, offset_months)

    # 月範囲全体の開始日・終了日
    range_start = _month_range_dates(month_list[0])[0]
    range_end = _month_range_dates(month_list[-1])[1]

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
    emp_result = await db.execute(emp_query)
    employees = list(emp_result.scalars().all())

    if not employees:
        return AvailabilityResponse(months_header=month_list, items=[])

    employee_ids = [e.id for e in employees]

    # ── 期間内のアサイン一括取得 ────────────────────────────────────────────
    assign_query = (
        select(Assignment, Project.name.label("project_name"))
        .join(Project, Assignment.project_id == Project.id)
        .where(
            Assignment.employee_id.in_(employee_ids),
            Assignment.is_active == True,
            Assignment.started_at <= range_end,
            or_(
                Assignment.ends_at == None,
                Assignment.ends_at >= range_start,
            ),
        )
    )
    assign_result = await db.execute(assign_query)
    rows = assign_result.all()

    # emp_id -> list of (started_at, ends_at, allocation_percent, project_name)
    assign_map: dict[str, list[tuple]] = {eid: [] for eid in employee_ids}
    for row in rows:
        assignment: Assignment = row[0]
        project_name: str = row[1]
        assign_map[assignment.employee_id].append(
            (
                assignment.started_at,
                assignment.ends_at,
                assignment.allocation_percent,
                project_name,
            )
        )

    # ── 社員×月ごとに稼働状況を計算 ────────────────────────────────────────
    items: list[EmployeeAvailability] = []

    for emp in employees:
        month_entries: list[AvailabilityMonth] = []
        for month_str in month_list:
            m_start, m_end = _month_range_dates(month_str)
            total_alloc = 0
            primary_project: str | None = None
            primary_alloc = 0

            for (a_start, a_end, alloc, pname) in assign_map[emp.id]:
                # アサイン期間がこの月と重なるか判定
                a_end_eff = a_end if a_end is not None else date(9999, 12, 31)
                if a_start <= m_end and a_end_eff >= m_start:
                    total_alloc += alloc
                    if alloc > primary_alloc:
                        primary_alloc = alloc
                        primary_project = pname

            if total_alloc == 0:
                status = "FREE"
            elif total_alloc >= 100:
                status = "BUSY"
            else:
                status = "PARTIAL"

            month_entries.append(
                AvailabilityMonth(
                    month=month_str,
                    status=status,
                    allocation=min(total_alloc, 100),
                    project_name=primary_project if status != "FREE" else None,
                )
            )

        # status_filter が指定されている場合、該当月が存在しなければスキップ
        if status_filter:
            if not any(me.status == status_filter for me in month_entries):
                continue

        emp_item = EmployeeListItem.model_validate(emp)
        items.append(EmployeeAvailability(employee=emp_item, months=month_entries))

    return AvailabilityResponse(months_header=month_list, items=items)
