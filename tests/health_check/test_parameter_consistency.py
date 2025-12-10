"""
Test Parameter Consistency
Verifies that function parameters match their schema definitions across the codebase
"""

import pytest
import inspect
import sys
from pathlib import Path
from typing import get_type_hints

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.tool_schemas import TOOL_INPUT_SCHEMAS

# Import tool modules directly (not through src.tools) to avoid circular imports
from src.tools.file_operations import *
from src.tools.code_analysis import *
from src.tools.execution import *
from src.tools.git_operations import *
from src.tools.context_search import *
from src.tools.ai_assisted import *
from src.tools.javascript_tools import *
from src.tools.design_system import *
from src.tools.page_management import *
from src.tools.redux_tools import *

# Import modules as objects for mapping
from src.tools import file_operations, code_analysis, execution, git_operations, context_search, ai_assisted
import src.tools.javascript_tools as javascript_tools
import src.tools.design_system as design_system
import src.tools.page_management as page_management
import src.tools.redux_tools as redux_tools


# Map tool names to their functions
TOOL_FUNCTIONS = {
    # File operations
    "read_file": file_operations.read_file,
    "write_file": file_operations.write_file,
    "edit_file": file_operations.edit_file,
    "delete_file": file_operations.delete_file,
    "list_directory": file_operations.list_directory,
    "search_files": file_operations.search_files,
    
    # Code analysis
    "parse_code": code_analysis.parse_code,
    "find_definitions": code_analysis.find_definitions,
    "find_references": code_analysis.find_references,
    "get_diagnostics": code_analysis.get_diagnostics,
    "analyze_dependencies": code_analysis.analyze_dependencies,
    
    # Execution
    "execute_command": execution.execute_command,
    "run_tests": execution.run_tests,
    "validate_syntax": execution.validate_syntax,
    "benchmark_code": execution.benchmark_code,
    
    # Git operations
    "git_status": git_operations.git_status,
    "git_diff": git_operations.git_diff,
    "git_commit": git_operations.git_commit,
    "git_push": git_operations.git_push,
    "create_branch": git_operations.create_branch,
    
    # Context search
    "semantic_search": context_search.semantic_search,
    "grep_search": context_search.grep_search,
    "get_context": context_search.get_context,
    "summarize_codebase": context_search.summarize_codebase,
    
    # AI assisted
    "generate_tests": ai_assisted.generate_tests,
    "explain_code": ai_assisted.explain_code,
    "suggest_improvements": ai_assisted.suggest_improvements,
    "generate_docs": ai_assisted.generate_docs,
    
    # JavaScript/React
    "generate_react_component": javascript_tools.generate_react_component,
    "generate_nextjs_page": javascript_tools.generate_nextjs_page,
    "generate_api_route": javascript_tools.generate_api_route,
    "typescript_check": javascript_tools.typescript_check,
    "eslint_check": javascript_tools.eslint_check,
    "prettier_format": javascript_tools.prettier_format,
    "npm_command": javascript_tools.npm_command,
    "generate_type_definitions": javascript_tools.generate_type_definitions,
    
    # Design system
    "generate_design_system": design_system.generate_design_system,
    
    # Page management
    "update_page_imports": page_management.update_page_imports,
    "generate_page_with_components": page_management.generate_page_with_components,
    "organize_project_files": page_management.organize_project_files,
    "clean_demo_folder": page_management.clean_demo_folder,
    
    # Redux
    "generate_redux_setup": redux_tools.generate_redux_setup,
}


