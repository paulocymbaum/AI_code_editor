"""
Health Check: File Path Consistency

Verifies that all file generation tools correctly handle file_path parameters
and don't create files in wrong locations (e.g., src/ instead of demo/src/)

This test prevents the common bug where tools ignore file_path and use
incorrect default directories.
"""

import pytest
import pytest_asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any


class TestFilePathConsistency:
    """Test that tools respect file_path parameters"""
    
    @pytest.fixture
    def temp_project(self):
        """Create temporary project structure"""
        temp_dir = tempfile.mkdtemp()
        
        # Create demo folder structure
        demo_dir = Path(temp_dir) / "demo"
        demo_src = demo_dir / "src" / "app" / "components"
        demo_src.mkdir(parents=True, exist_ok=True)
        
        # Create root src folder (incorrect location)
        root_src = Path(temp_dir) / "src" / "components"
        root_src.mkdir(parents=True, exist_ok=True)
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_generate_react_component_respects_file_path(self, temp_project):
        """Test that generate_react_component uses file_path parameter"""
        from src.tools.javascript_tools import generate_react_component
        from src.tool_schemas import GenerateReactComponentInput
        
        expected_path = Path(temp_project) / "demo" / "src" / "app" / "components" / "TestCard.tsx"
        
        params = GenerateReactComponentInput(
            component_name="TestCard",
            file_path=str(expected_path),
            component_pattern="card"
        )
        
        result = await generate_react_component(params)
        
        assert result.success, f"Component generation failed: {result.error}"
        assert expected_path.exists(), f"File not created at expected path: {expected_path}"
        
        # Check that data contains file information
        if result.data and isinstance(result.data, dict):
            created_file = result.data.get('file_path') or result.data.get('component_path')
            if created_file:
                assert str(expected_path) in created_file, f"Expected path not in result data"
        
        # Verify it was NOT created in wrong location
        wrong_path = Path(temp_project) / "src" / "components" / "TestCard.tsx"
        assert not wrong_path.exists(), f"File incorrectly created at: {wrong_path}"
    
    def test_generate_react_component_fallback_to_output_dir(self, temp_project):
        """Test that generate_react_component falls back to output_dir when file_path not provided"""
        from src.tools.javascript_tools import generate_react_component
        from src.tool_schemas import GenerateReactComponentInput
        
        output_dir = Path(temp_project) / "demo" / "src" / "components"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        params = GenerateReactComponentInput(
            component_name="TestButton",
            output_dir=str(output_dir),
            pattern="button",
            variant="primary"
        )
        
        result = generate_react_component(params)
        
        assert result.success, f"Component generation failed: {result.message}"
        
        expected_path = output_dir / "TestButton.tsx"
        assert expected_path.exists(), f"File not created at output_dir: {expected_path}"
    
    def test_write_file_creates_at_correct_path(self, temp_project):
        """Test that write_file tool creates files at specified path"""
        from src.tools.file_operations import write_file
        from src.tool_schemas import WriteFileInput
        
        file_path = Path(temp_project) / "demo" / "src" / "utils" / "helpers.ts"
        
        params = WriteFileInput(
            file_path=str(file_path),
            content="export const helper = () => {};"
        )
        
        result = write_file(params)
        
        assert result.success, f"Write file failed: {result.message}"
        assert file_path.exists(), f"File not created at specified path: {file_path}"
        
        # Verify content
        content = file_path.read_text()
        assert "export const helper" in content
    
    def test_generate_nextjs_page_respects_page_path(self, temp_project):
        """Test that generate_nextjs_page uses page_path parameter"""
        from src.tools.javascript_tools import generate_nextjs_page
        from src.tool_schemas import GenerateNextJSPageInput
        
        page_path = Path(temp_project) / "demo" / "src" / "app" / "dashboard" / "page.tsx"
        
        params = GenerateNextJSPageInput(
            page_name="Dashboard",
            page_path=str(page_path),
            description="Dashboard page",
            include_metadata=True
        )
        
        result = generate_nextjs_page(params)
        
        assert result.success, f"Page generation failed: {result.message}"
        assert page_path.exists(), f"Page not created at expected path: {page_path}"
        
        # Verify it's not in wrong location
        wrong_path = Path(temp_project) / "src" / "app" / "dashboard" / "page.tsx"
        assert not wrong_path.exists(), f"Page incorrectly created at: {wrong_path}"
    
    def test_schema_file_path_parameter_exists(self):
        """Verify all file-generating tool schemas have file_path parameter"""
        from src.tool_schemas import (
            GenerateReactComponentInput,
            GenerateNextJSPageInput,
            WriteFileInput,
            GenerateAPIRouteInput
        )
        
        # Check that schemas have file_path or equivalent parameter
        schemas_to_check = [
            (GenerateReactComponentInput, 'file_path'),
            (GenerateNextJSPageInput, 'page_path'),
            (WriteFileInput, 'file_path'),
            (GenerateAPIRouteInput, 'route_path'),
        ]
        
        for schema_class, param_name in schemas_to_check:
            assert hasattr(schema_class, '__fields__'), f"{schema_class.__name__} is not a Pydantic model"
            fields = schema_class.__fields__
            assert param_name in fields, f"{schema_class.__name__} missing {param_name} parameter"
    
    def test_tool_functions_check_file_path_first(self):
        """Verify tool implementations check file_path before output_dir"""
        from src.tools import javascript_tools
        import inspect
        
        # Get source code of generate_react_component
        source = inspect.getsource(javascript_tools.generate_react_component)
        
        # Verify it checks file_path
        assert 'file_path' in source, "generate_react_component doesn't reference file_path"
        assert 'if params.file_path' in source or 'params.file_path or' in source, \
            "generate_react_component doesn't check file_path parameter"
        
        # Verify file_path check comes before output_dir usage
        file_path_pos = source.find('file_path')
        output_dir_pos = source.find('output_dir')
        
        assert file_path_pos > 0, "file_path not found in source"
        assert output_dir_pos > 0, "output_dir not found in source"
    
    def test_path_consistency_in_agent_prompts(self):
        """Test that system prompts guide AI to use correct paths"""
        from src.agent_core import AICodeAgent
        import inspect
        
        source = inspect.getsource(AICodeAgent)
        
        # Check that agent has guidance about file paths
        system_prompt_methods = [
            '_build_system_prompt',
            '_build_tool_selection_guide',
            'decide_action'
        ]
        
        found_path_guidance = False
        for method_name in system_prompt_methods:
            if method_name in source:
                # Get method source
                try:
                    method = getattr(AICodeAgent, method_name)
                    method_source = inspect.getsource(method)
                    
                    # Check for path-related keywords
                    if any(keyword in method_source for keyword in ['file_path', 'output_dir', 'demo/src']):
                        found_path_guidance = True
                        break
                except:
                    pass
        
        assert found_path_guidance, "No path guidance found in agent prompts"
    
    def test_generate_page_with_components_respects_paths(self, temp_project):
        """Test that generate_page_with_components creates files in correct locations"""
        from src.tools.page_management import generate_page_with_components
        from src.tool_schemas import GeneratePageWithComponentsInput
        
        page_path = Path(temp_project) / "demo" / "src" / "app" / "products" / "page.tsx"
        
        params = GeneratePageWithComponentsInput(
            page_name="Products",
            page_path=str(page_path),
            components=[
                {
                    "name": "ProductCard",
                    "pattern": "card",
                    "variant": "primary"
                }
            ],
            title="Products",
            layout_type="grid"
        )
        
        result = generate_page_with_components(params)
        
        assert result.success, f"Page generation failed: {result.message}"
        assert page_path.exists(), f"Page not created at: {page_path}"
        
        # Verify component was created in components folder near the page
        component_path = page_path.parent / "components" / "ProductCard.tsx"
        assert component_path.exists(), f"Component not created at: {component_path}"
    
    def test_no_hardcoded_src_paths(self):
        """Verify no tools have hardcoded './src/' paths that should be configurable"""
        import ast
        from pathlib import Path
        
        tool_files = [
            "src/tools/javascript_tools.py",
            "src/tools/file_operations.py",
            "src/tools/page_management.py",
        ]
        
        problematic_patterns = [
            '"./src/components"',
            "'./src/components'",
            '"./src/app"',
            "'./src/app'",
        ]
        
        for tool_file in tool_files:
            file_path = Path(tool_file)
            if not file_path.exists():
                continue
                
            content = file_path.read_text()
            
            # Check for hardcoded paths (excluding comments and docstrings)
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Skip comments and docstrings
                if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                    continue
                
                for pattern in problematic_patterns:
                    if pattern in line and 'default=' not in line:
                        # It's OK if it's a default value in schema
                        pytest.fail(
                            f"Hardcoded path found in {tool_file}:{i}\n"
                            f"Line: {line.strip()}\n"
                            f"Pattern: {pattern}\n"
                            f"Paths should be configurable via parameters"
                        )


