"""
Task State Management System
Tracks task execution state and file creation verification
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import json
import time

from .utils.path_utils import PathUtils

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TaskState:
    """State of a single task"""
    id: int
    name: str
    description: str
    status: TaskStatus
    files_expected: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    files_verified: List[str] = field(default_factory=list)
    tool_used: Optional[str] = None
    error: Optional[str] = None
    iteration_started: Optional[int] = None
    iteration_completed: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def verify_files_exist(self) -> Dict[str, bool]:
        """
        Verify files exist using bash find command
        Returns dict of {filepath: exists}
        """
        verification = {}
        
        for expected_file in self.files_expected:
            exists = self._bash_file_exists(expected_file)
            verification[expected_file] = exists
            
            if exists:
                self.files_verified.append(expected_file)
        
        return verification
    
    def _bash_file_exists(self, filepath: str) -> bool:
        """
        Check if file exists using PathUtils (prevents false positives)
        Returns True if file exists and has content
        """
        return PathUtils.file_exists(filepath)
    
    def verify_completion(self) -> bool:
        """
        Check if task is truly complete
        - All expected files exist
        - All files have content
        """
        if not self.files_expected:
            # No specific files expected, assume done if status is done
            return self.status == TaskStatus.DONE
        
        verification = self.verify_files_exist()
        all_exist = all(verification.values())
        
        if not all_exist:
            missing = [f for f, exists in verification.items() if not exists]
            self.error = f"Missing files: {', '.join(missing)}"
            return False
        
        return True
    
    def can_retry(self) -> bool:
        """Check if task can be retried"""
        return self.status == TaskStatus.FAILED and self.retry_count < self.max_retries
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "files_expected": self.files_expected,
            "files_created": self.files_created,
            "files_verified": self.files_verified,
            "tool_used": self.tool_used,
            "error": self.error,
            "iteration_started": self.iteration_started,
            "iteration_completed": self.iteration_completed,
            "retry_count": self.retry_count
        }


@dataclass
class TaskPlan:
    """Complete task execution plan"""
    tasks: List[TaskState]
    user_request: str
    created_at: float
    project_dir: str = "."
    
    def get_next_task(self) -> Optional[TaskState]:
        """Get next pending or failed (retryable) task"""
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                return task
            if task.status == TaskStatus.FAILED and task.can_retry():
                task.retry_count += 1
                return task
        return None
    
    def is_complete(self) -> bool:
        """Check if all tasks are done (and verified)"""
        return all(
            t.status == TaskStatus.DONE and t.verify_completion() 
            for t in self.tasks
        )
    
    def get_progress(self) -> Dict[str, int]:
        """Get progress summary"""
        return {
            "total": len(self.tasks),
            "done": sum(1 for t in self.tasks if t.status == TaskStatus.DONE),
            "in_progress": sum(1 for t in self.tasks if t.status == TaskStatus.IN_PROGRESS),
            "pending": sum(1 for t in self.tasks if t.status == TaskStatus.PENDING),
            "failed": sum(1 for t in self.tasks if t.status == TaskStatus.FAILED),
            "skipped": sum(1 for t in self.tasks if t.status == TaskStatus.SKIPPED),
        }
    
    def get_completion_percentage(self) -> float:
        """Get completion percentage"""
        if not self.tasks:
            return 100.0
        progress = self.get_progress()
        return (progress["done"] / progress["total"]) * 100
    
    def get_files_created(self) -> List[str]:
        """Get all files created across all tasks"""
        files = []
        for task in self.tasks:
            files.extend(task.files_verified)
        return files
    
    def verify_all_tasks(self) -> Dict[int, bool]:
        """
        Verify all tasks marked as done actually created files
        Returns dict of {task_id: verified}
        """
        verification = {}
        for task in self.tasks:
            if task.status == TaskStatus.DONE:
                verified = task.verify_completion()
                verification[task.id] = verified
                
                if not verified:
                    # Mark as failed if verification fails
                    task.status = TaskStatus.FAILED
        
        return verification
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "user_request": self.user_request,
            "created_at": self.created_at,
            "project_dir": self.project_dir,
            "tasks": [t.to_dict() for t in self.tasks],
            "progress": self.get_progress(),
            "completion_percentage": self.get_completion_percentage(),
            "files_created": self.get_files_created()
        }
    
    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskPlan':
        """Create TaskPlan from dictionary"""
        tasks = [
            TaskState(
                id=t["id"],
                name=t["name"],
                description=t["description"],
                status=TaskStatus(t["status"]),
                files_expected=t.get("files_expected", []),
                files_created=t.get("files_created", []),
                files_verified=t.get("files_verified", []),
                tool_used=t.get("tool_used"),
                error=t.get("error"),
                iteration_started=t.get("iteration_started"),
                iteration_completed=t.get("iteration_completed"),
                retry_count=t.get("retry_count", 0)
            )
            for t in data["tasks"]
        ]
        
        return cls(
            tasks=tasks,
            user_request=data["user_request"],
            created_at=data["created_at"],
            project_dir=data.get("project_dir", ".")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TaskPlan':
        """Deserialize from JSON"""
        data = json.loads(json_str)
        return cls.from_dict(data)


def log_task_plan(task_plan: TaskPlan, logger):
    """Log task plan in a beautiful format"""
    import logging
    
    logger.info(f"\n{'='*80}")
    logger.info(f"📋 TASK PLAN - {len(task_plan.tasks)} tasks")
    logger.info(f"{'='*80}")
    
    progress = task_plan.get_progress()
    completion = task_plan.get_completion_percentage()
    
    logger.info(f"📊 Progress: {progress['done']}/{progress['total']} tasks completed ({completion:.1f}%)")
    logger.info(f"")
    
    status_icons = {
        TaskStatus.DONE: "✅",
        TaskStatus.IN_PROGRESS: "🔄",
        TaskStatus.PENDING: "⏳",
        TaskStatus.FAILED: "❌",
        TaskStatus.SKIPPED: "⏭️"
    }
    
    for task in task_plan.tasks:
        icon = status_icons.get(task.status, "❓")
        logger.info(f"{icon} Task {task.id}: {task.name}")
        
        if task.status == TaskStatus.DONE and task.files_verified:
            logger.info(f"   📄 Files: {', '.join(task.files_verified)}")
        
        if task.status == TaskStatus.IN_PROGRESS:
            logger.info(f"   🔧 Tool: {task.tool_used}")
        
        if task.status == TaskStatus.FAILED:
            logger.info(f"   ❌ Error: {task.error}")
            if task.retry_count > 0:
                logger.info(f"   🔄 Retries: {task.retry_count}/{task.max_retries}")
    
    logger.info(f"{'='*80}\n")
