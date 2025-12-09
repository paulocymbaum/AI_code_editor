"""
Test Tool Registry
Validates that all tools can be imported, registered correctly, and match their schemas
"""

import pytest
import json
import os
from pathlib import Path
from typing import Dict, Any
import asyncio

# Import test modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.tool_schemas import TOOL_INPUT_SCHEMAS, ToolResult
from src import tools
from src.tools import (
    file_operations,
    code_analysis,
    execution,
    git_operations,
    context_search,
    ai_assisted,
    javascript_tools,
    design_system,
    page_management,
    redux_tools
)


class TestToolImports:
    """Test that all tool modules can be imported"""
    
    def test_import_file_operations(self):
        """Test file operations module"""
        assert hasattr(file_operations, 'read_file')
        assert hasattr(file_operations, 'write_file')
        assert hasattr(file_operations, 'edit_file')
        assert hasattr(file_operations, 'delete_file')
        assert hasattr(file_operations, 'list_directory')
        assert hasattr(file_operations, 'search_files')
    
    def test_import_code_analysis(self):
        """Test code analysis module"""
        assert hasattr(code_analysis, 'parse_code')
        assert hasattr(code_analysis, 'find_definitions')
        assert hasattr(code_analysis, 'find_references')
    
    def test_import_execution(self):
        """Test execution module"""
        assert hasattr(execution, 'execute_command')
        assert hasattr(execution, 'run_tests')
    
    def test_import_git_operations(self):
        """Test git operations module"""
        assert hasattr(git_operations, 'git_status')
        assert hasattr(git_operations, 'git_diff')
        assert hasattr(git_operations, 'git_commit')
    
    def test_import_context_search(self):
        """Test context search module"""
        assert hasattr(context_search, 'semantic_search')
        assert hasattr(context_search, 'grep_search')
    
    def test_import_javascript_tools(self):
        """Test JavaScript/React tools"""
        assert hasattr(javascript_tools, 'generate_react_component')
        assert hasattr(javascript_tools, 'GenerateReactComponentInput')
    
    def test_import_design_system(self):
        """Test design system tools"""
        assert hasattr(design_system, 'generate_design_system')
        assert hasattr(design_system, 'GenerateDesignSystemInput')
        assert hasattr(design_system, 'DesignSystemGenerator')
    
    def test_import_page_management(self):
        """Test page management tools"""
        assert hasattr(page_management, 'generate_page_with_components')
        assert hasattr(page_management, 'update_page_imports')
        assert hasattr(page_management, 'organize_project_files')
        assert hasattr(page_management, 'clean_demo_folder')


class TestToolRegistry:
    """Test tool registry and schema mapping"""
    
    def test_tool_input_schemas_exist(self):
        """Test that TOOL_INPUT_SCHEMAS is properly defined"""
        assert TOOL_INPUT_SCHEMAS is not None
        assert isinstance(TOOL_INPUT_SCHEMAS, dict)
        assert len(TOOL_INPUT_SCHEMAS) > 0
    
    def test_schema_registry_keys(self):
        """Test that key tools have schemas registered"""
        essential_tools = [
            "read_file",
            "write_file",
            "list_directory",
            "execute_command",
            "git_status"
        ]
        
        for tool in essential_tools:
            assert tool in TOOL_INPUT_SCHEMAS, f"Missing schema for {tool}"
    
    def test_schemas_are_classes(self):
        """Test that all registered schemas are classes"""
        for tool_name, schema in TOOL_INPUT_SCHEMAS.items():
            assert isinstance(schema, type), f"{tool_name} schema is not a class"
    
    def test_schema_instantiation(self):
        """Test that schemas can be instantiated with valid data"""
        from src.tool_schemas import ReadFileInput, WriteFileInput
        
        # Test ReadFileInput
        read_input = ReadFileInput(file_path="test.txt")
        assert read_input.file_path == "test.txt"
        
        # Test WriteFileInput
        write_input = WriteFileInput(
            file_path="output.txt",
            content="Hello world"
        )
        assert write_input.file_path == "output.txt"
        assert write_input.content == "Hello world"


