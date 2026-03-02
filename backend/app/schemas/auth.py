from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str  # EmailStr は .local ドメインを拒否するため str を使用
    password: str


class GoogleLoginRequest(BaseModel):
    id_token: str


class RefreshRequest(BaseModel):
    refresh_token: str


class EmployeeEmbed(BaseModel):
    """トークンレスポンスに埋め込む社員情報"""
    id: str
    employee_number: str
    name_ja: str
    name_en: str | None = None
    system_role: str
    avatar_url: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒
    employee: EmployeeEmbed


class CurrentUserResponse(BaseModel):
    id: str
    email: str
    name: str
    employee_id: str
    system_role: str
    avatar_url: str | None = None