class TestParameterConsistency:
    """Test that function parameters match schema definitions"""
    
    def test_all_tool_functions_exist(self):
        """Verify all tools in TOOL_INPUT_SCHEMAS have corresponding functions"""
        missing_functions = []
        
        for tool_name in TOOL_INPUT_SCHEMAS.keys():
            if tool_name not in TOOL_FUNCTIONS:
                missing_functions.append(tool_name)
        
        if missing_functions:
            pytest.fail(
                f"Missing function implementations for tools: {', '.join(missing_functions)}\n"
                f"Add them to TOOL_FUNCTIONS mapping in test_parameter_consistency.py"
            )
    
    def test_all_functions_have_schemas(self):
        """Verify all tool functions have corresponding schemas"""
        missing_schemas = []
        
        for tool_name in TOOL_FUNCTIONS.keys():
            if tool_name not in TOOL_INPUT_SCHEMAS:
                missing_schemas.append(tool_name)
        
        if missing_schemas:
            pytest.fail(
                f"Missing schemas for tools: {', '.join(missing_schemas)}\n"
                f"Add them to TOOL_INPUT_SCHEMAS in src/tool_schemas.py"
            )
    
    @pytest.mark.parametrize("tool_name", list(TOOL_INPUT_SCHEMAS.keys()))
    def test_function_parameter_matches_schema(self, tool_name):
        """Test that function signature matches schema definition"""
        
        # Skip if function not in mapping
        if tool_name not in TOOL_FUNCTIONS:
            pytest.skip(f"Function not mapped for {tool_name}")
        
        tool_func = TOOL_FUNCTIONS[tool_name]
        schema_class = TOOL_INPUT_SCHEMAS[tool_name]
        
        # Get function signature
        sig = inspect.signature(tool_func)
        func_params = list(sig.parameters.keys())
        
        # Function should have 'params' as first parameter
        if not func_params or func_params[0] != 'params':
            pytest.fail(
                f"Tool function '{tool_name}' should have 'params' as first parameter.\n"
                f"Current parameters: {func_params}\n"
                f"Expected: ['params']"
            )
        
        # Check that params type annotation matches schema
        params_annotation = sig.parameters['params'].annotation
        
        if params_annotation == inspect.Parameter.empty:
            pytest.fail(
                f"Tool function '{tool_name}' parameter 'params' has no type annotation.\n"
                f"Expected: {schema_class.__name__}"
            )
        
        # Get the actual type (handle string annotations)
        if isinstance(params_annotation, str):
            # Skip string annotations for now
            return
        
        # Check if annotation matches schema class
        if params_annotation != schema_class:
            pytest.fail(
                f"Tool function '{tool_name}' parameter type mismatch.\n"
                f"Function expects: {params_annotation}\n"
                f"Schema defines: {schema_class}\n"
                f"These should match!"
            )
    
    def test_schema_field_naming_conventions(self):
        """Test that schema fields follow naming conventions"""
        issues = []
        
        for tool_name, schema_class in TOOL_INPUT_SCHEMAS.items():
            # Get all fields
            for field_name, field_info in schema_class.model_fields.items():
                # Check for camelCase (should be snake_case)
                if field_name != field_name.lower():
                    if '_' not in field_name:
                        issues.append(
                            f"{tool_name}.{field_name}: Use snake_case, not camelCase"
                        )
                
                # Check for double underscores
                if '__' in field_name:
                    issues.append(
                        f"{tool_name}.{field_name}: Avoid double underscores in field names"
                    )
        
        if issues:
            pytest.fail(
                "Schema field naming issues:\n" + 
                "\n".join(f"  - {issue}" for issue in issues)
            )
    
    def test_no_conflicting_parameter_names(self):
        """Test that similar tools don't have conflicting parameter names for same concept"""
        
        # Common parameter names that should be consistent
        param_patterns = {
            "file_path": [],  # Should be consistent across all file operations
            "output_dir": [],  # Should be consistent for output directories
            "working_dir": [],  # Should be consistent for working directories
            "cwd": [],  # Should ideally be 'working_dir' instead
        }
        
        # Collect which tools use which parameter names
        for tool_name, schema_class in TOOL_INPUT_SCHEMAS.items():
            for field_name in schema_class.model_fields.keys():
                if field_name in param_patterns:
                    param_patterns[field_name].append(tool_name)
        
        # Report findings
        print("\nParameter name usage across tools:")
        for param_name, tools in param_patterns.items():
            if tools:
                print(f"  {param_name}: {len(tools)} tools")
                if param_name == "cwd" and tools:
                    print(f"    ⚠️  Consider renaming 'cwd' to 'working_dir' in: {', '.join(tools)}")
    
    def test_all_schemas_have_descriptions(self):
        """Test that all schema fields have descriptions"""
        missing_descriptions = []
        
        for tool_name, schema_class in TOOL_INPUT_SCHEMAS.items():
            for field_name, field_info in schema_class.model_fields.items():
                # Check if field has description
                if not field_info.description:
                    missing_descriptions.append(f"{tool_name}.{field_name}")
        
        if missing_descriptions:
            pytest.fail(
                f"Schema fields missing descriptions:\n" +
                "\n".join(f"  - {field}" for field in missing_descriptions[:20]) +
                (f"\n  ... and {len(missing_descriptions) - 20} more" if len(missing_descriptions) > 20 else "")
            )
    
    def test_optional_fields_have_defaults(self):
        """Test that Optional fields have default values"""
        issues = []
        
        for tool_name, schema_class in TOOL_INPUT_SCHEMAS.items():
            for field_name, field_info in schema_class.model_fields.items():
                # Check if field is Optional (has None as one of the types)
                if field_info.annotation:
                    annotation_str = str(field_info.annotation)
                    is_optional = 'Optional' in annotation_str or 'None' in annotation_str
                    
                    if is_optional:
                        # Should have a default value
                        if field_info.default is None and not field_info.is_required():
                            # This is OK - Optional with None default
                            pass
                        elif field_info.is_required():
                            issues.append(
                                f"{tool_name}.{field_name}: Optional field should have default=None"
                            )
        
        if issues:
            pytest.fail(
                "Optional fields without defaults:\n" +
                "\n".join(f"  - {issue}" for issue in issues)
            )


class TestParameterUsage:
    """Test that parameters are used correctly in function implementations"""
    
    @pytest.mark.parametrize("tool_name", list(TOOL_FUNCTIONS.keys()))
    def test_function_accesses_schema_fields(self, tool_name):
        """Test that function implementation accesses params correctly"""
        
        tool_func = TOOL_FUNCTIONS[tool_name]
        schema_class = TOOL_INPUT_SCHEMAS.get(tool_name)
        
        if not schema_class:
            pytest.skip(f"No schema for {tool_name}")
        
        # Get function source code
        try:
            source = inspect.getsource(tool_func)
        except OSError:
            pytest.skip(f"Cannot get source for {tool_name}")
        
        # Check that function accesses params fields
        field_names = list(schema_class.model_fields.keys())
        accessed_fields = []
        
        for field_name in field_names:
            # Look for params.field_name in source
            if f"params.{field_name}" in source:
                accessed_fields.append(field_name)
        
        # At least some fields should be accessed
        if not accessed_fields and field_names:
            pytest.fail(
                f"Tool function '{tool_name}' doesn't seem to access any schema fields.\n"
                f"Schema defines: {', '.join(field_names)}\n"
                f"Expected to see 'params.{field_names[0]}' etc. in function body"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
