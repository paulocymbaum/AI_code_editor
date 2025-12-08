# AI Coding Agent with Groq - React/TypeScript Code Generator

A robust, production-ready AI coding agent powered by Groq language models, **specialized in generating React, TypeScript, JavaScript, and Next.js code**. This system provides intelligent code generation, refactoring, and project scaffolding through a modular tool architecture.

## Features

- **React/TypeScript Focus**: Generate React components, Next.js pages, API routes, and TypeScript types
- **Fast Inference**: Powered by Groq's LPU for sub-second response times
- **Modular Tool System**: 38+ tools including specialized React/TS tools
- **Multi-Tier Memory**: Redis (short-term), ChromaDB (vector), PostgreSQL (long-term)
- **Task Loop Management**: Intelligent task planning and execution
- **Code Quality**: Built-in TypeScript checking, ESLint, and Prettier
- **REST API**: FastAPI-based API for easy integration
- **Async Architecture**: High-performance async/await throughout

## Architecture

```
User Request → Task Planning → Execution Loop → Tool Selection → 
Tool Execution → Result Processing → Context Update → 
Next Action Decision → Loop or Complete → Response Synthesis
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

## Usage

### Generate React Components

```python
from agent_core import AICodeAgent
import asyncio

async def main():
    agent = AICodeAgent(groq_api_key="your_key")
    
    result = await agent.execute(
        """
        Create a React TypeScript component called 'UserCard' that:
        - Takes props: name, email, avatar
        - Uses useState for hover state
        - Uses Tailwind CSS for styling
        - Displays user info in a card layout
        """
    )
    
    print(result["response"])

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

## Tool Categories

### React/TypeScript/JavaScript (NEW!)
- **generate_react_component**: Create React components (functional/class, TypeScript)
- **generate_nextjs_page**: Generate Next.js pages with SSR/SSG/ISR
- **generate_api_route**: Create API routes (Next.js, Express, Fastify)
- **typescript_check**: Run TypeScript type checking
- **eslint_check**: Run ESLint with auto-fix
- **prettier_format**: Format code with Prettier
- **npm_command**: Execute NPM commands
- **generate_type_definitions**: Generate TS types from JSON/API

### File Operations
- read_file, write_file, edit_file, delete_file
- list_directory, search_files

### Code Analysis
- parse_code, find_definitions, find_references
- get_diagnostics, analyze_dependencies

### Execution
- execute_command, run_tests
- validate_syntax, benchmark_code

### Git Operations
- git_status, git_diff, git_commit
- git_push, create_branch

### Context & Search
- semantic_search, grep_search
- get_context, summarize_codebase

### AI-Assisted
- generate_tests, explain_code
- suggest_improvements, generate_docs

## Configuration

Key configuration options in `.env`:

```env
# Groq Model Selection
GROQ_MODEL=llama-3.1-70b-versatile  # Best for complex tasks
# GROQ_MODEL=llama-3.1-8b-instant   # Faster for simple tasks

# Agent Behavior
MAX_ITERATIONS=10          # Maximum execution loop iterations
TOOL_TIMEOUT=30           # Tool execution timeout (seconds)
ENABLE_SAFETY_CHECKS=true # Enable safety validations
```

## Memory System

### Short-Term Memory (Redis)
- Stores active conversation context
- Session state and recent tool outputs
- TTL: 1-24 hours

### Vector Memory (ChromaDB)
- Semantic code search
- Code embeddings for context retrieval
- Persistent across sessions

### Long-Term Storage (PostgreSQL)
- User preferences and project metadata
- Audit logs and analytics
- Permanent storage

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
├── requirements.txt       # Python dependencies
└── README.md
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
