# Design Document - AI Agent Testing and Fixes

## Overview

This design outlines the approach for testing, fixing, and validating the AI Coding Agent project. The system is a Groq-powered AI assistant specialized in React/TypeScript code generation. The project was "vibecoded" and requires comprehensive testing and bug fixes before generating a React demo.

## Architecture

### Current System Architecture

The system follows a modular architecture:

```
┌─────────────────────────────────────────┐
│         AI Coding Agent                  │
├─────────────────────────────────────────┤
│  Agent Core (agent_core.py)             │
│  ├─ Task Planning                       │
│  ├─ Execution Loop                      │
│  └─ Tool Orchestration                  │
├─────────────────────────────────────────┤
│  Tool System (tools/)                    │
│  ├─ File Operations (6 tools)           │
│  ├─ Code Analysis (5 tools)             │
│  ├─ Execution (4 tools)                 │
│  ├─ Git Operations (5 tools)            │
│  ├─ Context Search (4 tools)            │
│  ├─ AI Assisted (4 tools)               │
│  └─ JavaScript/React (8 tools)          │
├─────────────────────────────────────────┤
│  API Server (api_server.py)             │
│  └─ REST Endpoints                      │
├─────────────────────────────────────────┤
│  Memory Manager (memory_manager.py)     │
│  └─ Multi-tier Storage                  │
└─────────────────────────────────────────┘
```

### Testing Strategy

We'll use a bottom-up testing approach:
1. Fix syntax errors first
2. Test individual tools
3. Test tool integration
4. Test agent core
5. Test API server
6. Generate and test React demo

## Components and Interfaces

### 1. Syntax Error Fixes

**Component**: `tools/javascript_tools.py`

**Issue Identified**: Line 124 has an f-string syntax error

**Fix Strategy**:
- Locate the problematic f-string
- Escape curly braces that are not Python expressions
- Use double braces `{{` and `}}` for literal braces in f-strings

### 2. Tool Registry System

**Component**: `agent_core.py` - `_build_tool_registry()`

**Current Implementation**:
```python
tool_modules = {
    'file_operations': tools.file_operations,
    'code_analysis': tools.code_analysis,
    'execution': tools.execution,
    'git_operations': tools.git_operations,
    'context_search': tools.context_search,
    'ai_assisted': tools.ai_assisted,
}
```

**Issue**: Missing `javascript_tools` module in registry

**Fix**: Add javascript_tools to the tool_modules dictionary

### 3. Tool Validation System

**Interface**:
```python
async def validate_tool(tool_name: str, tool_func: callable) -> ValidationResult:
    """Validate a single tool can be called"""
    pass
```

**Implementation**:
- Check tool exists in TOOL_INPUT_SCHEMAS
- Verify function signature matches schema
- Test with minimal valid parameters
- Catch and report errors

### 4. Agent Core Testing

**Test Cases**:
1. Task planning with simple request
2. Action decision making
3. Tool execution with valid parameters
4. Error handling and retry logic
5. Response synthesis

### 5. API Server Testing

**Endpoints to Test**:
- `GET /health` - Health check
- `POST /execute` - Main execution
- `GET /tools` - List tools
- `POST /tool/execute` - Direct tool execution
- `GET /session/{id}` - Session retrieval
- `DELETE /session/{id}` - Session deletion

### 6. React Demo Generator

**Component**: New tool or script

**Functionality**:
- Generate a complete React application
- Include multiple components
- Add routing
- Include styling (Tailwind CSS)
- Create package.json with dependencies
- Generate README with run instructions

## Data Models

### ToolValidationResult

```python
@dataclass
class ToolValidationResult:
    tool_name: str
    success: bool
    error: Optional[str] = None
    execution_time_ms: float = 0.0
```

### TestResult

```python
@dataclass
class TestResult:
    test_name: str
    passed: bool
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
```

### ReactDemoConfig

```python
@dataclass
class ReactDemoConfig:
    project_name: str = "ai-agent-demo"
    output_dir: str = "./demo"
    components: List[str] = field(default_factory=lambda: ["Header", "Footer", "Card"])
    use_typescript: bool = True
    use_tailwind: bool = True
    include_routing: bool = True
```

## Error Handling

### Error Categories

1. **Syntax Errors**: Python parsing failures
2. **Import Errors**: Missing modules or incorrect imports
3. **Type Errors**: Pydantic validation failures
4. **Runtime Errors**: Tool execution failures
5. **API Errors**: HTTP request/response issues

### Error Handling Strategy

