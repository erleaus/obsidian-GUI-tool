"""
Vault utilities - Core functionality for Obsidian vault operations
Ported from the original tkinter GUI implementation
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import asyncio
from datetime import datetime


class VaultStats:
    """Statistics for an Obsidian vault"""
    
    def __init__(
        self,
        path: str,
        name: str,
        total_files: int,
        markdown_files: int,
        total_size_bytes: int,
        last_modified: datetime,
        is_valid: bool = True,
        error: Optional[str] = None
    ):
        self.path = path
        self.name = name
        self.total_files = total_files
        self.markdown_files = markdown_files
        self.total_size_bytes = total_size_bytes
        self.last_modified = last_modified
        self.is_valid = is_valid
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "path": self.path,
            "name": self.name,
            "total_files": self.total_files,
            "markdown_files": self.markdown_files,
            "total_size_mb": round(self.total_size_bytes / 1024 / 1024, 2),
            "last_modified": self.last_modified.isoformat(),
            "is_valid": self.is_valid,
            "error": self.error
        }


class VaultManager:
    """Manages Obsidian vault operations"""
    
    def __init__(self):
        self.common_paths = [
            "~/Documents/Obsidian",
            "~/Obsidian", 
            "~/Documents",
            "~/Desktop",
            "~/Downloads",
        ]
    
    def is_obsidian_vault(self, path: str) -> bool:
        """Check if directory is an Obsidian vault"""
        if not path or not os.path.exists(path):
            return False
        return os.path.exists(os.path.join(path, ".obsidian"))
    
    def find_vaults_in_directory(self, directory: str) -> List[str]:
        """Find Obsidian vaults in a directory (non-recursive)"""
        vaults = []
        try:
            if not os.path.exists(directory) or not os.path.isdir(directory):
                return vaults
                
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path) and self.is_obsidian_vault(item_path):
                    vaults.append(item_path)
        except PermissionError:
            pass
        except Exception:
            pass
        
        return sorted(vaults)
    
    def auto_detect_vaults(self) -> List[str]:
        """Auto-detect Obsidian vaults in common locations"""
        detected_vaults = []
        
        for path_pattern in self.common_paths:
            expanded_path = os.path.expanduser(path_pattern)
            vaults_in_path = self.find_vaults_in_directory(expanded_path)
            detected_vaults.extend(vaults_in_path)
        
        # Remove duplicates while preserving order
        unique_vaults = []
        seen = set()
        for vault in detected_vaults:
            canonical_path = os.path.realpath(vault)
            if canonical_path not in seen:
                unique_vaults.append(vault)
                seen.add(canonical_path)
        
        return unique_vaults
    
    async def get_vault_stats(self, vault_path: str) -> VaultStats:
        """Get detailed statistics for an Obsidian vault"""
        vault_path = os.path.expanduser(vault_path)
        vault_name = Path(vault_path).name
        
        try:
            if not os.path.exists(vault_path):
                return VaultStats(
                    path=vault_path,
                    name=vault_name,
                    total_files=0,
                    markdown_files=0,
                    total_size_bytes=0,
                    last_modified=datetime.now(),
                    is_valid=False,
                    error="Path does not exist"
                )
            
            if not self.is_obsidian_vault(vault_path):
                return VaultStats(
                    path=vault_path,
                    name=vault_name,
                    total_files=0,
                    markdown_files=0,
                    total_size_bytes=0,
                    last_modified=datetime.now(),
                    is_valid=False,
                    error="Not an Obsidian vault (missing .obsidian folder)"
                )
            
            # Count files and calculate size
            total_files = 0
            markdown_files = 0
            total_size = 0
            max_mod_time = 0
            
            vault_pathlib = Path(vault_path)
            
            # Use pathlib for better performance
            all_files = list(vault_pathlib.rglob("*"))
            
            for file_path in all_files:
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        total_files += 1
                        total_size += stat.st_size
                        max_mod_time = max(max_mod_time, stat.st_mtime)
                        
                        if file_path.suffix.lower() == '.md':
                            markdown_files += 1
                    except (OSError, PermissionError):
                        continue
            
            last_modified = datetime.fromtimestamp(max_mod_time) if max_mod_time > 0 else datetime.now()
            
            return VaultStats(
                path=vault_path,
                name=vault_name,
                total_files=total_files,
                markdown_files=markdown_files,
                total_size_bytes=total_size,
                last_modified=last_modified,
                is_valid=True
            )
            
        except Exception as e:
            return VaultStats(
                path=vault_path,
                name=vault_name,
                total_files=0,
                markdown_files=0,
                total_size_bytes=0,
                last_modified=datetime.now(),
                is_valid=False,
                error=str(e)
            )
    
    def get_markdown_files(self, vault_path: str) -> List[Path]:
        """Get all markdown files in the vault"""
        try:
            vault_pathlib = Path(vault_path)
            if not vault_pathlib.exists():
                return []
            
            return list(vault_pathlib.rglob("*.md"))
        except Exception:
            return []
    
    async def open_obsidian(self, vault_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Open Obsidian application
        Returns: (success: bool, message: str)
        """
        try:
            import subprocess
            import platform
            
            system = platform.system()
            
            if vault_path and os.path.exists(vault_path):
                if system == "Darwin":  # macOS
                    result = subprocess.run(['open', '-a', 'Obsidian', vault_path], 
                                          capture_output=True, text=True)
                elif system == "Windows":
                    result = subprocess.run(['start', 'obsidian:', vault_path], 
                                          shell=True, capture_output=True, text=True)
                else:  # Linux
                    result = subprocess.run(['obsidian', vault_path], 
                                          capture_output=True, text=True)
                
                if result.returncode == 0:
                    return True, f"Opened Obsidian with vault: {Path(vault_path).name}"
                else:
                    return False, f"Failed to open Obsidian: {result.stderr}"
            else:
                # Open Obsidian without specific vault
                if system == "Darwin":  # macOS
                    result = subprocess.run(['open', '-a', 'Obsidian'], 
                                          capture_output=True, text=True)
                elif system == "Windows":
                    result = subprocess.run(['start', 'obsidian:'], 
                                          shell=True, capture_output=True, text=True)
                else:  # Linux
                    result = subprocess.run(['obsidian'], 
                                          capture_output=True, text=True)
                
                if result.returncode == 0:
                    return True, "Opened Obsidian"
                else:
                    return False, f"Failed to open Obsidian: {result.stderr}"
                    
        except FileNotFoundError:
            return False, "Obsidian application not found. Make sure it's installed."
        except Exception as e:
            return False, f"Error opening Obsidian: {str(e)}"


# Global vault manager instance
vault_manager = VaultManager()