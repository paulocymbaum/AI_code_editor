# Testing Guide

## Health Check System

The AI Code Editor includes a comprehensive health check system to validate that all components are working correctly.

### Quick Start

Run the complete health check:

```bash
python3 tests/health_check/run_health_check.py
```

Run in quick mode (skips long-running tests):

```bash
python3 tests/health_check/run_health_check.py --quick
```

Run with verbose output:

```bash
python3 tests/health_check/run_health_check.py --verbose
```

### Test Suites

The health check system includes the following test suites:

#### 1. Tool Schema Validation (`test_tool_schemas.py`)
- Validates that all tool schemas are correctly defined
- Checks that schemas match the tool_dictionary.json
- Tests schema validation and error handling
- Verifies serialization/deserialization

**What it checks:**
- Tool input schemas are properly defined
- Tool dictionary structure is valid
- Risk levels are correctly set
- Schema validation works correctly

#### 2. Tool Registry & Imports (`test_tool_registry.py`)
- Tests that all tool modules can be imported
- Validates tool registration
- Checks tool function signatures
- Verifies tool error handling

**What it checks:**
- All tool modules can be imported
- Tools are registered correctly
- Tool functions have correct signatures
- Tools return ToolResult format
- Error handling works properly

#### 3. Tool Execution (`test_tool_execution.py`)
- Tests actual tool execution
- Validates file operations
- Tests design system generation
- Tests React component generation

**What it checks:**
- File read/write operations work
- Directory operations work
- Design system generates correctly
- React components generate correctly
- Tool results are in correct format

#### 4. Agent Core Functionality (`test_agent_core.py`)
- Tests agent initialization
- Validates tool registry in agent
- Tests agent execution (requires API key)
- Checks agent configuration

**What it checks:**
- Agent initializes correctly
- Tool registry is populated
- Agent can execute requests
- Configuration options work
- Iteration limits are respected

#### 5. Design System Tests (`test_design_system.py`)
- Comprehensive design system tests
- Tests design tokens
- Tests component patterns
- Tests Tailwind integration

**What it checks:**
- Design tokens are properly defined
- Tailwind config is generated correctly
- Global CSS is properly structured
- Component patterns are available

#### 6. End-to-End Integration (`test_e2e_design_system.py`)
- Complete workflow tests
- Tests full design system generation
- Tests multiple component generation
- Validates complete project setup

**What it checks:**
- Complete workflow from design system to components
- Multiple components can be generated
- Files are created in correct locations
- Component content is valid

### Running Individual Test Suites

You can run individual test suites using pytest:

```bash
# Run tool schema tests
python3 -m pytest tests/health_check/test_tool_schemas.py -v

# Run tool registry tests
python3 -m pytest tests/health_check/test_tool_registry.py -v

# Run tool execution tests
python3 -m pytest tests/health_check/test_tool_execution.py -v

# Run agent core tests
python3 -m pytest tests/health_check/test_agent_core.py -v

# Run design system tests
python3 -m pytest tests/health_check/test_design_system.py -v

# Run e2e tests
python3 -m pytest tests/health_check/test_e2e_design_system.py -v
```

### Running Specific Tests

Run a specific test class:

```bash
python3 -m pytest tests/health_check/test_tool_schemas.py::TestToolSchemas -v
```

Run a specific test method:

```bash
python3 -m pytest tests/health_check/test_tool_schemas.py::TestToolSchemas::test_tool_result_schema -v
```

### Environment Setup

Some tests require environment configuration:

1. **GROQ_API_KEY** (optional): Required for agent execution tests
   ```bash
   export GROQ_API_KEY="your-api-key-here"
   ```
   Or add to `.env` file:
   ```
   GROQ_API_KEY=your-api-key-here
   ```

2. **Python dependencies**: Install required packages
   ```bash
   pip install -r requirements.txt
   ```

### Test Reports

After running the health check, a JSON report is generated:

```
health_check_report.json
```

The report contains:
- Timestamp of the test run
- Total duration
- Results for each test suite
- Pass/fail counts
- Detailed test output

### Continuous Integration

The health check system is designed to be used in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Health Check
  run: python3 tests/health_check/run_health_check.py --quick
```

### What Gets Validated

The health check system validates:

✅ **Tool System**
- All tool schemas are correctly defined
- Tools can be imported and registered
- Tool execution works correctly
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
- Read/write operations work
- Directory operations work
- Nested directory creation works
- File deletion works

✅ **Code Generation**
- React components generate correctly
- Design system generates correctly
- Pages can be created
- Files are in correct locations

### Troubleshooting

**Tests are failing:**
1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Ensure you're in the project root directory
3. Check the detailed error output with `--verbose` flag
4. Review the `health_check_report.json` for details

**API key tests are skipped:**
- These tests require a valid GROQ_API_KEY
- Set the environment variable or add to `.env` file
- Tests will be skipped if key is not set (this is normal)

**Import errors:**
- Ensure you're running from the project root
- Check that `src` directory is in Python path
- Verify all source files exist

### Test Organization

```
tests/health_check/
├── __init__.py                    # Package initialization
├── run_health_check.py            # Main test runner
├── test_tool_schemas.py           # Schema validation tests
├── test_tool_registry.py          # Tool import and registry tests
├── test_tool_execution.py         # Tool execution tests
├── test_agent_core.py             # Agent functionality tests
├── test_design_system.py          # Design system tests
└── test_e2e_design_system.py      # Integration tests
```

### Best Practices

1. **Run health check before committing** to ensure changes don't break functionality
2. **Use quick mode for rapid feedback** during development
3. **Run full test suite before releases** to catch all issues
4. **Check the JSON report** for detailed information on failures
5. **Add new tests** when adding new features or tools

### Adding New Tests

To add new tests:

1. Create a new test file in `tests/health_check/`
2. Follow the existing test structure
3. Add the test file to `run_health_check.py` test modules list
4. Use descriptive test names and docstrings
5. Include both positive and negative test cases

Example:

```python
import pytest

class TestMyNewFeature:
    """Test my new feature"""
    
    def test_feature_works(self):
        """Test that feature works correctly"""
        # Test implementation
        assert True
    
    def test_feature_error_handling(self):
        """Test that feature handles errors"""
        # Test implementation
        assert True
```

### Support

For issues or questions about testing:
1. Check the test output for specific error messages
2. Review the health check report JSON
3. Look at individual test files for examples
4. Check that environment is properly configured
