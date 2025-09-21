"""
Conversational AI chat API endpoints
"""

from fastapi import APIRouter, HTTPException
from ..models.schemas import ChatRequest, ChatResponse
from ..core.config import settings

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat with AI about vault content"""
    if not settings.OPENAI_ENABLED:
        raise HTTPException(
            status_code=501,
            detail="Chat features not available. Configure OpenAI API key to enable."
        )
    
    # Placeholder - will implement full chat functionality
    raise HTTPException(
        status_code=501,
        detail="Chat functionality not yet implemented"
    )