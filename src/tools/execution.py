"""
Execution Tools
Handles command execution, testing, and benchmarking
"""

import subprocess
import time
from typing import Optional, Dict
from ..tool_schemas import (
    ExecuteCommandInput, RunTestsInput, ValidateSyntaxInput,
    BenchmarkCodeInput, ToolResult
)


async def execute_command(params: ExecuteCommandInput) -> ToolResult:
    """Execute shell command safely"""
    try:
        start_time = time.time()
        
        result = subprocess.run(
            params.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=params.timeout,
            cwd=params.working_dir,
            env=params.env_vars
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        return ToolResult(
            success=result.returncode == 0,
            data={
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            },
            execution_time_ms=execution_time
        )
    except subprocess.TimeoutExpired:
        return ToolResult(success=False, error="Command timed out")
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def run_tests(params: RunTestsInput) -> ToolResult:
    """Run test suite"""
    try:
        commands = {
            "pytest": f"pytest {params.test_path}" + (" --cov" if params.coverage else ""),
            "unittest": f"python -m unittest {params.test_path}",
            "jest": f"jest {params.test_path}" + (" --coverage" if params.coverage else ""),
            "mocha": f"mocha {params.test_path}",
            "vitest": f"vitest run {params.test_path}" + (" --coverage" if params.coverage else "")
        }
        
        command = commands.get(params.framework)
        if not command:
            return ToolResult(success=False, error=f"Unsupported framework: {params.framework}")
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return ToolResult(
            success=result.returncode == 0,
            data={
                "output": result.stdout,
                "errors": result.stderr,
                "passed": result.returncode == 0
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def validate_syntax(params: ValidateSyntaxInput) -> ToolResult:
    """Validate code syntax"""
    try:
        import pathlib
        import ast
        
        file_path = pathlib.Path(params.file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Python syntax validation
        if params.language in [None, "python"] and file_path.suffix == ".py":
            try:
                ast.parse(code)
                return ToolResult(success=True, data={"valid": True, "language": "python"})
            except SyntaxError as e:
                return ToolResult(
                    success=False,
                    data={"valid": False, "error": str(e), "line": e.lineno}
                )
        
        return ToolResult(success=False, error="Unsupported language")
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def benchmark_code(params: BenchmarkCodeInput) -> ToolResult:
    """Benchmark code performance"""
    try:
        import timeit
        
        # Simple benchmarking using timeit
        setup = f"from {params.file_path.replace('.py', '')} import {params.function_name}"
        stmt = f"{params.function_name}()"
        
        time_taken = timeit.timeit(stmt, setup=setup, number=params.iterations)
        avg_time = time_taken / params.iterations
        
        return ToolResult(
            success=True,
            data={
                "total_time": time_taken,
                "avg_time": avg_time,
                "iterations": params.iterations,
                "ops_per_sec": 1 / avg_time if avg_time > 0 else 0
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))
