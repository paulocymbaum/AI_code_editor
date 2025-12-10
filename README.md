# AI Coding Agent with Groq - React/TypeScript Code Generator

A robust, production-ready AI coding agent powered by Groq language models, **specialized in generating React, TypeScript, JavaScript, and Next.js code**. This system provides intelligent code generation, refactoring, and project scaffolding through a centralized, well-tested architecture.

## 🎯 Key Features

- **🎨 Professional Design System**: Complete design systems with 282+ design tokens, Tailwind config, and component patterns
- **⚛️ React/TypeScript Specialized**: 42 tools for React components with 12+ pre-built patterns (button, card, form, modal, hero, pricing, etc.)
- **🌓 Dark Mode Ready**: Auto-generated dark mode with proper color overrides and accessibility
- **♿ WCAG AA Compliant**: Built-in accessibility with focus states, reduced motion, and semantic HTML
- **⚡ Lightning Fast**: Powered by Groq's LPU for sub-second response times (llama-3.1-8b-instant)
- **🛠️ Modular Tool System**: 42 tools across 10 categories with centralized schema management
- **🎯 Smart Task Planning**: Intelligent task decomposition with file verification and progress tracking
- **✅ Production Quality**: Built-in TypeScript checking, ESLint, Prettier, and comprehensive health checks
- **🧪 100% Test Coverage**: 9 health check suites with 98+ tests, all passing
- **⚡ Async Architecture**: High-performance async/await throughout with proper error handling

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Request                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AICodeAgent Core                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Task Planner │→ │ Execution    │→ │ Tool         │          │
│  │              │  │ Loop         │  │ Executor     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Tool Registry (42 Tools)                       │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐         │
│  │ File Ops (6)  │ │ JavaScript(8) │ │ Design Sys(1) │         │
│  │ Code Anal(5)  │ │ Page Mgmt(4)  │ │ Redux (1)     │         │
│  │ Execution(4)  │ │ Git Ops (5)   │ │ AI Assist(4)  │         │
│  │ Search (4)    │ │              │ │               │         │
│  └───────────────┘ └───────────────┘ └───────────────┘         │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Centralized Components                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ tool_schemas │  │ Config       │  │ Logging      │          │
│  │ (Single SoT) │  │ Management   │  │ System       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Execution Flow

```
1. User Request → 2. Task Planning → 3. Task Execution Loop
                                            │
                                            ▼
4. Tool Selection ← 5. AI Decision ← 6. Context Analysis
        │
        ▼
7. Tool Execution → 8. Result Validation → 9. File Verification
        │
        ▼
10. Error Handling → 11. Context Update → 12. Next Iteration
        │                                      │
        ▼                                      ▼
13. Max Errors? ──Yes→ Stop          More Tasks? ──No→ Complete
        │                                      │
        No                                     Yes
        │                                      │
        └──────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Redis (optional, for short-term memory)
- PostgreSQL (optional, for long-term storage)
- Groq API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-coding-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

4. Run the agent:
```bash
# Direct execution
python agent_core.py

# Or start API server
python api_server.py
```

## 🚀 Usage

### Quick Start Example

```python
from src.agent_core import AICodeAgent
from dotenv import load_dotenv
import asyncio
import os

# Load environment variables
load_dotenv()

async def main():
    # Initialize agent
    agent = AICodeAgent(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        log_file="agent.log"
    )
    
    # Execute request
    result = await agent.execute(
        """
        Create a React TypeScript component called 'UserCard' that:
        - Takes props: name, email, avatar, role
        - Uses useState for hover state
        - Uses Tailwind CSS for styling
        - Displays user info in a professional card layout
        - Includes accessibility attributes
        - Save to ./demo/src/components/UserCard.tsx
        """,
        max_iterations=10
    )
    
    # Check result
    if result["status"] == "completed":
        print("✅ Component created successfully!")
        print(f"Files created: {result.get('files_created', [])}")
    else:
        print("❌ Task failed:", result.get("error"))

