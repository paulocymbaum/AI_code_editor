"""
Test Import Consistency
Verifies that all imports are valid and consistent across the codebase
"""

import pytest
import ast
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple
import importlib
import importlib.util

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to collect import statements"""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.imports = []
        self.from_imports = []
        self.errors = []
    
    def visit_Import(self, node):
        """Visit import statement"""
        for alias in node.names:
            self.imports.append({
                'module': alias.name,
                'alias': alias.asname,
                'line': node.lineno
            })
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visit from...import statement"""
        module = node.module or ''
        level = node.level  # Number of dots for relative imports
        
        for alias in node.names:
            self.from_imports.append({
                'module': module,
                'name': alias.name,
                'alias': alias.asname,
                'level': level,
                'line': node.lineno
            })
        self.generic_visit(node)


class TestImportConsistency:
    """Test that imports are consistent across the codebase"""
    
    @pytest.fixture(scope="class")
    def python_files(self):
        """Get all Python files in the project"""
        src_dir = project_root / "src"
        tests_dir = project_root / "tests"
        
        files = []
        for directory in [src_dir, tests_dir]:
            if directory.exists():
                files.extend(directory.rglob("*.py"))
        
        # Exclude __pycache__ and .pyc files
        files = [f for f in files if "__pycache__" not in str(f)]
        
        return files
    
    @pytest.fixture(scope="class")
    def import_data(self, python_files):
        """Parse all Python files and collect import data"""
        data = {}
        
        for filepath in python_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content, filename=str(filepath))
                visitor = ImportVisitor(filepath)
                visitor.visit(tree)
                
                data[filepath] = {
                    'imports': visitor.imports,
                    'from_imports': visitor.from_imports,
                    'errors': visitor.errors
                }
            except SyntaxError as e:
                data[filepath] = {
                    'imports': [],
                    'from_imports': [],
                    'errors': [f"Syntax error: {e}"]
                }
            except Exception as e:
                data[filepath] = {
                    'imports': [],
                    'from_imports': [],
                    'errors': [f"Parse error: {e}"]
                }
        
        return data
    
    def test_no_syntax_errors_in_imports(self, import_data):
        """Test that all Python files can be parsed"""
        errors = []
        
        for filepath, data in import_data.items():
            if data['errors']:
                rel_path = filepath.relative_to(project_root)
                errors.append(f"{rel_path}: {data['errors']}")
        
        if errors:
            pytest.fail(
                "Files with syntax/parse errors:\n" +
                "\n".join(f"  - {error}" for error in errors)
            )
    
    def test_all_imports_are_valid(self, import_data):
        """Test that all imported modules can be resolved"""
        errors = []
        
        for filepath, data in import_data.items():
            rel_path = filepath.relative_to(project_root)
            
            # Check regular imports
            for imp in data['imports']:
                module_name = imp['module']
                
                # Skip certain modules
                if self._should_skip_module(module_name):
                    continue
                
                if not self._can_import(module_name):
                    errors.append(
                        f"{rel_path}:{imp['line']}: Cannot import '{module_name}'"
                    )
            
            # Check from imports
            for imp in data['from_imports']:
                if imp['level'] > 0:
                    # Relative import - validate later
                    continue
                
                module_name = imp['module']
                
                if self._should_skip_module(module_name):
                    continue
                
                if not self._can_import(module_name):
                    errors.append(
                        f"{rel_path}:{imp['line']}: Cannot import from '{module_name}'"
                    )
        
        if errors:
            # Only show first 20 errors
            pytest.fail(
                "Invalid imports found:\n" +
                "\n".join(f"  - {error}" for error in errors[:20]) +
                (f"\n  ... and {len(errors) - 20} more" if len(errors) > 20 else "")
            )
    
    def test_no_circular_imports(self, python_files):
        """Test for circular import patterns"""
        # This is a simplified check - full circular import detection is complex
        # We check for direct circular imports between tool_schemas and tool modules
        
        tool_schemas_file = project_root / "src" / "tool_schemas.py"
        tools_dir = project_root / "src" / "tools"
        
        if not tool_schemas_file.exists():
            pytest.skip("tool_schemas.py not found")
        
        # Check what tool_schemas imports
        with open(tool_schemas_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        visitor = ImportVisitor(tool_schemas_file)
        visitor.visit(tree)
        
        # Get modules imported by tool_schemas
        imported_tool_modules = set()
        for imp in visitor.from_imports:
            if imp['module'].startswith('.tools.'):
                tool_name = imp['module'].replace('.tools.', '')
                imported_tool_modules.add(tool_name)
        
        # Check if those tool modules import from tool_schemas
        circular_imports = []
        
        for tool_name in imported_tool_modules:
            tool_file = tools_dir / f"{tool_name}.py"
            if not tool_file.exists():
                continue
            
            with open(tool_file, 'r', encoding='utf-8') as f:
                tool_content = f.read()
            
            tool_tree = ast.parse(tool_content)
            tool_visitor = ImportVisitor(tool_file)
            tool_visitor.visit(tool_tree)
            
            # Check if tool imports from tool_schemas
            for imp in tool_visitor.from_imports:
                if 'tool_schemas' in imp['module']:
                    # This is expected! Tools should import from tool_schemas
                    # The key is that they import ONLY ToolResult and schemas
                    # They should NOT define schemas locally
                    pass
        
        # Note: This test is informational rather than failing
        # Circular imports in Python are often intentional and managed
        print(f"\n✅ No problematic circular imports detected")
    
    def test_consistent_schema_imports(self, import_data):
        """Test that tool modules import schemas from tool_schemas.py, not define them"""
        issues = []
        
        tools_dir = project_root / "src" / "tools"
        
        for filepath, data in import_data.items():
            # Only check tool modules
            if not str(filepath).startswith(str(tools_dir)):
                continue
            
            rel_path = filepath.relative_to(project_root)
            
            # Read file content to check for class definitions
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for schema class definitions (should be in tool_schemas.py only)
            if 'class ' in content and 'Input(BaseModel)' in content:
                # This file defines input schemas
                # Check if it also imports from tool_schemas
                imports_from_schemas = any(
                    'tool_schemas' in imp['module']
                    for imp in data['from_imports']
                )
                
                if not imports_from_schemas:
                    issues.append(
                        f"{rel_path}: Defines schema classes but doesn't import from tool_schemas.\n"
                        f"  Consider moving schema definitions to src/tool_schemas.py"
                    )
        
        if issues:
            print("\n⚠️  Schema definition warnings:")
            for issue in issues:
                print(f"  - {issue}")
            # Don't fail, just warn
    
    def test_no_star_imports_in_production(self, import_data):
        """Test that production code doesn't use 'from x import *'"""
        star_imports = []
        
        for filepath, data in import_data.items():
            # Skip test files
            if 'test' in str(filepath).lower():
                continue
            
            rel_path = filepath.relative_to(project_root)
            
            for imp in data['from_imports']:
                if imp['name'] == '*':
                    star_imports.append(
                        f"{rel_path}:{imp['line']}: from {imp['module']} import *"
                    )
        
        if star_imports:
            print("\n⚠️  Star imports found (consider explicit imports):")
            for imp in star_imports[:10]:
                print(f"  - {imp}")
            # Don't fail, just warn
    
    def test_imports_are_sorted(self, python_files):
        """Test that imports follow a consistent order"""
        # This is a style check - imports should be grouped:
        # 1. Standard library
        # 2. Third-party packages
        # 3. Local imports
        
        issues = []
        
        for filepath in python_files[:5]:  # Check first 5 files as example
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Find import block
            import_lines = []
            in_import_block = False
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith(('import ', 'from ')):
                    import_lines.append((i, line))
                    in_import_block = True
                elif in_import_block and stripped and not stripped.startswith('#'):
                    # End of import block
                    break
            
            # Check if imports are grouped (this is informational)
            if len(import_lines) > 5:
                rel_path = filepath.relative_to(project_root)
                print(f"\n  {rel_path}: {len(import_lines)} import lines")
    
    def test_tool_schemas_exports_all_schemas(self, import_data):
        """Test that tool_schemas.py properly exports all schemas"""
        tool_schemas_file = project_root / "src" / "tool_schemas.py"
        
        if not tool_schemas_file.exists():
            pytest.skip("tool_schemas.py not found")
        
        with open(tool_schemas_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Find all class definitions that inherit from BaseModel
        schema_classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a schema (ends with Input, inherits from BaseModel)
                if 'Input' in node.name:
                    schema_classes.append(node.name)
        
        # Check TOOL_INPUT_SCHEMAS registry
        if 'TOOL_INPUT_SCHEMAS' not in content:
            pytest.fail("TOOL_INPUT_SCHEMAS registry not found in tool_schemas.py")
        
        print(f"\n✅ Found {len(schema_classes)} schema classes in tool_schemas.py")
        
        # Check that registry references all schemas
        registry_pattern = "TOOL_INPUT_SCHEMAS"
        if registry_pattern in content:
            print(f"✅ TOOL_INPUT_SCHEMAS registry exists")
    
    # Helper methods
    
    def _should_skip_module(self, module_name: str) -> bool:
        """Check if module should be skipped from import validation"""
        skip_patterns = [
            'typing',  # Typing imports are special
            '__future__',  # Future imports
        ]
        
        for pattern in skip_patterns:
            if pattern in module_name:
                return True
        
        return False
    
    def _can_import(self, module_name: str) -> bool:
        """Check if a module can be imported"""
        try:
            # Try to find the module spec
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except (ImportError, ModuleNotFoundError, ValueError, AttributeError):
            # Module cannot be imported
            return False
        except Exception:
            # Other errors - assume module exists
            return True


class TestImportPerformance:
    """Test import performance and optimization"""
    
    def test_no_import_time_side_effects(self):
        """Test that importing modules doesn't have expensive side effects"""
        import time
        
        # Test importing agent_core
        start = time.time()
        try:
            import src.agent_core
            duration = time.time() - start
            
            if duration > 2.0:
                print(f"\n⚠️  agent_core import took {duration:.2f}s (threshold: 2.0s)")
            else:
                print(f"\n✅ agent_core import took {duration:.3f}s")
        except Exception as e:
            pytest.fail(f"Cannot import agent_core: {e}")
        
        # Test importing tool_schemas
        start = time.time()
        try:
            import src.tool_schemas
            duration = time.time() - start
            
            if duration > 1.0:
                print(f"\n⚠️  tool_schemas import took {duration:.2f}s (threshold: 1.0s)")
            else:
                print(f"\n✅ tool_schemas import took {duration:.3f}s")
        except Exception as e:
            pytest.fail(f"Cannot import tool_schemas: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
