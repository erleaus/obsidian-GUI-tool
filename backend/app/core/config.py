"""
Configuration settings for the Obsidian AI Assistant backend
"""

import os
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App Configuration
    DEBUG: bool = True
    API_VERSION: str = "v1"
    PROJECT_NAME: str = "Obsidian AI Assistant"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",
        "http://localhost:8000",  # FastAPI dev server
        "http://127.0.0.1:8000",
    ]
    
    # AI Features - Feature Flags
    AI_ENABLED: bool = True
    OPENAI_ENABLED: bool = False
    
    # AI Configuration
    AI_MODEL_NAME: str = "all-MiniLM-L6-v2"
    MAX_CONTEXT_CHUNKS: int = 10
    SIMILARITY_THRESHOLD: float = 0.3
    MAX_RESULTS: int = 50
    
    # OpenAI Configuration (optional)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 2000
    
    # MongoDB (optional for chat history)
    MONGODB_URL: Optional[str] = None
    MONGODB_DB_NAME: str = "obsidian_ai"
    
    # File Upload Limits
    MAX_VAULT_SIZE_MB: int = 1000
    MAX_FILES_TO_INDEX: int = 10000
    
    # Cache Configuration
    CACHE_TTL_SECONDS: int = 3600  # 1 hour
    AI_CACHE_ENABLED: bool = True
    
    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Auto-detect AI availability
        try:
            import sentence_transformers
            self.AI_ENABLED = True
        except ImportError:
            self.AI_ENABLED = False
            
        # Auto-detect OpenAI availability
        if self.OPENAI_API_KEY:
            try:
                import openai
                self.OPENAI_ENABLED = True
            except ImportError:
                self.OPENAI_ENABLED = False
        else:
            self.OPENAI_ENABLED = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()