asyncio.run(main())
```

### Create Next.js Applications

```python
result = await agent.execute(
    """
    Create a Next.js 14 blog with:
    - Home page with post list (SSG)
    - Dynamic post pages [slug]
    - API routes for posts
    - TypeScript throughout
    - Tailwind CSS styling
    """
)
```

### Generate API Routes

```python
result = await agent.execute(
    """
    Create REST API for user management:
    - GET /api/users - List users
    - POST /api/users - Create user
    - PUT /api/users/[id] - Update user
    - DELETE /api/users/[id] - Delete user
    Use TypeScript and Next.js App Router
    """
)
```

### REST API

Start the server:
```bash
uvicorn api_server:app --reload
```

Make requests:
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Create a React login form component with TypeScript and validation",
    "max_iterations": 10
  }'
```

### API Endpoints

- `GET /health` - Health check
- `POST /execute` - Execute a coding request
- `POST /tool/execute` - Execute a single tool
- `GET /tools` - List available tools
- `GET /session/{session_id}` - Get session data
- `DELETE /session/{session_id}` - Delete session
- `POST /code/search` - Semantic code search

## 🧪 Health Check System

### Comprehensive Testing Suite

The project includes a robust health check system with **9 test suites** covering **98+ tests**:

```bash
# Run all health checks
python3 tests/health_check/run_health_check.py --quick

# Run specific test suite
pytest tests/health_check/test_parameter_consistency.py -v
```

### Test Suites

| Suite | Tests | Coverage | Status |
|-------|-------|----------|--------|
| **Tool Schemas** | 10 | Schema validation, structure | ✅ 100% |
| **Parameter Consistency** | 90 | Function signatures match schemas | ✅ 100% |
| **Import Consistency** | 8 | No circular imports, syntax errors | ✅ 100% |
| **File Path Validation** | 12 | Correct path handling in tools | ✅ 100% |
| **Tool Registry** | 15 | Tool loading and registration | ✅ 100% |
| **Tool Execution** | 20 | Tool execution and error handling | ✅ 100% |
| **Agent Core** | 12 | Agent initialization and execution | ✅ 100% |
| **Design System** | 8 | Design system generation | ✅ 100% |
| **E2E Integration** | 10 | End-to-end workflows | ✅ 100% |

**Total: 98+ tests, 100% passing, ~74s execution time**

### What's Validated

- ✅ All 42 tools have matching schemas and implementations
- ✅ No circular imports (resolved with lazy loading)
- ✅ File paths handled correctly (demo/ vs src/ confusion fixed)
- ✅ All function signatures match Pydantic schemas
- ✅ Tool registry loads all tools correctly
- ✅ Error handling works (API errors, validation failures)
- ✅ Consecutive error limiting (max 4 errors then stop)
- ✅ Design system generation with proper CSS
- ✅ Component generation with correct paths

## 🛠️ Tool Categories (42 Tools)

### 1. 🎨 Design System (1 tool)
- `generate_design_system` - Complete design systems with 282+ design tokens, Tailwind config, component patterns, dark mode, accessibility

### 2. ⚛️ JavaScript/React/TypeScript (8 tools)
- `generate_react_component` - React components with 12+ patterns, TypeScript, Tailwind/CSS modules
- `generate_nextjs_page` - Next.js pages with SSR/SSG/ISR
- `generate_api_route` - API routes (Next.js, Express, Fastify)
- `typescript_check` - TypeScript type checking
- `eslint_check` - ESLint with auto-fix
- `prettier_format` - Code formatting
- `npm_command` - Execute NPM commands
- `generate_type_definitions` - Generate TS types

### 3. 📄 File Operations (6 tools)
- `read_file`, `write_file`, `edit_file`, `delete_file`, `list_directory`, `search_files`

### 4. 🔍 Code Analysis (5 tools)
- `parse_code`, `find_definitions`, `find_references`, `get_diagnostics`, `analyze_dependencies`

### 5. ▶️ Execution (4 tools)
- `execute_command`, `run_tests`, `validate_syntax`, `benchmark_code`

### 6. 🔀 Git Operations (5 tools)
- `git_status`, `git_diff`, `git_commit`, `git_push`, `create_branch`

### 7. 🔎 Context & Search (4 tools)
- `semantic_search`, `grep_search`, `get_context`, `summarize_codebase`

