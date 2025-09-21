"""
AI features API endpoints
"""

from fastapi import APIRouter, HTTPException
from ..models.schemas import AISearchRequest, AISearchResponse, AIIndexRequest
from ..core.config import settings

router = APIRouter()


@router.post("/search", response_model=AISearchResponse)
async def ai_search(request: AISearchRequest):
    """Perform AI semantic search"""
    if not settings.AI_ENABLED:
        raise HTTPException(
            status_code=501,
            detail="AI features not available. Install sentence-transformers to enable."
        )
    
    # Placeholder - will implement full AI search
    raise HTTPException(
        status_code=501,
        detail="AI search not yet implemented"
    )


@router.post("/index")
async def build_ai_index(request: AIIndexRequest):
    """Build AI semantic index"""
    if not settings.AI_ENABLED:
        raise HTTPException(
            status_code=501,
            detail="AI features not available"
        )
    
    raise HTTPException(
        status_code=501,
        detail="AI indexing not yet implemented"
    )