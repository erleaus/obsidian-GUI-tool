"""
Search service - Core text search functionality
Ported from the original tkinter implementation
"""

import re
import time
from pathlib import Path
from typing import List, Dict, Any, Generator, Tuple, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .vault_utils import vault_manager


class SearchMatch:
    """Represents a single search match"""
    
    def __init__(self, line_number: int, line_content: str, matches_count: int):
        self.line_number = line_number
        self.line_content = line_content
        self.matches_count = matches_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "line_number": self.line_number,
            "line_content": self.line_content,
            "matches_count": self.matches_count
        }


class SearchFileResult:
    """Search results for a single file"""
    
    def __init__(self, file_path: Path, vault_path: str):
        self.file_path = file_path
        self.vault_path = vault_path
        self.matches: List[SearchMatch] = []
        self.total_matches = 0
    
    @property
    def relative_path(self) -> str:
        try:
            return str(self.file_path.relative_to(self.vault_path))
        except ValueError:
            return str(self.file_path)
    
    def add_match(self, match: SearchMatch):
        self.matches.append(match)
        self.total_matches += match.matches_count
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": str(self.file_path),
            "relative_path": self.relative_path,
            "total_matches": self.total_matches,
            "matches": [match.to_dict() for match in self.matches]
        }


class SearchService:
    """Text search service for Obsidian vaults"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def compile_search_pattern(
        self, 
        query: str, 
        case_sensitive: bool = False,
        whole_word: bool = False,
        use_regex: bool = False
    ) -> re.Pattern:
        """Compile search pattern based on options"""
        
        if use_regex:
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                return re.compile(query, flags)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        else:
            # Escape special regex characters for literal search
            escaped_query = re.escape(query)
            if whole_word:
                escaped_query = r'\b' + escaped_query + r'\b'
            flags = 0 if case_sensitive else re.IGNORECASE
            return re.compile(escaped_query, flags)
    
    def search_file(
        self, 
        file_path: Path, 
        pattern: re.Pattern,
        vault_path: str
    ) -> Optional[SearchFileResult]:
        """Search for pattern in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            result = SearchFileResult(file_path, vault_path)
            
            for line_num, line in enumerate(lines, 1):
                matches = list(pattern.finditer(line))
                if matches:
                    search_match = SearchMatch(
                        line_number=line_num,
                        line_content=line.rstrip(),
                        matches_count=len(matches)
                    )
                    result.add_match(search_match)
            
            return result if result.matches else None
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    async def search_vault(
        self,
        vault_path: str,
        query: str,
        case_sensitive: bool = False,
        whole_word: bool = False,
        use_regex: bool = False,
        max_results: int = 100,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Search for text in vault files
        Returns: Dictionary with search results and metadata
        """
        
        start_time = time.time()
        
        # Validate vault
        if not vault_manager.is_obsidian_vault(vault_path):
            raise ValueError("Invalid Obsidian vault path")
        
        # Get markdown files
        md_files = vault_manager.get_markdown_files(vault_path)
        total_files = len(md_files)
        
        if total_files == 0:
            return {
                "query": query,
                "total_files_scanned": 0,
                "files_with_matches": 0,
                "total_matches": 0,
                "results": [],
                "execution_time_ms": (time.time() - start_time) * 1000
            }
        
        # Compile search pattern
        try:
            pattern = self.compile_search_pattern(query, case_sensitive, whole_word, use_regex)
        except ValueError as e:
            raise ValueError(str(e))
        
        # Search files concurrently
        results = []
        total_matches = 0
        
        # Process files in batches to avoid overwhelming the system
        batch_size = 20
        files_processed = 0
        
        for i in range(0, len(md_files), batch_size):
            batch_files = md_files[i:i + batch_size]
            
            # Submit batch to thread pool
            loop = asyncio.get_event_loop()
            batch_tasks = [
                loop.run_in_executor(
                    self.executor,
                    self.search_file,
                    file_path,
                    pattern,
                    vault_path
                )
                for file_path in batch_files
            ]
            
            # Wait for batch completion
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process results
            for result in batch_results:
                if isinstance(result, SearchFileResult):
                    results.append(result)
                    total_matches += result.total_matches
                    
                    # Stop if we hit max results
                    if len(results) >= max_results:
                        break
            
            # Update progress
            files_processed += len(batch_files)
            if progress_callback:
                progress_pct = (files_processed / total_files) * 100
                progress_callback(progress_pct, f"Searched {files_processed}/{total_files} files")
            
            # Break if we hit max results
            if len(results) >= max_results:
                break
        
        # Sort results by total matches (most relevant first)
        results.sort(key=lambda x: x.total_matches, reverse=True)
        
        # Limit results
        results = results[:max_results]
        
        execution_time = (time.time() - start_time) * 1000
        
        return {
            "query": query,
            "total_files_scanned": total_files,
            "files_with_matches": len(results),
            "total_matches": total_matches,
            "results": [result.to_dict() for result in results],
            "execution_time_ms": execution_time
        }
    
    def export_results_csv(self, results: List[Dict], query: str) -> str:
        """Export search results to CSV format"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Query', 'File', 'Line Number', 'Content', 'Matches'])
        
        # Write results
        for file_result in results:
            file_path = file_result['relative_path']
            for match in file_result['matches']:
                writer.writerow([
                    query,
                    file_path,
                    match['line_number'],
                    match['line_content'],
                    match['matches_count']
                ])
        
        return output.getvalue()
    
    def export_results_json(self, results_data: Dict) -> str:
        """Export search results to JSON format"""
        import json
        return json.dumps(results_data, indent=2, default=str)


# Global search service instance
search_service = SearchService()