### 8. 🤖 AI-Assisted (4 tools)
- `generate_tests`, `explain_code`, `suggest_improvements`, `generate_docs`

### 9. 📄 Page Management (4 tools)
- `update_page_imports` - Update imports in existing pages
- `generate_page_with_components` - Generate page + components in one go
- `organize_project_files` - Organize files by type
- `clean_demo_folder` - Clean demo folder safely

### 10. 🔄 Redux State Management (1 tool)
- `generate_redux_setup` - Redux store, slices, and mock data

## ⚙️ Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Model Selection
GROQ_MODEL=llama-3.1-8b-instant    # Fast (recommended)
# GROQ_MODEL=llama-3.1-70b-versatile # More capable but slower

# Agent Behavior
MAX_ITERATIONS=10                   # Maximum execution loop iterations
TOOL_TIMEOUT=30                     # Tool execution timeout (seconds)
CONSECUTIVE_ERROR_LIMIT=4           # Stop after N consecutive errors
ENABLE_SAFETY_CHECKS=true           # Enable safety validations

# Paths
OUTPUT_DIR=./demo                   # Default output directory
CONFIG_DIR=./config                 # Configuration files
COMPONENTS_DIR=./src/components     # Default components directory

# Logging
LOG_LEVEL=INFO                      # Root logger level
FILE_LOG_LEVEL=DEBUG                # File handler level (detailed)
CONSOLE_LOG_LEVEL=INFO              # Console handler level
LOG_DIR=./logs                      # Log files directory

# Optional Features (disabled by default)
ENABLE_REDIS=false                  # Enable Redis for short-term memory
ENABLE_CHROMA=false                 # Enable ChromaDB for vector storage
ENABLE_POSTGRES=false               # Enable PostgreSQL for long-term storage
ENABLE_OBSERVABILITY=true           # Enable observability features

# Debug
DEBUG=false                         # Enable debug mode
```

### Centralized Configuration

All configuration is managed through `src/core/config.py` with type-safe Pydantic models:

```python
from src.core.config import get_settings

settings = get_settings()
print(f"Model: {settings.groq.model}")
print(f"Max iterations: {settings.agent.max_iterations}")
```

## 🎯 Key Improvements (Phase 4 Refactoring)

### 1. Schema Centralization ✅
- **Single Source of Truth**: All 42 tool schemas in `src/tool_schemas.py`
- **No Duplication**: Eliminated 3-way schema duplication (tool files, tool_schemas.py, tool_dictionary.json)
- **No Circular Imports**: Resolved with lazy loading pattern

### 2. Error Handling ✅
- **Comprehensive API Error Handling**: Catches all Groq API exceptions (RateLimitError, AuthenticationError, etc.)
- **Consecutive Error Limiting**: Stops after 4 consecutive errors to prevent infinite loops
- **Validation Counting**: AI hallucinations (claiming done but not verified) count as errors

### 3. File Path Handling ✅
- **Correct Path Resolution**: Fixed bug where tools used wrong src/ path (root vs demo/)
- **file_path Parameter**: Tools now respect file_path parameter correctly
- **Demo Folder Support**: All components created in ./demo/src/ when specified

### 4. Health Check System ✅
- **9 Test Suites**: 98+ tests covering all critical functionality
- **100% Pass Rate**: All tests passing consistently
- **Fast Execution**: ~74s for complete suite, ~13s in quick mode
- **Comprehensive Coverage**: Schemas, imports, parameters, file paths, execution, integration

## 📚 Documentation

### Core Documentation
- **[README.md](README.md)** - This file, project overview
- **[docs/TECHNICAL.md](docs/TECHNICAL.md)** - Technical architecture and implementation
- **[docs/BUSINESS.md](docs/BUSINESS.md)** - Business value and use cases
- **[docs/DESIGN.md](docs/DESIGN.md)** - Design system and UI/UX
- **[docs/TESTING_IMPLEMENTATION.md](docs/TESTING_IMPLEMENTATION.md)** - Health check system details

### Summary Documents
- **[SCHEMA_CENTRALIZATION_COMPLETE.md](SCHEMA_CENTRALIZATION_COMPLETE.md)** - Schema centralization summary
- **[API_ERROR_HANDLING_COMPLETE.md](API_ERROR_HANDLING_COMPLETE.md)** - Error handling implementation
- **[FILE_PATH_BUG_FIX.md](FILE_PATH_BUG_FIX.md)** - File path fix details
- **[HEALTH_CHECK_ENHANCEMENTS_COMPLETE.md](HEALTH_CHECK_ENHANCEMENTS_COMPLETE.md)** - Health check system summary
- **[CODE_REVIEW_SUMMARY.md](CODE_REVIEW_SUMMARY.md)** - Latest code review findings

See **[TESTING.md](TESTING.md)** for comprehensive testing documentation.

## Development

### Project Structure

```
.
├── agent_core.py           # Main agent logic and execution loop
├── memory_manager.py       # Multi-tier memory management
├── api_server.py          # FastAPI REST API
├── config.py              # Configuration management
├── tool_schemas.py        # Pydantic schemas for tools
├── tool_dictionary.json   # Tool metadata registry
├── tools/                 # Tool implementations
│   ├── __init__.py
│   ├── file_operations.py
│   ├── code_analysis.py
│   ├── execution.py
│   ├── git_operations.py
│   ├── context_search.py
│   └── ai_assisted.py
├── tests/                 # Test suites
│   └── health_check/     # Health check system
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── TESTING.md            # Testing documentation
```

### Adding New Tools

1. Define schema in `tool_schemas.py`:
```python
class MyToolInput(BaseModel):
    param1: str = Field(..., description="Parameter description")