```python
try:
    # Execute operation
    result = await operation()
except SyntaxError as e:
    # Log and fix syntax errors
    log_error("SYNTAX", e)
    fix_syntax_error(e)
except ImportError as e:
    # Log and fix import errors
    log_error("IMPORT", e)
    fix_import_error(e)
except ValidationError as e:
    # Log validation errors
    log_error("VALIDATION", e)
except Exception as e:
    # Log general errors
    log_error("RUNTIME", e)
```

## Testing Strategy

### Unit Testing

**File Operations Tests**:
- Test read_file with existing file
- Test write_file creates file
- Test edit_file modifies content
- Test delete_file removes file
- Test path traversal prevention

**JavaScript Tools Tests**:
- Test generate_react_component creates valid component
- Test generate_nextjs_page creates valid page
- Test generate_api_route creates valid route
- Test typescript_check runs without errors
- Test generated code is syntactically valid

### Integration Testing

**Agent Core Integration**:
- Test complete execution loop
- Test tool selection and execution
- Test error recovery
- Test response synthesis

**API Server Integration**:
- Test all endpoints respond correctly
- Test session management
- Test error responses

### End-to-End Testing

**React Demo Test**:
- Generate complete React application
- Verify all files created
- Install dependencies
- Build application
- Run application
- Verify UI renders correctly

## Implementation Plan

### Phase 1: Fix Syntax Errors (Priority: Critical)

1. Fix f-string error in javascript_tools.py line 124
2. Run Python syntax checker on all files
3. Fix any additional syntax errors found

### Phase 2: Fix Import Errors (Priority: High)

1. Add javascript_tools to agent_core.py tool registry
2. Verify all tool imports in tools/__init__.py
3. Test imports with Python interpreter

### Phase 3: Tool Validation (Priority: High)

1. Create tool validation script
2. Test each tool with minimal parameters
3. Fix any tool implementation errors
4. Document tool test results

### Phase 4: Agent Core Testing (Priority: Medium)

1. Test task planning
2. Test action decision
3. Test tool execution
4. Test error handling
5. Test response synthesis

### Phase 5: API Server Testing (Priority: Medium)

1. Start API server
2. Test health endpoint
3. Test execute endpoint
4. Test tools endpoint
5. Test session endpoints

### Phase 6: React Demo Generation (Priority: High)

1. Design demo application structure
2. Generate components
3. Generate pages
4. Generate API routes
5. Create package.json
6. Create README
7. Test build and run

### Phase 7: Final Validation (Priority: High)

1. Run all tests
2. Verify no errors
3. Document test results
4. Create test report

## Dependencies

### Required Python Packages

- groq (Groq SDK)
- fastapi (API server)
- pydantic (validation)
- chardet (encoding detection)
- python-dotenv (environment variables)

### Optional Python Packages

- redis (short-term memory)
- chromadb (vector storage)
- psycopg2 (PostgreSQL)
- pytest (testing)

### Required Node.js Packages (for React demo)

- react
- react-dom
- next (Next.js)
- typescript
- tailwindcss
- @types/react
- @types/node

## Monitoring and Validation

### Success Criteria

1. All Python files parse without syntax errors
2. All tools can be imported successfully
3. All tools execute without errors (with valid inputs)
4. Agent core completes execution loop
5. API server starts and responds to requests
6. React demo generates successfully
7. React demo builds without errors
8. React demo runs and displays UI

### Validation Checklist

- [ ] Python syntax errors fixed
- [ ] Import errors fixed
- [ ] Tool registry includes all tools
- [ ] All 38+ tools validated
- [ ] Agent core execution tested
- [ ] API server endpoints tested
- [ ] React demo generated
- [ ] React demo builds successfully
- [ ] React demo runs successfully
- [ ] All tests pass

## Risk Mitigation

### Identified Risks

1. **Missing Dependencies**: Some Python packages may not be installed
   - Mitigation: Check requirements.txt and install missing packages

2. **Tool Implementation Errors**: Tools may have logic errors
   - Mitigation: Test each tool individually with valid inputs

3. **API Key Missing**: GROQ_API_KEY may not be set
   - Mitigation: Check .env file and provide clear error messages

4. **Node.js Not Installed**: React demo requires Node.js
   - Mitigation: Check for Node.js installation before generating demo

5. **Port Conflicts**: API server port may be in use
   - Mitigation: Use configurable port or check availability

## Future Enhancements

1. Add comprehensive test suite with pytest
2. Add property-based testing for tools
3. Add performance benchmarks
4. Add integration with CI/CD
5. Add automated error reporting
6. Add test coverage reporting

## Conclusion

This design provides a systematic approach to testing and fixing the AI Coding Agent. By following the phased implementation plan, we'll ensure all components work correctly before generating the final React demo. The bottom-up testing strategy ensures we catch and fix errors early, reducing debugging time later.
