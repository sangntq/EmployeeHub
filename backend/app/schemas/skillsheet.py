"""
スキルシート出力用 Pydantic スキーマ
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator


class ExportRequest(BaseModel):
    employee_ids: list[str]                             # 1〜20名
    format: Literal["xlsx", "pdf"] = "xlsx"
    output_style: Literal["combined", "zip"] = "combined"
    filename_prefix: str = "skillsheet"
    include_salary: bool = False

    @field_validator("employee_ids")
    @classmethod
    def at_least_one(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("employee_ids must not be empty")
        return v


class ExportResponse(BaseModel):
    download_url: str       # /api/v1/skillsheet/download/{token}
    expires_at: datetime    # now + 1h
    filename: str