class TestToolFunctionSignatures:
    """Test that tool functions have correct signatures"""
    
    @pytest.mark.asyncio
    async def test_file_operations_signatures(self):
        """Test file operation function signatures"""
        from src.tool_schemas import ReadFileInput, WriteFileInput, ListDirectoryInput
        
        # All should accept their input schemas
        functions_to_test = [
            (file_operations.read_file, ReadFileInput),
            (file_operations.write_file, WriteFileInput),
            (file_operations.list_directory, ListDirectoryInput),
        ]
        
        for func, input_schema in functions_to_test:
            assert callable(func), f"{func.__name__} is not callable"
            # Check if it's async
            assert asyncio.iscoroutinefunction(func), f"{func.__name__} should be async"
    
    @pytest.mark.asyncio
    async def test_tool_return_type(self):
        """Test that tools return ToolResult"""
        from src.tool_schemas import ListDirectoryInput
        
        # Test list_directory (safe operation)
        result = await file_operations.list_directory(
            ListDirectoryInput(directory_path=".")
        )
        
        assert isinstance(result, ToolResult), "Tool should return ToolResult"
        assert hasattr(result, 'success'), "ToolResult should have success field"
        assert hasattr(result, 'data'), "ToolResult should have data field"
        assert hasattr(result, 'error'), "ToolResult should have error field"


class TestToolDictionaryAlignment:
    """Test that tool_dictionary.json aligns with actual tools"""
    
    @pytest.fixture
    def tool_dictionary(self) -> Dict[str, Any]:
        """Load tool dictionary"""
        dict_path = Path(__file__).parent.parent.parent / "config" / "tool_dictionary.json"
        with open(dict_path, 'r') as f:
            return json.load(f)
    
    def test_file_operations_alignment(self, tool_dictionary):
        """Test file operations tools match dictionary"""
        file_ops_dict = tool_dictionary["tools"]["file_operations"]
        
        # Check each tool in dictionary exists as function
        for tool_name in file_ops_dict.keys():
            assert hasattr(file_operations, tool_name), \
                f"File operations missing function: {tool_name}"
    
    def test_ai_assisted_alignment(self, tool_dictionary):
        """Test AI-assisted tools match dictionary"""
        ai_tools_dict = tool_dictionary["tools"]["ai_assisted"]
        
        # Check key tools exist
        if "generate_react_component" in ai_tools_dict:
            assert hasattr(javascript_tools, 'generate_react_component')
        
        if "generate_design_system" in ai_tools_dict:
            assert hasattr(design_system, 'generate_design_system')
        
        if "generate_page_with_components" in ai_tools_dict:
            assert hasattr(page_management, 'generate_page_with_components')
    
    def test_tool_parameters_match(self, tool_dictionary):
        """Test that tool parameters in dictionary match schemas"""
        # Check read_file
        read_file_dict = tool_dictionary["tools"]["file_operations"]["read_file"]
        assert "file_path" in read_file_dict["parameters"]
        
        # Check write_file
        write_file_dict = tool_dictionary["tools"]["file_operations"]["write_file"]
        assert "file_path" in write_file_dict["parameters"]
        assert "content" in write_file_dict["parameters"]


class TestToolErrorHandling:
    """Test that tools handle errors properly"""
    
    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self):
        """Test reading a non-existent file returns error"""
        from src.tool_schemas import ReadFileInput
        
        result = await file_operations.read_file(
            ReadFileInput(file_path="/nonexistent/file/path/test.txt")
        )
        
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert result.error is not None
        assert len(result.error) > 0
    
    @pytest.mark.asyncio
    async def test_invalid_directory_listing(self):
        """Test listing invalid directory returns error"""
        from src.tool_schemas import ListDirectoryInput
        
        result = await file_operations.list_directory(
            ListDirectoryInput(directory_path="/this/path/does/not/exist")
        )
        
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert result.error is not None


class TestToolMetadata:
    """Test that tools provide proper metadata"""
    
    @pytest.mark.asyncio
    async def test_execution_time_tracking(self):
        """Test that tools track execution time"""
        from src.tool_schemas import ListDirectoryInput
        
        result = await file_operations.list_directory(
            ListDirectoryInput(directory_path=".")
        )
        
        # Check if execution_time_ms is tracked
        if result.execution_time_ms is not None:
            assert result.execution_time_ms >= 0, "Execution time should be non-negative"
    
    @pytest.mark.asyncio
    async def test_metadata_field(self):
        """Test that metadata field is available"""
        from src.tool_schemas import ListDirectoryInput
        
        result = await file_operations.list_directory(
            ListDirectoryInput(directory_path=".")
        )
        
        assert hasattr(result, 'metadata')
        assert isinstance(result.metadata, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
