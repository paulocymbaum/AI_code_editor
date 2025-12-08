"""
AI Coding Agent Core
Main execution loop and task management
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import time

from groq import AsyncGroq
from tool_schemas import ToolResult, TOOL_INPUT_SCHEMAS
import tools


class ActionType(str, Enum):
    """Types of actions the agent can take"""
    TOOL_USE = "tool_use"
    COMPLETE = "complete"
    CLARIFY = "clarify"
    ERROR = "error"


@dataclass
class AgentContext:
    """Context maintained throughout agent execution"""
    user_request: str
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[ToolResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    iteration: int = 0
    max_iterations: int = 10
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def add_tool_result(self, tool_name: str, result: ToolResult):
        """Add tool execution result"""
        self.tool_results.append(result)
        self.add_message("assistant", f"Tool: {tool_name}\nResult: {json.dumps(result.dict(), indent=2)}")
    
    def add_error(self, error: str):
        """Add error to context"""
        self.errors.append(error)
        self.add_message("system", f"Error: {error}")


@dataclass
class AgentAction:
    """Action to be taken by the agent"""
    type: ActionType
    tool_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    reasoning: Optional[str] = None


class AICodeAgent:
    """Main AI Coding Agent with Groq integration"""
    
    def __init__(self, groq_api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = AsyncGroq(api_key=groq_api_key)
        self.model = model
        self.tool_registry = self._build_tool_registry()
    
    def _build_tool_registry(self) -> Dict[str, Any]:
        """Build registry of available tools"""
        registry = {}
        
        # Map tool names to implementations
        tool_modules = {
            'file_operations': tools.file_operations,
            'code_analysis': tools.code_analysis,
            'execution': tools.execution,
            'git_operations': tools.git_operations,
            'context_search': tools.context_search,
            'ai_assisted': tools.ai_assisted,
            'javascript_tools': tools.javascript_tools,
        }
        
        for module_name, module in tool_modules.items():
            for attr_name in dir(module):
                if not attr_name.startswith('_') and callable(getattr(module, attr_name)):
                    func = getattr(module, attr_name)
                    if attr_name in TOOL_INPUT_SCHEMAS:
                        registry[attr_name] = {
                            'function': func,
                            'schema': TOOL_INPUT_SCHEMAS[attr_name]
                        }
        
        return registry

    
    async def plan_tasks(self, user_request: str, context: AgentContext) -> List[str]:
        """Generate task plan from user request"""
        system_prompt = """You are an AI coding assistant. Break down the user's request into clear, actionable subtasks.
Return a JSON array of task descriptions."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Request: {user_request}\n\nBreak this into subtasks."}
        ]
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        
        try:
            tasks = json.loads(response.choices[0].message.content)
            return tasks if isinstance(tasks, list) else [tasks]
        except:
            return [user_request]
    
    async def decide_action(self, context: AgentContext) -> AgentAction:
        """Decide next action based on context"""
        
        # Build tool descriptions with parameters
        tool_descriptions = []
        for tool_name, tool_info in self.tool_registry.items():
            schema = tool_info['schema']
            # Get schema fields
            fields = schema.model_fields if hasattr(schema, 'model_fields') else {}
            params = {name: str(field.annotation) for name, field in fields.items()}
            tool_descriptions.append(f"- {tool_name}: {schema.__doc__ or 'No description'}\n  Parameters: {json.dumps(params, indent=4)}")
        
        tools_text = "\n".join(tool_descriptions[:10])  # Limit to first 10 tools to save tokens
        
        system_prompt = f"""You are an AI coding assistant. You MUST use tools to accomplish tasks.

Available tools:
{tools_text}

IMPORTANT: You MUST respond with valid JSON in this EXACT format:

For using a tool:
{{
    "type": "tool_use",
    "tool_name": "write_file",
    "parameters": {{"file_path": "demo/src/app/page.tsx", "content": "..."}},
    "message": "Creating the page file",
    "reasoning": "Need to write the page content to file"
}}

For completing:
{{
    "type": "complete",
    "message": "Task completed successfully"
}}

RULES:
1. ALWAYS use tools to accomplish tasks - don't just describe what to do
2. For creating files, use write_file tool
3. For React components, use generate_react_component or write_file
4. Respond ONLY with valid JSON, no other text
5. Use "complete" only after all work is done"""
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(context.conversation_history[-3:])  # Last 3 messages
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        try:
            action_data = json.loads(response.choices[0].message.content)
            return AgentAction(**action_data)
        except Exception as e:
            return AgentAction(
                type=ActionType.ERROR,
                message=f"Failed to parse action: {str(e)}\nResponse: {response.choices[0].message.content[:200]}"
            )
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute a tool with given parameters"""
        if tool_name not in self.tool_registry:
            return ToolResult(
                success=False,
                error=f"Tool not found: {tool_name}"
            )
        
        tool_info = self.tool_registry[tool_name]
        
        try:
            # Validate parameters
            schema = tool_info['schema']
            validated_params = schema(**parameters)
            
            # Execute tool
            start_time = time.time()
            result = await tool_info['function'](validated_params)
            execution_time = (time.time() - start_time) * 1000
            
            if result.execution_time_ms is None:
                result.execution_time_ms = execution_time
            
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Tool execution failed: {str(e)}"
            )
    
    async def synthesize_response(self, context: AgentContext) -> str:
        """Generate final response from context"""
        system_prompt = """You are an AI coding assistant. Synthesize the conversation and tool results into a clear, helpful response for the user."""
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(context.conversation_history)
        messages.append({
            "role": "user",
            "content": "Please provide a summary of what was accomplished."
        })
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.5,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    async def execute(self, user_request: str, max_iterations: int = 10) -> Dict[str, Any]:
        """Main execution loop"""
        context = AgentContext(
            user_request=user_request,
            max_iterations=max_iterations
        )
        
        # Add initial user request
        context.add_message("user", user_request)
        
        # Plan tasks
        task_plan = await self.plan_tasks(user_request, context)
        context.add_message("assistant", f"Task plan: {json.dumps(task_plan, indent=2)}")
        
        # Execution loop
        while context.iteration < context.max_iterations:
            context.iteration += 1
            
            # Decide next action
            action = await self.decide_action(context)
            
            if action.type == ActionType.COMPLETE:
                break
            
            elif action.type == ActionType.TOOL_USE:
                if action.tool_name and action.parameters:
                    # Execute tool
                    result = await self.execute_tool(action.tool_name, action.parameters)
                    context.add_tool_result(action.tool_name, result)
                    
                    # Handle errors with retry logic
                    if not result.success and context.iteration < context.max_iterations:
                        context.add_error(f"Tool {action.tool_name} failed: {result.error}")
            
            elif action.type == ActionType.CLARIFY:
                context.add_message("assistant", action.message or "Need clarification")
                break
            
            elif action.type == ActionType.ERROR:
                context.add_error(action.message or "Unknown error")
                break
        
        # Generate final response
        final_response = await self.synthesize_response(context)
        
        return {
            "success": len(context.errors) == 0,
            "response": final_response,
            "iterations": context.iteration,
            "tool_results": [r.dict() for r in context.tool_results],
            "errors": context.errors
        }


async def main():
    """Example usage"""
    import os
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable not set")
        return
    
    agent = AICodeAgent(groq_api_key=api_key)
    
    # Example request
    result = await agent.execute(
        "List all Python files in the current directory and show me the structure of the first one"
    )
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
