from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # アプリケーション設定
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev-secret-key-please-change"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # データベース
    DATABASE_URL: str = "postgresql+asyncpg://employeehub:employeehub@db:5432/employeehub_db"
    DATABASE_URL_SYNC: str = "postgresql://employeehub:employeehub@db:5432/employeehub_db"

    # CORS（カンマ区切り文字列またはJSON配列どちらでも可）
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        v = self.CORS_ORIGINS.strip()
        try:
            parsed = json.loads(v)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass
        return [o.strip() for o in v.split(",") if o.strip()]

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # ファイルストレージ
    S3_ENDPOINT_URL: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_BUCKET_NAME: str = "employeehub-files"

    # メール
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # AI検索
    ANTHROPIC_API_KEY: str = ""

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def ai_search_enabled(self) -> bool:
        return bool(self.ANTHROPIC_API_KEY)

    @property
    def google_auth_enabled(self) -> bool:
        return bool(self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET)


settings = Settings()
