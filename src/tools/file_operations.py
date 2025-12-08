"""
File Operations Tools
Handles all file system operations with safety checks
"""

import os
import pathlib
from typing import Optional, List
import chardet
from ..tool_schemas import (
    ReadFileInput, WriteFileInput, EditFileInput,
    DeleteFileInput, ListDirectoryInput, SearchFilesInput,
    ToolResult
)


async def read_file(params: ReadFileInput) -> ToolResult:
    """Read file contents with encoding detection"""
    try:
        file_path = pathlib.Path(params.file_path)
        
        if not file_path.exists():
            return ToolResult(
                success=False,
                error=f"File not found: {params.file_path}"
            )
        
        # Auto-detect encoding if needed
        if params.encoding == "auto":
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                detected = chardet.detect(raw_data)
                encoding = detected['encoding'] or 'utf-8'
        else:
            encoding = params.encoding
        
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        return ToolResult(
            success=True,
            data={
                "content": content,
                "encoding": encoding,
                "size": len(content),
                "lines": content.count('\n') + 1
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def write_file(params: WriteFileInput) -> ToolResult:
    """Write content to file"""
    try:
        file_path = pathlib.Path(params.file_path)
        
        # Create parent directories if needed
        if params.create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(params.content)
        
        return ToolResult(
            success=True,
            data={
                "file_path": str(file_path),
                "bytes_written": len(params.content.encode('utf-8'))
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def edit_file(params: EditFileInput) -> ToolResult:
    """Apply targeted edits to a file"""
    try:
        file_path = pathlib.Path(params.file_path)
        
        if not file_path.exists():
            return ToolResult(success=False, error=f"File not found: {params.file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if params.edit_type == "line_range":
            # Parse line range (e.g., "10-15")
            start, end = map(int, params.target.split('-'))
            lines[start-1:end] = [params.new_content + '\n']
        
        elif params.edit_type == "search_replace":
            # Simple search and replace
            content = ''.join(lines)
            content = content.replace(params.target, params.new_content)
            lines = content.splitlines(keepends=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return ToolResult(success=True, data={"modified": str(file_path)})
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def delete_file(params: DeleteFileInput) -> ToolResult:
    """Delete a file safely"""
    try:
        file_path = pathlib.Path(params.file_path)
        
        if not file_path.exists():
            return ToolResult(success=False, error=f"File not found: {params.file_path}")
        
        file_path.unlink()
        
        return ToolResult(success=True, data={"deleted": str(file_path)})
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def list_directory(params: ListDirectoryInput) -> ToolResult:
    """List directory contents"""
    try:
        dir_path = pathlib.Path(params.directory_path)
        
        if not dir_path.exists():
            return ToolResult(success=False, error=f"Directory not found: {params.directory_path}")
        
        if params.recursive:
            pattern = params.pattern or "**/*"
            files = [str(p) for p in dir_path.glob(pattern) if p.is_file()]
        else:
            pattern = params.pattern or "*"
            files = [str(p) for p in dir_path.glob(pattern)]
        
        return ToolResult(
            success=True,
            data={
                "files": files,
                "count": len(files)
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def search_files(params: SearchFilesInput) -> ToolResult:
    """Fuzzy search for files"""
    try:
        root = pathlib.Path(params.root_path)
        matches = []
        
        for file_path in root.rglob("*"):
            if file_path.is_file():
                # Simple fuzzy matching
                if params.query.lower() in file_path.name.lower():
                    if params.file_types:
                        if file_path.suffix in params.file_types:
                            matches.append(str(file_path))
                    else:
                        matches.append(str(file_path))
        
        return ToolResult(
            success=True,
            data={
                "matches": matches[:50],  # Limit results
                "total": len(matches)
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))
