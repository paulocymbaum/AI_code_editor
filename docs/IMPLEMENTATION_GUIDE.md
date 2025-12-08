# Implementation Guide

## Step-by-Step Setup

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Configure Groq API

1. Get API key from [Groq Console](https://console.groq.com)
2. Add to `.env`:
```env
GROQ_API_KEY=gsk_your_key_here
```

### 3. Optional: Set Up Memory Infrastructure

#### Redis (Short-term memory)
```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or install locally
# macOS: brew install redis
# Ubuntu: sudo apt-get install redis-server
```

#### ChromaDB (Vector storage)
```bash
# Using Docker
docker run -d -p 8001:8000 chromadb/chroma

# Or install locally
pip install chromadb
```

#### PostgreSQL (Long-term storage)
```bash
# Using Docker
docker run -d \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=ai_agent \
  -p 5432:5432 \
  postgres:15-alpine
```

### 4. Test the Agent

```bash
# Test basic functionality
python agent_core.py

# Run examples
python example_usage.py

# Start API server
python api_server.py
```

### 5. Docker Deployment (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f agent

# Stop services
docker-compose down
```

## Development Workflow

### Adding a New Tool

1. **Define Schema** (`tool_schemas.py`):
```python
class MyNewToolInput(BaseModel):
    param1: str = Field(..., description="Description")
    param2: int = Field(default=10, description="Optional param")
```

2. **Implement Tool** (`tools/category.py`):
```python
async def my_new_tool(params: MyNewToolInput) -> ToolResult:
    try:
        # Your implementation
        result = do_something(params.param1, params.param2)
        
        return ToolResult(
            success=True,
            data={"result": result}
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))
```

3. **Register Tool** (`tool_dictionary.json`):
```json
{
  "my_new_tool": {
    "description": "Does something useful",
    "category": "category_name",
    "risk_level": "low",
    "requires_approval": false,
    "parameters": ["param1", "param2"],
    "returns": "result_data"
  }
}
```

4. **Export Tool** (`tools/__init__.py`):
```python
from .category import my_new_tool

__all__ = [..., 'my_new_tool']
```

5. **Test Tool**:
```python
from tools.category import my_new_tool
from tool_schemas import MyNewToolInput

params = MyNewToolInput(param1="test", param2=20)
result = await my_new_tool(params)
print(result)
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_tools.py

# Run with verbose output
pytest -v
```

### Monitoring

Access monitoring dashboards:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- API Docs: http://localhost:8000/docs

## Production Deployment

### 1. Security Hardening

```python
# config.py - Add authentication
class SecurityConfig(BaseModel):
    api_key_required: bool = True
    allowed_origins: List[str] = ["https://yourdomain.com"]
    rate_limit_per_minute: int = 60
```

### 2. Scaling Strategy

```yaml
# docker-compose.prod.yml
services:
  agent:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### 3. Load Balancing

```nginx
# nginx.conf
upstream agent_backend {
    least_conn;
    server agent1:8000;
    server agent2:8000;
    server agent3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://agent_backend;
    }
}
```

### 4. Database Migrations

```python
# migrations/001_initial.sql
CREATE TABLE sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_created ON sessions(created_at);
```

### 5. Monitoring & Alerts

```yaml
# prometheus/alerts.yml
groups:
  - name: agent_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(agent_errors_total[5m]) > 0.1
        annotations:
          summary: "High error rate detected"
```

## Optimization Tips

### 1. Context Management

```python
# Implement intelligent context pruning
def prune_context(messages: List[Dict], max_tokens: int = 4000):
    # Keep recent messages + relevant history
    recent = messages[-5:]
    relevant = semantic_search(messages[:-5], query=recent[-1])
    return recent + relevant[:3]
```

### 2. Caching

```python
# Cache common responses
from functools import lru_cache

@lru_cache(maxsize=100)
async def cached_tool_execution(tool_name: str, params_hash: str):
    # Execute and cache result
    pass
```

### 3. Parallel Tool Execution

```python
# Execute independent tools in parallel
async def execute_parallel_tools(tools: List[Tuple[str, Dict]]):
    tasks = [execute_tool(name, params) for name, params in tools]
    return await asyncio.gather(*tasks)
```

### 4. Model Selection

```python
# Route to appropriate model based on complexity
def select_model(task_complexity: str) -> str:
    if task_complexity == "simple":
        return "llama-3.1-8b-instant"  # Fast
    else:
        return "llama-3.1-70b-versatile"  # Powerful
```

## Troubleshooting

### Issue: Slow Response Times

**Solution:**
- Use smaller model for simple tasks
- Implement response caching
- Reduce context window size
- Enable parallel tool execution

### Issue: Memory Errors

**Solution:**
- Increase Docker memory limits
- Implement context pruning
- Use streaming responses
- Clear old sessions regularly

### Issue: Tool Execution Failures

**Solution:**
- Check tool dependencies installed
- Verify file permissions
- Review safety checks
- Check timeout settings

### Issue: Rate Limiting

**Solution:**
- Implement exponential backoff
- Use multiple API keys
- Cache responses
- Queue requests

## Best Practices

1. **Always validate inputs** with Pydantic schemas
2. **Use async/await** for I/O operations
3. **Implement proper error handling** with try/except
4. **Log all operations** for debugging
5. **Test tools independently** before integration
6. **Monitor performance metrics** continuously
7. **Keep context focused** and relevant
8. **Use appropriate models** for task complexity
9. **Implement safety checks** for destructive operations
10. **Document all tools** thoroughly

## Next Steps

1. Customize tools for your use case
2. Integrate with your IDE/editor
3. Add custom prompts and templates
4. Implement user authentication
5. Set up CI/CD pipeline
6. Configure monitoring alerts
7. Optimize for your workload
8. Scale horizontally as needed

## Resources

- [Groq Documentation](https://console.groq.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [ChromaDB Documentation](https://docs.trychroma.com)
- [Redis Documentation](https://redis.io/docs)
- [Pydantic Documentation](https://docs.pydantic.dev)
