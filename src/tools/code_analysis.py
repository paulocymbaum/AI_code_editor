"""
Code Analysis Tools
Provides AST parsing, symbol finding, and diagnostics
"""

import ast
import pathlib
from typing import Optional, List, Dict, Any
from ..tool_schemas import (
    ParseCodeInput, FindDefinitionsInput, FindReferencesInput,
    GetDiagnosticsInput, AnalyzeDependenciesInput, ToolResult
)


async def parse_code(params: ParseCodeInput) -> ToolResult:
    """Parse code into AST structure"""
    try:
        file_path = pathlib.Path(params.file_path)
        
        if not file_path.exists():
            return ToolResult(success=False, error=f"File not found: {params.file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Parse Python code (extend for other languages)
        if params.language in [None, "python"] and file_path.suffix == ".py":
            tree = ast.parse(code)
            
            # Extract structure
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
            
            return ToolResult(
                success=True,
                data={
                    "functions": functions,
                    "classes": classes,
                    "imports": imports,
                    "language": "python"
                }
            )
        
        return ToolResult(success=False, error="Unsupported language")
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def find_definitions(params: FindDefinitionsInput) -> ToolResult:
    """Find symbol definitions"""
    try:
        # Simplified implementation - would use LSP in production
        locations = []
        
        if params.file_path:
            search_paths = [pathlib.Path(params.file_path)]
        else:
            search_paths = pathlib.Path('.').rglob('*.py')
        
        for file_path in search_paths:
            if file_path.is_file():
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if f"def {params.symbol_name}" in line or f"class {params.symbol_name}" in line:
                            locations.append({
                                "file": str(file_path),
                                "line": line_num,
                                "content": line.strip()
                            })
        
        return ToolResult(success=True, data={"locations": locations})
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def find_references(params: FindReferencesInput) -> ToolResult:
    """Find all references to a symbol"""
    try:
        references = []
        
        for file_path in pathlib.Path('.').rglob('*.py'):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if params.symbol_name in line:
                        references.append({
                            "file": str(file_path),
                            "line": line_num,
                            "content": line.strip()
                        })
        
        return ToolResult(success=True, data={"references": references[:100]})
    except Exception as e:
        return ToolResult(success=False, error=str(e))



async def get_diagnostics(params: GetDiagnosticsInput) -> ToolResult:
    """Run linting and type checking"""
    try:
        import subprocess
        
        file_path = pathlib.Path(params.file_path)
        diagnostics = []
        
        if params.check_style:
            # Run ruff for linting
            result = subprocess.run(
                ['ruff', 'check', str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.stdout:
                diagnostics.append({"type": "lint", "output": result.stdout})
        
        if params.check_types:
            # Run mypy for type checking
            result = subprocess.run(
                ['mypy', str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.stdout:
                diagnostics.append({"type": "type", "output": result.stdout})
        
        return ToolResult(success=True, data={"diagnostics": diagnostics})
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def analyze_dependencies(params: AnalyzeDependenciesInput) -> ToolResult:
    """Analyze code dependencies"""
    try:
        root = pathlib.Path(params.root_path)
        dependencies = {}
        
        for py_file in root.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
                
                dependencies[str(py_file)] = imports
        
        return ToolResult(success=True, data={"dependencies": dependencies})
    except Exception as e:
        return ToolResult(success=False, error=str(e))
