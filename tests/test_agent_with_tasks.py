"""
Integration tests for AI Agent with Task State Management
"""
import pytest
import asyncio
from src.agent_core import AICodeAgent
import shutil
import os
from pathlib import Path

@pytest.mark.asyncio
async def test_agent_creates_files_with_verification():
    """Test that agent actually creates and verifies files"""
    
    # Clean demo folder
    demo_path = Path('demo')
    if demo_path.exists():
        shutil.rmtree(demo_path)
    demo_path.mkdir(parents=True)
    
    agent = AICodeAgent()
    
    result = await agent.execute("""
    Create a simple Header component in demo/src/components/Header.tsx
    with TypeScript and basic styling.
    """, max_iterations=5)
    
    # Check result
    assert result["success"] == True, f"Task failed: {result.get('error', 'Unknown error')}"
    
    # Check task plan exists
    task_plan = result.get("task_plan")
    assert task_plan is not None, "Task plan not found in result"
    
    # Check files were created
    files_created = result.get("files_created", [])
    assert len(files_created) > 0, "No files were created"
    
    # Verify files actually exist
    for file_path in files_created:
        assert os.path.exists(file_path), f"File {file_path} not found!"
        
        # Check file has content
        with open(file_path) as f:
            content = f.read()
            assert len(content) > 0, f"File {file_path} is empty!"
    
    # Cleanup
    if demo_path.exists():
        shutil.rmtree(demo_path)

@pytest.mark.asyncio
async def test_task_progress_tracking():
    """Test that task progress is properly tracked"""
    
    agent = AICodeAgent()
    
    result = await agent.execute("""
    Create two simple components:
    1. Button component
    2. Card component
    """, max_iterations=8)
    
    # Check task plan
    task_plan = result.get("task_plan")
    assert task_plan is not None
    
    # Check progress
    progress = task_plan.get("progress", {})
    assert progress.get("total", 0) > 0, "No tasks were created"
    
    # Check completion percentage
    completion = task_plan.get("completion_percentage", 0)
    assert completion >= 0, "Invalid completion percentage"
    assert completion <= 100, "Completion percentage exceeds 100%"
    
    # If successful, all tasks should be done
    if result["success"]:
        assert progress.get("done", 0) == progress.get("total", 0), "Not all tasks completed"

@pytest.mark.asyncio
async def test_bash_verification_prevents_false_positives():
    """Test that bash verification catches when files aren't actually created"""
    
    # This test verifies the verification logic itself
    from src.task_state import TaskState, TaskStatus
    from pathlib import Path
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a task expecting a file
        task = TaskState(
            id=1,
            name="Test Task",
            description="Create a file",
            status=TaskStatus.IN_PROGRESS,
            files_expected=[os.path.join(tmpdir, "test.txt")]
        )
        
        # Verify without creating file - should fail
        verification = task.verify_files_exist()
        assert verification[os.path.join(tmpdir, "test.txt")] == False
        
        # Create the file
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("content")
        
        # Verify again - should pass
        verification = task.verify_files_exist()
        assert verification[str(test_file)] == True

@pytest.mark.asyncio
async def test_retry_logic():
    """Test that failed tasks can be retried"""
    
    from src.task_state import TaskState, TaskPlan, TaskStatus
    
    # Create a task plan with a failed task
    task1 = TaskState(
        id=1,
        name="Task 1",
        description="First task",
        status=TaskStatus.DONE
    )
    
    task2 = TaskState(
        id=2,
        name="Task 2",
        description="Second task",
        status=TaskStatus.FAILED,
        retry_count=0,
        max_retries=3
    )
    
    task_plan = TaskPlan(
        tasks=[task1, task2],
        user_request="Test request",
        created_at=0.0
    )
    
    # Get next task should return the failed task
    next_task = task_plan.get_next_task()
    assert next_task is not None
    assert next_task.id == 2
    assert next_task.retry_count == 1  # Should increment
    
    # Exhaust retries
    task2.retry_count = 3
    next_task = task_plan.get_next_task()
    assert next_task is None  # No more retryable tasks

@pytest.mark.asyncio  
async def test_no_duplicate_files():
    """Test that agent doesn't create duplicate files"""
    
    demo_path = Path('demo')
    if demo_path.exists():
        shutil.rmtree(demo_path)
    demo_path.mkdir(parents=True)
    
    agent = AICodeAgent()
    
    result = await agent.execute("""
    Create a Button component in demo/src/components/Button.tsx
    """, max_iterations=5)
    
    # Count Button.tsx files
    button_files = []
    for root, dirs, files in os.walk('demo'):
        for file in files:
            if 'Button.tsx' in file:
                button_files.append(os.path.join(root, file))
    
    # Should only have one Button.tsx
    assert len(button_files) <= 1, f"Duplicate files created: {button_files}"
    
    # Cleanup
    if demo_path.exists():
        shutil.rmtree(demo_path)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
