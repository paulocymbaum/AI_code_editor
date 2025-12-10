"""
Unit tests for Task State Management System
"""
import pytest
from src.task_state import TaskState, TaskPlan, TaskStatus
from pathlib import Path
import tempfile
import os

def test_task_state_creation():
    """Test basic task state creation"""
    task = TaskState(
        id=1,
        name="Test Task",
        description="Test description",
        status=TaskStatus.PENDING,
        files_expected=["test.txt"]
    )
    
    assert task.id == 1
    assert task.status == TaskStatus.PENDING
    assert len(task.files_expected) == 1
    assert task.name == "Test Task"
    assert task.description == "Test description"

def test_bash_file_verification():
    """Test bash file verification actually works"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a real file
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("content")
        
        task = TaskState(
            id=1,
            name="Test",
            description="Test",
            status=TaskStatus.PENDING,
            files_expected=[str(test_file)]
        )
        
        # Verify file exists
        verification = task.verify_files_exist()
        assert verification[str(test_file)] == True
        
        # Verify non-existent file
        task2 = TaskState(
            id=2,
            name="Test2",
            description="Test2",
            status=TaskStatus.PENDING,
            files_expected=["/nonexistent/file.txt"]
        )
        
        verification2 = task2.verify_files_exist()
        assert verification2["/nonexistent/file.txt"] == False

def test_empty_file_detection():
    """Test that empty files are not considered valid"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an empty file
        empty_file = Path(tmpdir) / "empty.txt"
        empty_file.touch()
        
        task = TaskState(
            id=1,
            name="Test",
            description="Test",
            status=TaskStatus.PENDING,
            files_expected=[str(empty_file)]
        )
        
        # Empty file should not verify
        verification = task.verify_files_exist()
        assert verification[str(empty_file)] == False

def test_task_plan_progress():
    """Test task plan progress tracking"""
    tasks = [
        TaskState(1, "Task 1", "Desc 1", TaskStatus.DONE),
        TaskState(2, "Task 2", "Desc 2", TaskStatus.PENDING),
        TaskState(3, "Task 3", "Desc 3", TaskStatus.FAILED)
    ]
    
    plan = TaskPlan(tasks, "Test request", 0.0)
    
    progress = plan.get_progress()
    assert progress["done"] == 1
    assert progress["pending"] == 1
    assert progress["failed"] == 1
    assert progress["total"] == 3
    
    completion = plan.get_completion_percentage()
    assert completion == pytest.approx(33.33, rel=0.01)

def test_get_next_task():
    """Test getting next pending task"""
    tasks = [
        TaskState(1, "Task 1", "Desc 1", TaskStatus.DONE),
        TaskState(2, "Task 2", "Desc 2", TaskStatus.PENDING),
        TaskState(3, "Task 3", "Desc 3", TaskStatus.PENDING)
    ]
    
    plan = TaskPlan(tasks, "Test request", 0.0)
    
    # Should return first pending task
    next_task = plan.get_next_task()
    assert next_task is not None
    assert next_task.id == 2
    
def test_retry_logic():
    """Test task retry functionality"""
    task = TaskState(
        id=1,
        name="Test",
        description="Test",
        status=TaskStatus.FAILED,
        retry_count=0,
        max_retries=3
    )
    
    # Should be retryable
    assert task.can_retry() == True
    
    # Exhaust retries
    task.retry_count = 3
    assert task.can_retry() == False
    
def test_task_completion_verification():
    """Test task completion verification"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a real file
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("content")
        
        task = TaskState(
            id=1,
            name="Test",
            description="Test",
            status=TaskStatus.DONE,
            files_expected=[str(test_file)]
        )
        
        # Should verify as complete
        assert task.verify_completion() == True
        
        # Task with missing files should not verify
        task2 = TaskState(
            id=2,
            name="Test2",
            description="Test2",
            status=TaskStatus.DONE,
            files_expected=["/nonexistent/file.txt"]
        )
        
        assert task2.verify_completion() == False

def test_json_serialization():
    """Test task plan can be serialized to JSON"""
    tasks = [
        TaskState(1, "Task 1", "Desc 1", TaskStatus.DONE,
                  files_verified=["file1.txt"])
    ]
    
    plan = TaskPlan(tasks, "Test", 0.0)
    
    # Serialize
    json_str = plan.to_json()
    assert json_str is not None
    assert "Task 1" in json_str
    
    # Deserialize
    plan2 = TaskPlan.from_json(json_str)
    assert len(plan2.tasks) == 1
    assert plan2.tasks[0].name == "Task 1"
    assert plan2.tasks[0].status == TaskStatus.DONE

def test_task_to_dict():
    """Test task state dictionary conversion"""
    task = TaskState(
        id=1,
        name="Test Task",
        description="Test description",
        status=TaskStatus.IN_PROGRESS,
        files_expected=["test.txt"],
        files_created=["test.txt"],
        files_verified=["test.txt"],
        tool_used="test_tool",
        error=None,
        iteration_started=1,
        iteration_completed=None,
        retry_count=0
    )
    
    task_dict = task.to_dict()
    
    assert task_dict["id"] == 1
    assert task_dict["name"] == "Test Task"
    assert task_dict["status"] == "in_progress"
    assert task_dict["tool_used"] == "test_tool"
    assert task_dict["retry_count"] == 0

def test_verify_all_tasks():
    """Test verifying all tasks in a plan"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a real file
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("content")
        
        tasks = [
            TaskState(1, "Task 1", "Desc 1", TaskStatus.DONE,
                      files_expected=[str(test_file)]),
            TaskState(2, "Task 2", "Desc 2", TaskStatus.DONE,
                      files_expected=["/nonexistent.txt"])
        ]
        
        plan = TaskPlan(tasks, "Test", 0.0)
        
        verification = plan.verify_all_tasks()
        
        # First task should verify
        assert verification[1] == True
        
        # Second task should fail verification
        assert verification[2] == False
        
        # Second task should now be marked as failed
        assert tasks[1].status == TaskStatus.FAILED

def test_is_complete():
    """Test checking if all tasks are complete"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a real file
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("content")
        
        tasks = [
            TaskState(1, "Task 1", "Desc 1", TaskStatus.DONE,
                      files_expected=[str(test_file)]),
            TaskState(2, "Task 2", "Desc 2", TaskStatus.PENDING)
        ]
        
        plan = TaskPlan(tasks, "Test", 0.0)
        
        # Not complete because task 2 is pending
        assert plan.is_complete() == False
        
        # Mark task 2 as done
        tasks[1].status = TaskStatus.DONE
        tasks[1].files_expected = []  # No files expected
        
        # Should now be complete
        assert plan.is_complete() == True

def test_get_files_created():
    """Test getting all files created across tasks"""
    tasks = [
        TaskState(1, "Task 1", "Desc 1", TaskStatus.DONE,
                  files_verified=["file1.txt", "file2.txt"]),
        TaskState(2, "Task 2", "Desc 2", TaskStatus.DONE,
                  files_verified=["file3.txt"])
    ]
    
    plan = TaskPlan(tasks, "Test", 0.0)
    
    files = plan.get_files_created()
    assert len(files) == 3
    assert "file1.txt" in files
    assert "file2.txt" in files
    assert "file3.txt" in files

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
