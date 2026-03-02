from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.employee import Employee

bearer_scheme = HTTPBearer()


async def get_current_employee(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Employee:
    """JWT を検証して現在のログインユーザー（Employee）を返す。"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効です",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(credentials.credentials)
        employee_id: str = payload.get("sub", "")
        if not employee_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(Employee).where(Employee.id == employee_id, Employee.is_active == True))
    employee = result.scalar_one_or_none()
    if employee is None:
        raise credentials_exception
    return employee


def require_role(*roles: str):
    """指定ロールのいずれかを持つユーザーのみ許可する依存関数を返す。"""
    async def _check(current: Employee = Depends(get_current_employee)) -> Employee:
        if current.system_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"この操作には {' / '.join(roles)} ロールが必要です",
            )
        return current
    return _check
