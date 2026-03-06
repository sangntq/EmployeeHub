from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.employee import Employee
from app.models.department import Department
from app.models.work_status import Assignment
from app.models.project import VisaInfo
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


async def list_employees(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    department_id: str | None = None,
    system_role: str | None = None,
    is_active: bool = True,
    q: str | None = None,
) -> tuple[list[Employee], int]:
    """社員一覧を返す。(items, total) のタプル。"""
    query = (
        select(Employee)
        .options(selectinload(Employee.department))
        .where(Employee.is_active == is_active)
    )
    count_query = select(func.count()).select_from(Employee).where(Employee.is_active == is_active)

    if department_id:
        query = query.where(Employee.department_id == department_id)
        count_query = count_query.where(Employee.department_id == department_id)
    if system_role:
        query = query.where(Employee.system_role == system_role)
        count_query = count_query.where(Employee.system_role == system_role)
    if q:
        like = f"%{q}%"
        query = query.where(
            Employee.name_ja.ilike(like)
            | Employee.name_en.ilike(like)
            | Employee.employee_number.ilike(like)
        )
        count_query = count_query.where(
            Employee.name_ja.ilike(like)
            | Employee.name_en.ilike(like)
            | Employee.employee_number.ilike(like)
        )

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = query.order_by(Employee.employee_number).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    employees = list(result.scalars().all())

    # workload_percent と is_mobilizable を一括計算して付与
    if employees:
        emp_ids = [e.id for e in employees]
        today = date.today()

        # 稼働率（workload_percent）: アクティブなアサインの allocation_percent 合計
        workload_rows = await db.execute(
            select(Assignment.employee_id, func.sum(Assignment.allocation_percent).label("total"))
            .where(
                Assignment.employee_id.in_(emp_ids),
                Assignment.is_active.is_(True),
                Assignment.started_at <= today,
                or_(Assignment.ends_at.is_(None), Assignment.ends_at >= today),
            )
            .group_by(Assignment.employee_id)
        )
        workload_map = {row.employee_id: int(row.total) for row in workload_rows}

        # モバイル可能者: HANOI/HCMC かつビザ有効期限 > 今日
        mobile_rows = await db.execute(
            select(VisaInfo.employee_id).where(
                VisaInfo.employee_id.in_(emp_ids),
                VisaInfo.expires_at > today,
            )
        )
        mobile_ids = {row.employee_id for row in mobile_rows}

        for emp in employees:
            emp.workload_percent = workload_map.get(emp.id)
            emp.is_mobilizable = emp.office_location in ("HANOI", "HCMC") and emp.id in mobile_ids

    return employees, total


async def get_employee(db: AsyncSession, employee_id: str) -> Employee:
    result = await db.execute(
        select(Employee)
        .options(selectinload(Employee.department))
        .where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="社員が見つかりません")
    return employee


async def create_employee(db: AsyncSession, data: EmployeeCreate) -> Employee:
    # 社員番号の重複チェック
    exists = await db.execute(select(Employee).where(Employee.employee_number == data.employee_number))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="この社員番号はすでに使用されています")

    employee = Employee(**data.model_dump())
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    # department をロードして返す
    return await get_employee(db, employee.id)


async def update_employee(db: AsyncSession, employee_id: str, data: EmployeeUpdate) -> Employee:
    employee = await get_employee(db, employee_id)
    update_data = data.model_dump(exclude_unset=True)

    # is_active が True → False に変更された場合、left_at を自動設定
    if update_data.get("is_active") is False and employee.is_active is True:
        if employee.left_at is None and "left_at" not in update_data:
            update_data["left_at"] = date.today()

    for field, value in update_data.items():
        setattr(employee, field, value)
    await db.commit()
    await db.refresh(employee)
    return await get_employee(db, employee.id)


async def deactivate_employee(db: AsyncSession, employee_id: str) -> None:
    """社員を論理削除（無効化）する。"""
    employee = await get_employee(db, employee_id)
    if not employee.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="この社員はすでに無効化されています")
    employee.is_active = False
    if employee.left_at is None:
        employee.left_at = date.today()
    await db.commit()


async def update_avatar(db: AsyncSession, employee_id: str, avatar_url: str) -> Employee:
    employee = await get_employee(db, employee_id)
    employee.avatar_url = avatar_url
    await db.commit()
    return employee
