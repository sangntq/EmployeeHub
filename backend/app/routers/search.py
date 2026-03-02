"""
検索エンドポイント

- POST /search/filter     : フィルター検索（sales / manager以上）
- GET  /search/saved      : 保存済み検索一覧（本人のみ）
- POST /search/saved      : 検索条件を保存
- DELETE /search/saved/{id} : 保存済み検索を削除
- POST /search/ai-parse   : AI自然言語解析（ANTHROPIC_API_KEY 必要）
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.models.employee import Employee
from app.schemas.search import (
    SearchFilter, SearchResponse,
    SavedSearchCreate, SavedSearchResponse,
    AIParseRequest, AIParseResponse,
)
from app.services import search_service, ai_parser

router = APIRouter()

# sales, manager, department_head, director, admin が検索可能
SEARCH_ROLES = ("sales", "manager", "department_head", "director", "admin")


@router.post("/search/filter", response_model=SearchResponse)
async def filter_search(
    body: SearchFilter,
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(require_role(*SEARCH_ROLES)),
):
    return await search_service.search_employees(db, body, current.id)


@router.get("/search/saved", response_model=list[SavedSearchResponse])
async def get_saved_searches(
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(require_role(*SEARCH_ROLES)),
):
    return await search_service.list_saved_searches(db, current.id)


@router.post("/search/saved", response_model=SavedSearchResponse, status_code=201)
async def create_saved_search(
    body: SavedSearchCreate,
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(require_role(*SEARCH_ROLES)),
):
    return await search_service.save_search(db, body, current.id)


@router.delete("/search/saved/{search_id}", status_code=204)
async def delete_saved_search(
    search_id: str,
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(require_role(*SEARCH_ROLES)),
):
    await search_service.delete_saved_search(db, search_id, current.id)


@router.post("/search/ai-parse", response_model=AIParseResponse)
async def ai_parse_search(
    body: AIParseRequest,
    db: AsyncSession = Depends(get_db),
    current: Employee = Depends(require_role(*SEARCH_ROLES)),
):
    """自然言語テキストをAIで解析し、構造化された検索条件を返す。"""
    return await ai_parser.parse_natural_language(body.text, db, current.id)
