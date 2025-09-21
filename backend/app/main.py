#!/usr/bin/env python3
"""
FastAPI Backend for Obsidian AI Assistant
Modern web-based replacement for the tkinter GUI
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .api import vaults, search, backlinks, ai, chat
from .core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    print("🚀 Starting Obsidian AI Assistant API")
    
    # Startup
    yield
    
    # Shutdown
    print("👋 Shutting down Obsidian AI Assistant API")


def create_app() -> FastAPI:
    """Create FastAPI application"""
    
    app = FastAPI(
        title="Obsidian AI Assistant",
        description="Modern web-based interface for Obsidian vault analysis with AI capabilities",
        version="2.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API routes
    app.include_router(vaults.router, prefix="/api/vaults", tags=["vaults"])
    app.include_router(search.router, prefix="/api/search", tags=["search"])
    app.include_router(backlinks.router, prefix="/api/backlinks", tags=["backlinks"])
    app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

    # Health check
    @app.get("/api/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": "2.0.0",
            "ai_available": settings.AI_ENABLED,
            "openai_available": settings.OPENAI_ENABLED
        }

    # Serve React frontend in production
    frontend_path = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if frontend_path.exists():
        app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )