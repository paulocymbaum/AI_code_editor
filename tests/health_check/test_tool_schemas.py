"""
Test Tool Schemas
Validates that all tool schemas are correctly defined and match the tool_dictionary.json
"""

import pytest
import json
import os
from pathlib import Path
from typing import Dict, Any

# Import schemas
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.tool_schemas import (
    ToolResult,
    ToolParameter,
    ToolDefinition,
    ToolCategory,
    RiskLevel,
    # File Operations
    ReadFileInput,
    WriteFileInput,
    EditFileInput,
    DeleteFileInput,
    ListDirectoryInput,
    SearchFilesInput,
    # Code Analysis
    ParseCodeInput,
    FindDefinitionsInput,
    FindReferencesInput,
    # Execution
    ExecuteCommandInput,
    # JavaScript/React
    GenerateReactComponentInput,
)


class TestToolSchemas:
    """Test that all tool schemas are properly defined"""
    
    def test_tool_result_schema(self):
        """Test ToolResult schema"""
        # Valid result
        result = ToolResult(success=True, data={"test": "value"})
        assert result.success is True
        assert result.data == {"test": "value"}
        assert result.error is None
        assert isinstance(result.metadata, dict)
        
        # Error result
        error_result = ToolResult(success=False, error="Test error")
        assert error_result.success is False
        assert error_result.error == "Test error"
        assert error_result.data is None
    
    def test_file_operation_schemas(self):
        """Test file operation input schemas"""
        
        # ReadFileInput
        read = ReadFileInput(file_path="test.txt")
        assert read.file_path == "test.txt"
        assert read.encoding == "utf-8"
        
        # WriteFileInput
        write = WriteFileInput(file_path="test.txt", content="Hello")
        assert write.file_path == "test.txt"
        assert write.content == "Hello"
        assert write.create_dirs is True
        
        # Path traversal protection
        with pytest.raises(ValueError):
            ReadFileInput(file_path="../../../etc/passwd")
        
        with pytest.raises(ValueError):
            WriteFileInput(file_path="../test.txt", content="bad")
    
    def test_react_component_schema(self):
        """Test React component generation schema"""
        component = GenerateReactComponentInput(
            component_name="TestCard",
            component_pattern="card",
            variant="primary",
            styling="tailwind"
        )
        
        assert component.component_name == "TestCard"
        assert component.component_pattern == "card"
        assert component.variant == "primary"
        assert component.styling == "tailwind"
        assert component.output_dir == "./src/components"  # Default value
        
        # With all parameters
        full_component = GenerateReactComponentInput(
            component_name="CustomButton",
            component_pattern="button",
            variant="secondary",
            styling="tailwind",
            output_dir="./components",
            props=[{"name": "size", "type": "string"}, {"name": "disabled", "type": "boolean"}]
        )
        
        assert full_component.output_dir == "./components"
        assert full_component.props is not None and len(full_component.props) == 2
    
    def test_execution_schema(self):
        """Test command execution schema"""
        cmd = ExecuteCommandInput(
            command="npm install",
            working_dir="./demo"
        )
        
        assert cmd.command == "npm install"
        assert cmd.working_dir == "./demo"
        assert cmd.timeout == 30  # Default value is 30 seconds


