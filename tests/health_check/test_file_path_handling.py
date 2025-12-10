"""
Health Check: File Path Handling in File Generation Tools

Verifies that all file generation tools correctly handle file_path parameter
and respect user-specified paths instead of using incorrect defaults.

This test uses static code analysis and schema validation to ensure:
1. Tools that accept file_path parameter prioritize it over default paths
2. Path handling logic is correct and safe
3. Default paths are appropriate for the tool's purpose
"""

import pytest
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.tool_schemas import TOOL_INPUT_SCHEMAS


class TestFilePathHandling:
    """Test suite for file path handling in file generation tools"""
    
    # Tools that should handle file paths
    FILE_GENERATION_TOOLS = {
        'generate_react_component': {
            'file_path_param': 'file_path',
            'default_dir_param': 'output_dir',
            'expected_default': './src/components',
            'module': 'javascript_tools',
            'required_params': {'component_name': 'Test', 'pattern': 'button'}
        },
        'write_file': {
            'file_path_param': 'file_path',
            'default_dir_param': None,  # No default, path is required
            'expected_default': None,
            'module': 'file_operations',
            'required_params': {'content': 'test'}
        },
        'generate_design_system': {
            'file_path_param': 'css_output_path',
            'default_dir_param': 'project_path',
            'expected_default': None,  # Uses project_path
            'module': 'design_system',
            'required_params': {'project_path': './demo'}
        },
        'generate_page_with_components': {
            'file_path_param': 'page_path',
            'default_dir_param': None,  # page_path is required
            'expected_default': None,
            'module': 'page_management',
            'required_params': {'page_name': 'test', 'components': []}
        }
    }
    
    def test_schemas_have_file_path_parameters(self):
        """Verify file generation tools have proper file path parameters in schemas"""
        for tool_name, config in self.FILE_GENERATION_TOOLS.items():
            # Check if tool exists in schemas
            assert tool_name in TOOL_INPUT_SCHEMAS, \
                f"Tool '{tool_name}' not found in TOOL_INPUT_SCHEMAS"
            
            schema_class = TOOL_INPUT_SCHEMAS[tool_name]
            fields = schema_class.model_fields
            
            file_path_param = config['file_path_param']
            
            # Verify file path parameter exists
            assert file_path_param in fields, \
                f"Tool '{tool_name}' missing '{file_path_param}' parameter in schema"
            
            # Check if parameter has proper description
            field = fields[file_path_param]
            assert field.description, \
                f"Tool '{tool_name}' parameter '{file_path_param}' missing description"
            
            # Verify description mentions path
            desc_lower = field.description.lower()
            assert any(keyword in desc_lower for keyword in ['path', 'file', 'directory']), \
                f"Tool '{tool_name}' parameter '{file_path_param}' description doesn't mention path/file/directory"
    
    def test_tool_implementations_check_file_path(self):
        """Verify tool implementations check file_path parameter before using defaults"""
        for tool_name, config in self.FILE_GENERATION_TOOLS.items():
            module_name = config['module']
            file_path_param = config['file_path_param']
            
            # Load the tool module
            tool_file = project_root / 'src' / 'tools' / f"{module_name}.py"
            
            if not tool_file.exists():
                pytest.skip(f"Tool file {tool_file} not found")
            
            with open(tool_file, 'r') as f:
                source_code = f.read()
            
            # Parse the source code
            try:
                tree = ast.parse(source_code)
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {tool_file}: {e}")
            
            # Find the tool function
            tool_function = self._find_tool_function(tree, tool_name)
            
            if tool_function is None:
                pytest.skip(f"Function for tool '{tool_name}' not found in {module_name}.py")
            
            # Verify the function checks file_path parameter
            checks_file_path = self._function_checks_parameter(tool_function, file_path_param)
            
            assert checks_file_path, \
                f"Tool '{tool_name}' implementation doesn't check '{file_path_param}' parameter"
    
    def test_file_path_prioritization_logic(self):
        """Verify tools prioritize file_path over default directory"""
        critical_tools = ['generate_react_component']
        
        for tool_name in critical_tools:
            config = self.FILE_GENERATION_TOOLS[tool_name]
            module_name = config['module']
            
            tool_file = project_root / 'src' / 'tools' / f"{module_name}.py"
            
            if not tool_file.exists():
                pytest.skip(f"Tool file {tool_file} not found")
            
            with open(tool_file, 'r') as f:
                source_code = f.read()
            
            # Check for if/else pattern that prioritizes file_path
            file_path_param = config['file_path_param']
            
            # Look for pattern: if params.file_path: ... else: ...
            has_prioritization = (
                f"if params.{file_path_param}" in source_code or
                f"params.{file_path_param} or" in source_code or
                f"if {file_path_param}" in source_code
            )
            
            assert has_prioritization, \
                f"Tool '{tool_name}' doesn't have clear file_path prioritization logic"
    
    def test_path_safety_checks(self):
        """Verify tools have path safety checks (no path traversal, etc.)"""
        for tool_name, config in self.FILE_GENERATION_TOOLS.items():
            module_name = config['module']
            
            tool_file = project_root / 'src' / 'tools' / f"{module_name}.py"
            
            if not tool_file.exists():
                continue
            
            with open(tool_file, 'r') as f:
                source_code = f.read()
            
            # Check for PathUtils usage or Path() usage (safer than string manipulation)
            has_safe_path_handling = any([
                'PathUtils' in source_code,
                'pathlib.Path' in source_code,
                'Path(' in source_code,
                '.resolve()' in source_code,
                '.absolute()' in source_code
            ])
            
            assert has_safe_path_handling, \
                f"Tool '{tool_name}' doesn't use safe path handling (PathUtils or pathlib)"
    
    def test_default_paths_are_appropriate(self):
        """Verify default paths make sense for each tool"""
        for tool_name, config in self.FILE_GENERATION_TOOLS.items():
            schema_class = TOOL_INPUT_SCHEMAS[tool_name]
            fields = schema_class.model_fields
            
            default_dir_param = config.get('default_dir_param')
            if not default_dir_param or default_dir_param not in fields:
                continue
            
            field = fields[default_dir_param]
            expected_default = config.get('expected_default')
            
            if expected_default is None:
                continue
            
            # Check if default value matches expected
            actual_default = field.default
            
            # For generate_react_component, verify default is NOT in demo folder
            if tool_name == 'generate_react_component':
                if actual_default and isinstance(actual_default, str):
                    assert not actual_default.startswith('./demo'), \
                        f"Tool '{tool_name}' default path should not be in demo folder (use file_path instead)"
    
    def test_demo_folder_path_handling(self):
        """Verify tools can handle demo folder paths correctly"""
        demo_path_tools = ['generate_react_component', 'generate_page_with_components']
        
        for tool_name in demo_path_tools:
            if tool_name not in TOOL_INPUT_SCHEMAS:
                continue
            
            if tool_name not in self.FILE_GENERATION_TOOLS:
                continue
                
            schema_class = TOOL_INPUT_SCHEMAS[tool_name]
            config = self.FILE_GENERATION_TOOLS[tool_name]
            
            # Try to create instance with demo folder path
            demo_paths = [
                './demo/src/app/page.tsx',
                './demo/src/components/Button.tsx',
                'demo/src/app/products/page.tsx'
            ]
            
            for demo_path in demo_paths:
                try:
                    # Build params with required params from config
                    params = config['required_params'].copy()
                    
                    # Add the file path parameter
                    path_param = config['file_path_param']
                    params[path_param] = demo_path
                    
                    # Should not raise validation error
                    instance = schema_class(**params)
                    
                    # Verify path is preserved
                    actual_path = getattr(instance, path_param)
                    
                    assert actual_path == demo_path, \
                        f"Tool '{tool_name}' modified demo path: {actual_path} != {demo_path}"
                    
                except Exception as e:
                    pytest.fail(f"Tool '{tool_name}' failed to accept demo path '{demo_path}': {e}")
    
    # Helper methods
    
    def _find_tool_function(self, tree: ast.AST, tool_name: str) -> Optional[ast.FunctionDef]:
        """Find the function implementation for a tool"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for function with same name or containing tool name
                if node.name == tool_name or tool_name.replace('_', '') in node.name.replace('_', ''):
                    return node
        return None
    
    def _function_checks_parameter(self, func: ast.FunctionDef, param_name: str) -> bool:
        """Check if function references a specific parameter"""
        for node in ast.walk(func):
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id == 'params':
                    if node.attr == param_name:
                        return True
            elif isinstance(node, ast.Name):
                if node.id == param_name:
                    return True
        return False


class TestAgentCorePathGuidance:
    """Test that agent_core.py provides proper path guidance to the AI"""
    
    def test_system_prompt_mentions_file_path(self):
        """Verify system prompt guides AI to use file_path parameter"""
        agent_file = project_root / 'src' / 'agent_core.py'
        
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Look for system prompt
        assert 'SYSTEM_PROMPT' in content or 'system_prompt' in content or 'System Prompt' in content, \
            "agent_core.py should have a system prompt"
        
        # Check for path-related guidance
        path_keywords = ['file_path', 'path', 'directory', 'demo/src']
        
        has_path_guidance = any(keyword in content for keyword in path_keywords)
        
        assert has_path_guidance, \
            "agent_core.py system prompt should guide AI on path usage"
    
    def test_tool_dictionary_has_path_examples(self):
        """Verify tool_dictionary.json has examples with correct paths"""
        tool_dict_file = project_root / 'config' / 'tool_dictionary.json'
        
        if not tool_dict_file.exists():
            pytest.skip("tool_dictionary.json not found")
        
        import json
        with open(tool_dict_file, 'r') as f:
            tool_dict = json.load(f)
        
        # Check tools that generate files
        tools_section = tool_dict.get('tools', {})
        
        for category, tools in tools_section.items():
            for tool_name, tool_info in tools.items():
                if tool_name in TestFilePathHandling.FILE_GENERATION_TOOLS:
                    # Verify tool has examples
                    examples = tool_info.get('examples', [])
                    
                    if examples:
                        # Check if examples show file_path usage
                        examples_str = str(examples)
                        
                        # Should have at least one example with a path
                        has_path_example = any([
                            'file_path' in examples_str,
                            'page_path' in examples_str,
                            'output_path' in examples_str,
                            'demo/' in examples_str
                        ])
                        
                        assert has_path_example, \
                            f"Tool '{tool_name}' examples should demonstrate path usage"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
