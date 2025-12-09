# Health Check Test Suite

This directory contains the comprehensive health check system for the AI Code Editor.

## Quick Start

```bash
# Run all tests
python3 tests/health_check/run_health_check.py

# Quick mode
python3 tests/health_check/run_health_check.py --quick

# Verbose
python3 tests/health_check/run_health_check.py --verbose
```

## Test Files

- **`run_health_check.py`** - Main test runner with reporting
- **`test_tool_schemas.py`** - Schema validation tests (12 tests)
- **`test_tool_registry.py`** - Tool import and registry tests (20+ tests)
- **`test_tool_execution.py`** - Tool execution tests (15+ tests)
- **`test_agent_core.py`** - Agent functionality tests (17 tests)
- **`test_design_system.py`** - Design system tests (comprehensive)
- **`test_e2e_design_system.py`** - End-to-end integration tests

## What Gets Validated

✅ **Tool System**
- All schemas are correctly defined
- Tools can be imported and registered
- Tool execution works
- Error handling is proper

✅ **Agent Core**
- Agent initializes correctly
- Tool registry is populated
- Configuration works
- Basic execution works

✅ **Design System**
- Design tokens are valid
- Tailwind config generates correctly
- CSS is properly structured
- Component patterns work

✅ **File Operations**
- Read/write/delete operations
- Directory operations
- Nested directory creation
- Error handling

✅ **Code Generation**
- React components generate
- Design system generates
- Files are in correct locations
- Content is valid

## Running Individual Tests

```bash
# Run specific test file
python3 -m pytest tests/health_check/test_tool_schemas.py -v

# Run specific test class
python3 -m pytest tests/health_check/test_tool_schemas.py::TestToolSchemas -v

# Run specific test method
python3 -m pytest tests/health_check/test_tool_schemas.py::TestToolSchemas::test_tool_result_schema -v
```

## Test Reports

After running, check `health_check_report.json` in the project root for detailed results.

## Environment

Some tests require:
- **GROQ_API_KEY** (optional) - For agent execution tests
- All Python dependencies installed

Tests that require API key will be skipped if not set.

## See Also

- [Full Testing Documentation](../../TESTING.md)
- [Project README](../../README.md)
