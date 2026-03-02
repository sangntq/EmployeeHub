from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.models.employee import Employee
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_refresh_token
from app.core.config import settings
from jose import JWTError
import httpx


async def login_with_email(db: AsyncSession, email: str, password: str) -> tuple[Employee, str, str]:
    """メール＋パスワードで認証し、(employee, access_token, refresh_token) を返す。"""
    # ユーザー検索
    result = await db.execute(select(User).where(User.email == email, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="メールアドレスまたはパスワードが正しくありません")
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="メールアドレスまたはパスワードが正しくありません")

    employee = await _get_employee_by_user(db, user.id)
    return employee, *_issue_tokens(employee)


async def login_with_google(db: AsyncSession, id_token: str) -> tuple[Employee, str, str]:
    """Google id_token を検証し、(employee, access_token, refresh_token) を返す。"""
    if not settings.google_auth_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Google認証は設定されていません")

    # Google公開エンドポイントでトークン検証
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Googleトークンが無効です")

    info = resp.json()
    if info.get("aud") != settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Googleトークンの発行先が一致しません")

    google_id = info["sub"]
    email = info.get("email", "")

    # 既存ユーザー検索 or 新規作成
    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()
    if not user:
        # メールで既存ユーザーを検索してGoogleアカウントを紐付ける
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            user.google_id = google_id
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="このGoogleアカウントは登録されていません。管理者にお問い合わせください",
            )
        await db.commit()

    employee = await _get_employee_by_user(db, user.id)
    return employee, *_issue_tokens(employee)


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> tuple[Employee, str, str]:
    """refresh_token を検証して新しいトークンペアを返す。"""
    try:
        payload = decode_refresh_token(refresh_token)
        employee_id: str = payload.get("sub", "")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="リフレッシュトークンが無効です")

    result = await db.execute(select(Employee).where(Employee.id == employee_id, Employee.is_active == True))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="ユーザーが見つかりません")

    access, refresh_new = _issue_tokens(employee)
    return employee, access, refresh_new


# ── private helpers ────────────────────────────────────────────────────────

def _issue_tokens(employee: Employee) -> tuple[str, str]:
    extra = {"role": employee.system_role}
    access = create_access_token(subject=employee.id, extra=extra)
    refresh = create_refresh_token(subject=employee.id)
    return access, refresh


async def _get_employee_by_user(db: AsyncSession, user_id: str) -> Employee:
    result = await db.execute(
        select(Employee).where(Employee.user_id == user_id, Employee.is_active == True)
    )
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="社員レコードが見つかりません")
    return employee
