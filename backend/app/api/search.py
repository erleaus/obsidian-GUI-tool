"""
Search API endpoints
"""

from fastapi import APIRouter, HTTPException
from ..models.schemas import SearchRequest, SearchResponse
from ..core.search_service import search_service

router = APIRouter()


@router.post("/", response_model=SearchResponse)
async def search_vault(request: SearchRequest):
    """Perform text search in vault"""
    try:
        results = await search_service.search_vault(
            vault_path=request.vault_path,
            query=request.query,
            case_sensitive=request.case_sensitive,
            whole_word=request.whole_word,
            use_regex=request.use_regex,
            max_results=request.max_results
        )
        
        return SearchResponse(**results)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )