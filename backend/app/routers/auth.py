from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.core.deps import get_current_employee
from app.schemas.auth import LoginRequest, GoogleLoginRequest, RefreshRequest, TokenResponse, CurrentUserResponse, EmployeeEmbed
from app.services import auth_service
from app.models.employee import Employee

router = APIRouter()


def _make_token_response(employee, access: str, refresh: str) -> TokenResponse:
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        employee=EmployeeEmbed(
            id=employee.id,
            employee_number=employee.employee_number,
            name_ja=employee.name_ja,
            name_en=employee.name_en,
            system_role=employee.system_role,
            avatar_url=employee.avatar_url,
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """メール＋パスワードでログイン"""
    employee, access, refresh = await auth_service.login_with_email(db, body.email, body.password)
    return _make_token_response(employee, access, refresh)


@router.post("/google", response_model=TokenResponse)
async def google_login(body: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    """Google id_token でログイン"""
    employee, access, refresh = await auth_service.login_with_google(db, body.id_token)
    return _make_token_response(employee, access, refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """アクセストークンを更新"""
    employee, access, refresh_new = await auth_service.refresh_access_token(db, body.refresh_token)
    return _make_token_response(employee, access, refresh_new)


@router.delete("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current: Employee = Depends(get_current_employee)):
    """ログアウト（クライアント側でトークンを削除する）"""
    # サーバーサイドでのトークン無効化は Phase 9 で実装
    return None


@router.get("/me", response_model=CurrentUserResponse)
async def me(current: Employee = Depends(get_current_employee)):
    """現在のログインユーザー情報を返す"""
    return CurrentUserResponse(
        id=current.user_id or "",
        email=current.email,
        name=current.name_ja,
        employee_id=current.id,
        system_role=current.system_role,
        avatar_url=current.avatar_url,
    )
