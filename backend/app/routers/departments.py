from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_employee, require_role
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse

router = APIRouter()


@router.get("", response_model=list[DepartmentResponse])
async def list_departments(
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_employee),
):
    result = await db.execute(select(Department).where(Department.is_active == True).order_by(Department.sort_order))
    return list(result.scalars().all())


@router.post("", response_model=DepartmentResponse, status_code=201)
async def create_department(
    body: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_role("admin")),
):
    dept = Department(**body.model_dump())
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept


@router.put("/{dept_id}", response_model=DepartmentResponse)
async def update_department(
    dept_id: str,
    body: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_role("admin")),
):
    from fastapi import HTTPException, status as http_status
    result = await db.execute(select(Department).where(Department.id == dept_id))
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="部署が見つかりません")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(dept, field, value)
    await db.commit()
    await db.refresh(dept)
    return dept
