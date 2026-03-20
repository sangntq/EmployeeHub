from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.routers import auth, employees, departments, skills, certifications, approvals, work_statuses, projects, search, dashboard, skillsheet, notifications, availability, skillmatrix, certmatrix
from app.services.scheduler_service import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # アバター保存ディレクトリを確保
    Path("uploads").mkdir(exist_ok=True)
    # エクスポートファイル保存ディレクトリを確保
    Path("exports").mkdir(exist_ok=True)
    # スケジューラー起動
    scheduler = start_scheduler()
    yield
    # スケジューラー停止
    stop_scheduler(scheduler)


app = FastAPI(
    title="EmployeeHub API",
    description="IT人材管理プラットフォーム API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# アップロード・エクスポート用ディレクトリを自動作成
import os
os.makedirs("uploads", exist_ok=True)
os.makedirs("exports", exist_ok=True)

# アップロードファイルを静的配信
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# エクスポートファイルを静的配信
app.mount("/exports", StaticFiles(directory="exports"), name="exports")

# Phase 1 ルーター
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(employees.router, prefix="/api/v1/employees", tags=["employees"])
app.include_router(departments.router, prefix="/api/v1/departments", tags=["departments"])

# Phase 2 ルーター
app.include_router(skills.router, prefix="/api/v1", tags=["skills"])
app.include_router(certifications.router, prefix="/api/v1", tags=["certifications"])
app.include_router(approvals.router, prefix="/api/v1", tags=["approvals"])

# Phase 3 ルーター
app.include_router(work_statuses.router, prefix="/api/v1", tags=["work-status"])
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])

# Phase 4 ルーター
app.include_router(search.router, prefix="/api/v1", tags=["search"])

# Phase 6 ルーター
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"])

# Phase 7 ルーター
app.include_router(skillsheet.router, prefix="/api/v1/skillsheet", tags=["skillsheet"])

# Phase 8 ルーター
app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])

# 追加ルーター（稼働可否 / スキルマトリクス）
app.include_router(availability.router, prefix="/api/v1", tags=["availability"])
app.include_router(skillmatrix.router, prefix="/api/v1", tags=["skillmatrix"])
app.include_router(certmatrix.router, prefix="/api/v1", tags=["certmatrix"])


@app.get("/health", tags=["system"])
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "ok",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "features": {
            "google_auth": settings.google_auth_enabled,
            "ai_search": settings.ai_search_enabled,
        },
    }


@app.get("/", tags=["system"])
async def root():
    return {"message": "EmployeeHub API", "docs": "/docs"}
