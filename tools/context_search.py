"""
Context & Search Tools
Provides semantic search and context retrieval
"""

import pathlib
import subprocess
from typing import List, Dict, Any
from tool_schemas import (
    SemanticSearchInput, GrepSearchInput, GetContextInput,
    SummarizeCodebaseInput, ToolResult
)


async def semantic_search(params: SemanticSearchInput) -> ToolResult:
    """Semantic search using vector embeddings"""
    try:
        # This would integrate with ChromaDB in production
        # Simplified implementation for demonstration
        
        results = []
        # Placeholder: would query vector database here
        
        return ToolResult(
            success=True,
            data={
                "results": results,
                "query": params.query,
                "count": len(results)
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def grep_search(params: GrepSearchInput) -> ToolResult:
    """Fast text-based search"""
    try:
        cmd = ['grep', '-rn']
        
        if not params.case_sensitive:
            cmd.append('-i')
        
        cmd.extend([params.pattern, params.path])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        matches = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split(':', 2)
                if len(parts) >= 3:
                    matches.append({
                        "file": parts[0],
                        "line": parts[1],
                        "content": parts[2]
                    })
        
        return ToolResult(
            success=True,
            data={"matches": matches[:100]}  # Limit results
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def get_context(params: GetContextInput) -> ToolResult:
    """Retrieve relevant code context"""
    try:
        # This would use semantic search + file analysis in production
        context_data = {
            "task": params.task_description,
            "relevant_files": [],
            "snippets": []
        }
        
        return ToolResult(success=True, data=context_data)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def summarize_codebase(params: SummarizeCodebaseInput) -> ToolResult:
    """Generate codebase summary"""
    try:
        root = pathlib.Path(params.root_path)
        
        # Count files by type
        file_counts = {}
        total_lines = 0
        
        for file_path in root.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix or "no_extension"
                file_counts[ext] = file_counts.get(ext, 0) + 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        total_lines += len(f.readlines())
                except:
                    pass
        
        summary = {
            "root": str(root),
            "file_counts": file_counts,
            "total_files": sum(file_counts.values()),
            "total_lines": total_lines,
            "detail_level": params.detail_level
        }
        
        return ToolResult(success=True, data=summary)
    except Exception as e:
        return ToolResult(success=False, error=str(e))
