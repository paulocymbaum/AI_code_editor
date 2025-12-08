"""
Git Operations Tools
Handles version control operations
"""

import subprocess
from typing import Optional, List
from ..tool_schemas import (
    GitStatusInput, GitDiffInput, GitCommitInput,
    GitPushInput, CreateBranchInput, ToolResult
)


async def git_status(params: GitStatusInput) -> ToolResult:
    """Get git repository status"""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=params.repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return ToolResult(success=False, error=result.stderr)
        
        # Parse status output
        changes = []
        for line in result.stdout.strip().split('\n'):
            if line:
                status = line[:2]
                file_path = line[3:]
                changes.append({"status": status, "file": file_path})
        
        return ToolResult(success=True, data={"changes": changes})
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def git_diff(params: GitDiffInput) -> ToolResult:
    """Get git diff"""
    try:
        cmd = ['git', 'diff']
        
        if params.staged:
            cmd.append('--staged')
        
        if params.target:
            cmd.append(params.target)
        
        result = subprocess.run(
            cmd,
            cwd=params.repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return ToolResult(
            success=True,
            data={"diff": result.stdout}
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def git_commit(params: GitCommitInput) -> ToolResult:
    """Commit changes"""
    try:
        # Stage files
        if params.files:
            for file in params.files:
                subprocess.run(
                    ['git', 'add', file],
                    cwd=params.repo_path,
                    check=True
                )
        else:
            subprocess.run(
                ['git', 'add', '-A'],
                cwd=params.repo_path,
                check=True
            )
        
        # Commit
        result = subprocess.run(
            ['git', 'commit', '-m', params.message],
            cwd=params.repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return ToolResult(success=False, error=result.stderr)
        
        # Get commit hash
        hash_result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=params.repo_path,
            capture_output=True,
            text=True
        )
        
        return ToolResult(
            success=True,
            data={
                "commit_hash": hash_result.stdout.strip(),
                "message": params.message
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def git_push(params: GitPushInput) -> ToolResult:
    """Push commits to remote"""
    try:
        cmd = ['git', 'push', params.remote]
        
        if params.branch:
            cmd.append(params.branch)
        
        result = subprocess.run(
            cmd,
            cwd=params.repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return ToolResult(
            success=result.returncode == 0,
            data={
                "output": result.stdout,
                "remote": params.remote,
                "branch": params.branch
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def create_branch(params: CreateBranchInput) -> ToolResult:
    """Create a new git branch"""
    try:
        # Create branch
        result = subprocess.run(
            ['git', 'branch', params.branch_name],
            cwd=params.repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return ToolResult(success=False, error=result.stderr)
        
        # Checkout if requested
        if params.checkout:
            checkout_result = subprocess.run(
                ['git', 'checkout', params.branch_name],
                cwd=params.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if checkout_result.returncode != 0:
                return ToolResult(success=False, error=checkout_result.stderr)
        
        return ToolResult(
            success=True,
            data={
                "branch": params.branch_name,
                "checked_out": params.checkout
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))
