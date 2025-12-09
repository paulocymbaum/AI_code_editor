"""
Test Tool Execution
Tests that basic tool operations work correctly
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
import asyncio

# Import test modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.tool_schemas import (
    ToolResult,
    ReadFileInput,
    WriteFileInput,
    ListDirectoryInput,
    DeleteFileInput
)
from src.tools import file_operations
from src.tools.design_system import generate_design_system, GenerateDesignSystemInput
from src.tools.javascript_tools import generate_react_component, GenerateReactComponentInput


class TestFileOperations:
    """Test basic file operations"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_write_and_read_file(self, temp_dir):
        """Test writing and reading a file"""
        file_path = os.path.join(temp_dir, "test.txt")
        content = "Hello, World!\nThis is a test file."
        
        # Write file
        write_result = await file_operations.write_file(
            WriteFileInput(file_path=file_path, content=content)
        )
        
        assert write_result.success is True
        assert os.path.exists(file_path)
        
        # Read file
        read_result = await file_operations.read_file(
            ReadFileInput(file_path=file_path)
        )
        
        assert read_result.success is True
        assert read_result.data is not None
        assert read_result.data.get('content') == content
    
    @pytest.mark.asyncio
    async def test_list_directory(self, temp_dir):
        """Test listing directory contents"""
        # Create some test files
        for i in range(3):
            file_path = os.path.join(temp_dir, f"file{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Content {i}")
        
        # List directory
        result = await file_operations.list_directory(
            ListDirectoryInput(directory_path=temp_dir)
        )
        
        assert result.success is True
        assert result.data is not None
        assert 'files' in result.data
        assert len(result.data['files']) >= 3
    
    @pytest.mark.asyncio
    async def test_create_nested_directories(self, temp_dir):
        """Test creating nested directories automatically"""
        nested_path = os.path.join(temp_dir, "level1", "level2", "level3", "test.txt")
        
        write_result = await file_operations.write_file(
            WriteFileInput(
                file_path=nested_path,
                content="Nested file",
                create_dirs=True
            )
        )
        
        assert write_result.success is True
        assert os.path.exists(nested_path)
        assert os.path.isdir(os.path.join(temp_dir, "level1", "level2", "level3"))
    
    @pytest.mark.asyncio
    async def test_delete_file(self, temp_dir):
        """Test deleting a file"""
        file_path = os.path.join(temp_dir, "to_delete.txt")
        
        # Create file
        await file_operations.write_file(
            WriteFileInput(file_path=file_path, content="Delete me")
        )
        assert os.path.exists(file_path)
        
        # Delete file
        delete_result = await file_operations.delete_file(
            DeleteFileInput(file_path=file_path)
        )
        
        assert delete_result.success is True
        assert not os.path.exists(file_path)
    
    @pytest.mark.asyncio
    async def test_error_handling_read_nonexistent(self):
        """Test error handling when reading non-existent file"""
        result = await file_operations.read_file(
            ReadFileInput(file_path="/nonexistent/file.txt")
        )
        
        assert result.success is False
        assert result.error is not None
        assert "not found" in result.error.lower() or "no such file" in result.error.lower()