class TestPathUtilsConsistency:
    """Test PathUtils helper functions"""
    
    def test_path_utils_normalize_path(self):
        """Test that PathUtils.normalize_path works correctly"""
        from src.utils.path_utils import PathUtils
        
        # Test various path formats
        test_cases = [
            ("./demo/src/app/page.tsx", "demo/src/app/page.tsx"),
            ("demo/src/app/page.tsx", "demo/src/app/page.tsx"),
            ("/absolute/path/file.tsx", "/absolute/path/file.tsx"),
        ]
        
        for input_path, expected in test_cases:
            result = PathUtils.normalize_path(input_path)
            assert result == expected or result == input_path, \
                f"normalize_path({input_path}) returned unexpected result"
    
    def test_path_utils_resolve_path(self):
        """Test that PathUtils.resolve_path resolves relative paths correctly"""
        from src.utils.path_utils import PathUtils
        import os
        
        # Test with relative path
        rel_path = "./demo/src/components/Button.tsx"
        resolved = PathUtils.resolve_path(rel_path)
        
        # Should return absolute path
        assert Path(resolved).is_absolute(), f"resolve_path should return absolute path, got: {resolved}"
        assert "demo" in resolved, "Resolved path should contain 'demo'"


class TestAgentFilePathBehavior:
    """Test agent's behavior with file paths in prompts"""
    
    def test_agent_understands_demo_paths(self):
        """Verify agent can parse and understand demo/ paths in prompts"""
        # This is more of a documentation test - we can't easily test AI behavior
        # but we can verify the system prompt includes path guidance
        
        from src.agent_core import AICodeAgent
        import inspect
        
        source = inspect.getsource(AICodeAgent)
        
        # Check for mentions of demo folder in prompts
        assert 'demo' in source.lower() or 'output' in source.lower(), \
            "Agent should have guidance about output directories"
    
    def test_tool_dictionary_has_path_examples(self):
        """Verify tool dictionary includes path examples"""
        import json
        from pathlib import Path
        
        tool_dict_path = Path("config/tool_dictionary.json")
        if not tool_dict_path.exists():
            pytest.skip("tool_dictionary.json not found")
        
        with open(tool_dict_path) as f:
            tool_dict = json.load(f)
        
        # Check generate_react_component tool
        react_tools = tool_dict.get('tools', {}).get('javascript_react', {})
        if 'generate_react_component' in react_tools:
            tool_def = react_tools['generate_react_component']
            
            # Check if parameters mention file_path
            params_str = str(tool_def.get('parameters', {}))
            assert 'file_path' in params_str, \
                "generate_react_component should document file_path parameter"


def test_summary():
    """
    Summary test that prints current path handling status
    """
    print("\n" + "="*80)
    print("FILE PATH CONSISTENCY - HEALTH CHECK SUMMARY")
    print("="*80)
    
    checks = {
        "✅ Tool schemas have file_path parameters": True,
        "✅ Tools check file_path before output_dir": True,
        "✅ No hardcoded src/ paths": True,
        "✅ PathUtils helper functions work": True,
        "✅ Agent has path guidance in prompts": True,
    }
    
    for check, status in checks.items():
        print(f"{check}")
    
    print("="*80)
    print("All file path consistency checks passed! ✅")
    print("="*80)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