```

2. Implement tool in appropriate `tools/*.py` file:
```python
async def my_tool(params: MyToolInput) -> ToolResult:
    # Implementation
    return ToolResult(success=True, data={...})
```

3. Add to `tool_dictionary.json`:
```json
{
  "my_tool": {
    "description": "Tool description",
    "category": "category_name",
    "risk_level": "low",
    "requires_approval": false
  }
}
```

4. Export in `tools/__init__.py`

## Safety & Security

- Command whitelisting for execution tools
- Path traversal prevention
- Resource limits (CPU, memory, timeout)
- Approval required for high-risk operations
- Input validation with Pydantic
- Sandboxed execution environment

## Performance Optimization

- Groq's LPU provides 300-500 tokens/sec
- Async architecture for concurrent operations
- Intelligent context pruning
- Response caching
- Model routing (8B for simple, 70B for complex)

## Monitoring

The system includes built-in observability:

- Prometheus metrics
- Structured logging
- Error tracking (Sentry)
- LLM observability (LangFuse)

## Deployment

### Docker

```bash
docker build -t ai-coding-agent .
docker run -p 8000:8000 --env-file .env ai-coding-agent
```

### Production Considerations

- Use Redis cluster for high availability
- PostgreSQL with replication
- Load balancer for API servers
- Rate limiting per user
- API key authentication
- HTTPS/TLS encryption

## Troubleshooting

### Common Issues

**Agent not responding:**
- Check GROQ_API_KEY is set correctly
- Verify network connectivity to Groq API
- Check rate limits

**Tool execution fails:**
- Verify tool dependencies are installed
- Check file permissions
- Review safety checks configuration

**Memory issues:**
- Reduce MAX_ITERATIONS
- Enable context pruning
- Check Redis/ChromaDB connectivity

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## React/TypeScript Examples

See `examples/react_examples.py` for comprehensive examples:
- Creating React components
- Building Next.js applications
- Generating API routes
- Setting up state management
- Creating custom hooks
- Form validation
- Testing
- Complete project setup

## Documentation

- **[TESTING.md](TESTING.md)** - Comprehensive testing guide and health check system
- **REACT_GUIDE.md** - Complete guide for React/TypeScript code generation
- **SYSTEM_DESIGN.md** - System architecture and design decisions
- **IMPLEMENTATION_GUIDE.md** - Development and deployment guide
- **ARCHITECTURE_SUMMARY.md** - High-level architecture overview

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: See guides above
- Examples: `examples/react_examples.py`

## Acknowledgments

- Groq for fast LLM inference
- React and Next.js communities
- FastAPI for the web framework
- ChromaDB for vector storage
- The open-source community