class TestDesignSystemGeneration:
    """Test design system generation"""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory"""
        temp = tempfile.mkdtemp(prefix="test_project_")
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_generate_design_system_basic(self, temp_project):
        """Test basic design system generation"""
        result = await generate_design_system(
            GenerateDesignSystemInput(
                project_path=temp_project,
                framework="nextjs",
                include_dark_mode=True,
                include_component_patterns=True,
                include_docs=True
            )
        )
        
        assert result.success is True, f"Design system generation failed: {result.error}"
        assert result.data is not None
        assert 'generated_files' in result.data
        assert 'token_count' in result.data
        
        # Check files were created
        generated_files = result.data['generated_files']
        assert len(generated_files) > 0
        
        for file_path in generated_files:
            assert os.path.exists(file_path), f"File not found: {file_path}"
    
    @pytest.mark.asyncio
    async def test_design_system_files_content(self, temp_project):
        """Test that generated design system files have correct content"""
        result = await generate_design_system(
            GenerateDesignSystemInput(project_path=temp_project)
        )
        
        assert result.success is True
        
        # Check tailwind.config.js
        tailwind_path = os.path.join(temp_project, "tailwind.config.js")
        if os.path.exists(tailwind_path):
            with open(tailwind_path, 'r') as f:
                content = f.read()
            assert "module.exports" in content or "export default" in content
            assert "primary" in content
        
        # Check globals.css
        css_path = os.path.join(temp_project, "src", "app", "globals.css")
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                content = f.read()
            assert "@tailwind base" in content
            assert "--color-primary" in content or "primary" in content
    
    @pytest.mark.asyncio
    async def test_design_system_token_count(self, temp_project):
        """Test that design system reports token count"""
        result = await generate_design_system(
            GenerateDesignSystemInput(project_path=temp_project)
        )
        
        assert result.success is True
        assert result.data is not None
        assert 'token_count' in result.data
        assert result.data['token_count'] > 0


class TestReactComponentGeneration:
    """Test React component generation"""
    
    @pytest.fixture
    def temp_components_dir(self):
        """Create a temporary components directory"""
        temp = tempfile.mkdtemp(prefix="test_components_")
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_generate_simple_component(self, temp_components_dir):
        """Test generating a simple React component"""
        result = await generate_react_component(
            GenerateReactComponentInput(
                component_name="TestButton",
                component_pattern="button",
                variant="primary",
                styling="tailwind",
                output_dir=temp_components_dir
            )
        )
        
        assert result.success is True, f"Component generation failed: {result.error}"
        assert result.data is not None
        
        # Check file was created
        component_file = os.path.join(temp_components_dir, "TestButton.tsx")
        assert os.path.exists(component_file), f"Component file not found: {component_file}"
    
    @pytest.mark.asyncio
    async def test_component_file_content(self, temp_components_dir):
        """Test that generated component has correct structure"""
        result = await generate_react_component(
            GenerateReactComponentInput(
                component_name="CustomCard",
                component_pattern="card",
                variant="secondary",
                styling="tailwind",
                output_dir=temp_components_dir
            )
        )
        
        assert result.success is True
        
        component_file = os.path.join(temp_components_dir, "CustomCard.tsx")
        with open(component_file, 'r') as f:
            content = f.read()
        
        # Check component structure
        assert "CustomCard" in content
        assert "export" in content
        assert "function" in content or "const" in content
        assert "return" in content
    
    @pytest.mark.asyncio
    async def test_generate_multiple_components(self, temp_components_dir):
        """Test generating multiple components"""
        components = [
            ("Card1", "card", "primary"),
            ("Card2", "card", "secondary"),
            ("Button1", "button", "primary"),
        ]
        
        for name, pattern, variant in components:
            result = await generate_react_component(
                GenerateReactComponentInput(
                    component_name=name,
                    component_pattern=pattern,
                    variant=variant,
                    styling="tailwind",
                    output_dir=temp_components_dir
                )
            )
            assert result.success is True, f"Failed to generate {name}"
        
        # Check all files exist
        for name, _, _ in components:
            file_path = os.path.join(temp_components_dir, f"{name}.tsx")
            assert os.path.exists(file_path), f"Component {name} not found"


class TestToolResultFormat:
    """Test that tools return proper ToolResult format"""
    
    @pytest.mark.asyncio
    async def test_success_result_format(self):
        """Test successful result format"""
        temp_dir = tempfile.mkdtemp()
        try:
            result = await file_operations.list_directory(
                ListDirectoryInput(directory_path=temp_dir)
            )
            
            # Check ToolResult structure
            assert isinstance(result, ToolResult)
            assert result.success is True
            assert result.data is not None
            assert isinstance(result.data, dict)
            assert result.error is None
            assert isinstance(result.metadata, dict)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_error_result_format(self):
        """Test error result format"""
        result = await file_operations.read_file(
            ReadFileInput(file_path="/nonexistent/path/file.txt")
        )
        
        # Check error ToolResult structure
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert result.error is not None
        assert isinstance(result.error, str)
        assert len(result.error) > 0


class TestToolPerformance:
    """Test tool performance and efficiency"""
    
    @pytest.mark.asyncio
    async def test_file_operations_speed(self):
        """Test that file operations complete in reasonable time"""
        import time
        
        temp_dir = tempfile.mkdtemp()
        try:
            file_path = os.path.join(temp_dir, "speed_test.txt")
            content = "x" * 10000  # 10KB content
            
            start_time = time.time()
            result = await file_operations.write_file(
                WriteFileInput(file_path=file_path, content=content)
            )
            elapsed = time.time() - start_time
            
            assert result.success is True
            assert elapsed < 1.0, f"Write operation took too long: {elapsed}s"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test that tools can handle concurrent operations"""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create multiple files concurrently
            tasks = []
            for i in range(5):
                file_path = os.path.join(temp_dir, f"concurrent_{i}.txt")
                task = file_operations.write_file(
                    WriteFileInput(file_path=file_path, content=f"Content {i}")
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            # Check all succeeded
            for result in results:
                assert result.success is True
            
            # Check all files exist
            files = os.listdir(temp_dir)
            assert len(files) == 5
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
