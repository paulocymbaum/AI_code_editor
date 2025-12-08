"""
FastAPI Server for AI Coding Agent
Provides REST API endpoints
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import uuid

from .agent_core import AICodeAgent
from .memory_manager import MemoryManager


app = FastAPI(
    title="AI Coding Agent API",
    description="Groq-powered AI coding assistant",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
agent = AICodeAgent(groq_api_key=GROQ_API_KEY) if GROQ_API_KEY else None
memory_manager = MemoryManager()


# Request/Response Models
class ExecuteRequest(BaseModel):
    request: str
    session_id: Optional[str] = None
    max_iterations: int = 10
    model: Optional[str] = None


class ExecuteResponse(BaseModel):
    success: bool
    response: str
    session_id: str
    iterations: int
    tool_results: list
    errors: list


class ToolExecuteRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    version: str
    groq_configured: bool


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        groq_configured=GROQ_API_KEY is not None
    )


@app.post("/execute", response_model=ExecuteResponse)
async def execute_request(request: ExecuteRequest):
    """Execute a coding request"""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized. Set GROQ_API_KEY.")
    
    # Generate or use existing session ID
    session_id = request.session_id or str(uuid.uuid4())
    
    # Load conversation history if session exists
    conversation = await memory_manager.get_conversation(session_id)
    
    # Execute request
    result = await agent.execute(
        user_request=request.request,
        max_iterations=request.max_iterations
    )
    
    # Store conversation
    await memory_manager.store_conversation(session_id, conversation)
    
    return ExecuteResponse(
        success=result["success"],
        response=result["response"],
        session_id=session_id,
        iterations=result["iterations"],
        tool_results=result["tool_results"],
        errors=result["errors"]
    )


@app.post("/tool/execute")
async def execute_tool(request: ToolExecuteRequest):
    """Execute a single tool directly"""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    result = await agent.execute_tool(request.tool_name, request.parameters)
    return result.dict()


@app.get("/tools")
async def list_tools():
    """List available tools"""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    tools = []
    for tool_name, tool_info in agent.tool_registry.items():
        schema = tool_info['schema']
        tools.append({
            "name": tool_name,
            "description": schema.__doc__ or "No description",
            "parameters": schema.model_json_schema()
        })
    
    return {"tools": tools, "count": len(tools)}


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session data"""
    conversation = await memory_manager.get_conversation(session_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"session_id": session_id, "conversation": conversation}


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete session"""
    await memory_manager.short_term.delete(f"conversation:{session_id}")
    return {"message": "Session deleted", "session_id": session_id}


@app.post("/code/search")
async def search_code(query: str, top_k: int = 5):
    """Semantic code search"""
    results = await memory_manager.search_code(query, top_k)
    return {"query": query, "results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
