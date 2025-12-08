# Project Structure

## Overview
This is an AI coding agent system powered by Groq, specialized in generating **React, TypeScript, JavaScript, and Next.js** code.

## Directory Structure

```
.
├── agent_core.py                 # Main agent execution engine
├── api_server.py                 # FastAPI REST API server
├── config.py                     # Configuration management
├── memory_manager.py             # Multi-tier memory system
├── tool_schemas.py               # Pydantic schemas for all tools
├── tool_dictionary.json          # Tool metadata registry
│
├── tools/                        # Tool implementations
│   ├── __init__.py              # Tool exports
│   ├── file_operations.py       # File I/O tools
│   ├── code_analysis.py         # Code parsing and analysis
│   ├── execution.py             # Command execution
│   ├── git_operations.py        # Git/version control
│   ├── context_search.py        # Search and context retrieval
│   ├── ai_assisted.py           # AI-powered tools
│   └── javascript_tools.py      # React/TS/JS code generation ⭐
│
├── examples/                     # Usage examples
│   └── react_examples.py        # React/TypeScript examples ⭐
│
├── docs/                         # Documentation
│   ├── README.md                # Main documentation
│   ├── REACT_GUIDE.md           # React/TS development guide ⭐
│   ├── QUICK_REFERENCE.md       # Quick command reference ⭐
│   ├── SYSTEM_DESIGN.md         # Architecture documentation
│   ├── IMPLEMENTATION_GUIDE.md  # Setup and development guide
│   └── ARCHITECTURE_SUMMARY.md  # High-level overview
│
├── docker-compose.yml           # Docker services configuration
├── Dockerfile                   # Container definition
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── prometheus.yml               # Monitoring configuration
└── quickstart.sh               # Quick setup script
```

## Key Files

### Core System Files

**agent_core.py**
- Main agent execution loop
- Task planning and management
- Tool orchestration
- Groq LLM integration

**api_server.py**
- FastAPI REST API
- Endpoints for code generation
- Session management
- Tool execution API

**memory_manager.py**
- Redis (short-term memory)
- ChromaDB (vector storage)
- PostgreSQL (long-term storage)
- Context management

**config.py**
- Environment configuration
- API keys and settings
- Database connections

### Tool System

**tool_schemas.py**
- Pydantic models for validation
- Input/output schemas
- Type definitions

**tool_dictionary.json**
- Tool metadata
- Risk levels
- Parameter definitions

**tools/javascript_tools.py** ⭐
- React component generation
- Next.js page creation
- API route generation
- TypeScript type checking
- ESLint and Prettier integration
- NPM command execution
- Type definition generation

### Documentation

**REACT_GUIDE.md** ⭐
- Complete guide for React/TypeScript development
- Tool reference
- Best practices
- Common use cases

**QUICK_REFERENCE.md** ⭐
- Quick command reference
- Common patterns
- Troubleshooting

**SYSTEM_DESIGN.md**
- Architecture overview
- Design decisions
- Technology stack
- Scalability strategy

**IMPLEMENTATION_GUIDE.md**
- Setup instructions
- Development workflow
- Deployment guide
- Optimization tips

### Examples

**examples/react_examples.py** ⭐
- React component generation
- Next.js app creation
- API route generation
- Form validation
- Custom hooks
- State management
- Testing
- Complete project setup

## Tool Categories

### 1. React/TypeScript/JavaScript (8 tools) ⭐
Primary focus for code generation:
- generate_react_component
- generate_nextjs_page
- generate_api_route
- typescript_check
- eslint_check
- prettier_format
- npm_command
- generate_type_definitions

### 2. File Operations (6 tools)
- read_file
- write_file
- edit_file
- delete_file
- list_directory
- search_files

### 3. Code Analysis (5 tools)
- parse_code
- find_definitions
- find_references
- get_diagnostics
- analyze_dependencies

### 4. Execution (4 tools)
- execute_command
- run_tests
- validate_syntax
- benchmark_code

### 5. Git Operations (5 tools)
- git_status
- git_diff
- git_commit
- git_push
- create_branch

### 6. Context & Search (4 tools)
- semantic_search
- grep_search
- get_context
- summarize_codebase

### 7. AI-Assisted (4 tools)
- generate_tests
- explain_code
- suggest_improvements
- generate_docs

**Total: 38 tools**

## Data Flow

```
User Request
    ↓
API Server (api_server.py)
    ↓
Agent Core (agent_core.py)
    ↓
Task Planning (Groq LLM)
    ↓
Execution Loop:
    - Tool Selection
    - Parameter Validation (tool_schemas.py)
    - Tool Execution (tools/*.py)
    - Result Processing
    - Context Update (memory_manager.py)
    ↓
Response Synthesis (Groq LLM)
    ↓
Return to User
```

## Technology Stack

### Backend (Python)
- Python 3.11+
- FastAPI (API framework)
- Pydantic v2 (validation)
- Groq SDK (LLM inference)

### Target Languages (Code Generation)
- React (UI components)
- TypeScript (type-safe code)
- JavaScript (ES6+)
- Next.js (full-stack apps)

### Memory & Storage
- Redis (short-term)
- ChromaDB (vector)
- PostgreSQL (long-term)

### Code Quality Tools
- TypeScript Compiler
- ESLint
- Prettier
- Jest/Vitest

### Infrastructure
- Docker & Docker Compose
- Prometheus (metrics)
- Grafana (visualization)
- Nginx (load balancing)

## Getting Started

1. **Quick Start**
   ```bash
   ./quickstart.sh
   ```

2. **Manual Setup**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Add GROQ_API_KEY to .env
   python api_server.py
   ```

3. **Docker**
   ```bash
   docker-compose up
   ```

4. **Run Examples**
   ```bash
   python examples/react_examples.py
   ```

## Key Features

✅ React component generation (functional/class)
✅ Next.js page creation (SSR/SSG/ISR)
✅ API route generation (Next.js/Express/Fastify)
✅ TypeScript type checking
✅ ESLint with auto-fix
✅ Prettier formatting
✅ Custom hooks creation
✅ State management setup
✅ Form validation
✅ Test generation
✅ Complete project scaffolding

## Use Cases

1. **Component Development**: Generate React components with TypeScript
2. **Next.js Apps**: Build complete Next.js applications
3. **API Development**: Create REST API routes
4. **Type Safety**: Generate TypeScript types from JSON/APIs
5. **Code Quality**: Run type checking, linting, formatting
6. **Testing**: Generate comprehensive test suites
7. **Refactoring**: Convert JavaScript to TypeScript
8. **Project Setup**: Initialize new projects with best practices

## Documentation Guide

- **New to the project?** Start with `README.md`
- **Want to generate React code?** Read `REACT_GUIDE.md`
- **Need quick commands?** Check `QUICK_REFERENCE.md`
- **Understanding architecture?** See `SYSTEM_DESIGN.md`
- **Setting up for development?** Follow `IMPLEMENTATION_GUIDE.md`
- **Looking for examples?** Run `examples/react_examples.py`

## Support

For questions or issues:
1. Check the relevant documentation file
2. Review examples in `examples/`
3. Examine tool implementations in `tools/`
4. Open an issue on GitHub

## License

MIT License - See LICENSE file for details