class TestToolDictionary:
    """Test that tool_dictionary.json is valid and complete"""
    
    @pytest.fixture
    def tool_dictionary(self) -> Dict[str, Any]:
        """Load tool dictionary"""
        dict_path = Path(__file__).parent.parent.parent / "config" / "tool_dictionary.json"
        with open(dict_path, 'r') as f:
            return json.load(f)
    
    def test_dictionary_structure(self, tool_dictionary):
        """Test that tool dictionary has the correct structure"""
        assert "tools" in tool_dictionary
        assert isinstance(tool_dictionary["tools"], dict)
        
        # Check main categories exist
        categories = [
            "file_operations",
            "code_analysis",
            "execution",
            "git_operations",
            "context_search",
            "ai_assisted"
        ]
        
        for category in categories:
            assert category in tool_dictionary["tools"], f"Missing category: {category}"
    
    def test_tool_definitions(self, tool_dictionary):
        """Test that each tool has required fields"""
        required_fields = [
            "description",
            "category",
            "risk_level",
            "requires_approval",
            "parameters",
            "returns"
        ]
        
        for category, tools in tool_dictionary["tools"].items():
            for tool_name, tool_def in tools.items():
                for field in required_fields:
                    assert field in tool_def, \
                        f"Tool {category}.{tool_name} missing field: {field}"
    
    def test_risk_levels(self, tool_dictionary):
        """Test that all risk levels are valid"""
        valid_levels = ["low", "medium", "high"]
        
        for category, tools in tool_dictionary["tools"].items():
            for tool_name, tool_def in tools.items():
                risk = tool_def.get("risk_level")
                assert risk in valid_levels, \
                    f"Tool {category}.{tool_name} has invalid risk level: {risk}"
    
    def test_file_operations_tools(self, tool_dictionary):
        """Test that file operations tools are properly defined"""
        file_ops = tool_dictionary["tools"]["file_operations"]
        
        # Check essential tools exist
        essential_tools = ["read_file", "write_file", "edit_file", "delete_file", "list_directory"]
        for tool in essential_tools:
            assert tool in file_ops, f"Missing essential file operation: {tool}"
        
        # Check read_file is low risk
        assert file_ops["read_file"]["risk_level"] == "low"
        assert file_ops["read_file"]["requires_approval"] is False
        
        # Check write/delete are high risk
        assert file_ops["write_file"]["risk_level"] == "high"
        assert file_ops["write_file"]["requires_approval"] is True
        assert file_ops["delete_file"]["risk_level"] == "high"
        assert file_ops["delete_file"]["requires_approval"] is True
    
    def test_ai_assisted_tools(self, tool_dictionary):
        """Test that AI-assisted tools are properly defined"""
        ai_tools = tool_dictionary["tools"]["ai_assisted"]
        
        # Check that some AI tools exist
        assert len(ai_tools) > 0, "No AI-assisted tools found"
        
        # Check for common AI tools (some may be in different categories)
        expected_ai_tools = ["generate_tests", "explain_code", "suggest_improvements", "generate_docs"]
        found_tools = [tool for tool in expected_ai_tools if tool in ai_tools]
        assert len(found_tools) > 0, "No expected AI tools found"


class TestSchemaValidation:
    """Test schema validation and error handling"""
    
    def test_invalid_data_rejection(self):
        """Test that invalid data is rejected"""
        
        # Missing required field
        with pytest.raises(Exception):  # Pydantic will raise ValidationError
            ReadFileInput(file_path=None)  # type: ignore - Testing invalid input
        
        # Wrong type
        with pytest.raises(Exception):
            ReadFileInput(file_path=123)  # type: ignore - Testing invalid input
    
    def test_optional_parameters(self):
        """Test that optional parameters work correctly"""
        
        # GenerateReactComponentInput with minimal params
        component = GenerateReactComponentInput(
            component_name="Test",
            component_pattern="card",
            variant="primary",
            styling="tailwind"
        )
        
        # Check defaults
        assert component.output_dir == "./src/components"  # Has default
        assert component.props is None or component.props == []
        
        # ExecuteCommandInput with defaults
        cmd = ExecuteCommandInput(
            command="echo test",
            working_dir="."
        )
        
        assert cmd.timeout == 30  # Default is 30 seconds
    
    def test_schema_serialization(self):
        """Test that schemas can be serialized/deserialized"""
        
        # Create an input
        original = GenerateReactComponentInput(
            component_name="TestCard",
            component_pattern="card",
            variant="primary",
            styling="tailwind",
            props=[{"name": "title", "type": "string"}, {"name": "count", "type": "number"}]
        )
        
        # Serialize to dict
        data = original.model_dump()
        assert isinstance(data, dict)
        assert data["component_name"] == "TestCard"
        
        # Deserialize back
        restored = GenerateReactComponentInput(**data)
        assert restored.component_name == original.component_name
        assert restored.props == original.props
        
        # Serialize to JSON
        json_str = original.model_dump_json()
        assert isinstance(json_str, str)
        
        # Deserialize from JSON
        restored_from_json = GenerateReactComponentInput.model_validate_json(json_str)
        assert restored_from_json.component_name == original.component_name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
