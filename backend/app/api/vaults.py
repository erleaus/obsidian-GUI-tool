"""
Vault management API endpoints
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime

from ..models.schemas import (
    VaultInfo, VaultStats, VaultValidationRequest, VaultOpenRequest,
    ErrorResponse
)
from ..core.vault_utils import vault_manager
from ..core.config import settings

router = APIRouter()


@router.get("/autodetect", response_model=List[VaultInfo])
async def autodetect_vaults():
    """Auto-detect Obsidian vaults in common locations"""
    try:
        detected_paths = vault_manager.auto_detect_vaults()
        
        vaults = []
        for path in detected_paths:
            vault_name = path.split('/')[-1] if '/' in path else path.split('\\')[-1]
            vaults.append(VaultInfo(path=path, name=vault_name))
        
        return vaults
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect vaults: {str(e)}"
        )


@router.post("/validate", response_model=VaultStats)
async def validate_vault(request: VaultValidationRequest):
    """Validate a vault path and get statistics"""
    try:
        stats = await vault_manager.get_vault_stats(request.path)
        
        return VaultStats(
            path=stats.path,
            name=stats.name,
            total_files=stats.total_files,
            markdown_files=stats.markdown_files,
            total_size_mb=stats.total_size_bytes / 1024 / 1024,
            last_modified=stats.last_modified,
            is_valid=stats.is_valid,
            error=stats.error
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate vault: {str(e)}"
        )


@router.post("/open")
async def open_vault(request: VaultOpenRequest):
    """Open Obsidian application with optional vault"""
    try:
        success, message = await vault_manager.open_obsidian(request.path)
        
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(
                status_code=400,
                detail=message
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to open Obsidian: {str(e)}"
        )