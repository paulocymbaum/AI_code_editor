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
from .tool_schemas import ToolResult, TOOL_INPUT_SCHEMAS
from . import tools


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
    
    def __init__(self, groq_api_key: str, model: str = "llama-3.1-8b-instant"):
        self.client = AsyncGroq(api_key=groq_api_key)
        self.model = model
        self.tool_dictionary = self._load_tool_dictionary()
        self.tool_registry = self._build_tool_registry()
    
    def _load_tool_dictionary(self) -> Dict[str, Any]:
        """Load tool dictionary from config file"""
        import pathlib
        
        # Try multiple locations
        possible_paths = [
            pathlib.Path("config/tool_dictionary.json"),
            pathlib.Path(__file__).parent.parent / "config" / "tool_dictionary.json",
        ]
        
        for path in possible_paths:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        # Return empty dict if not found
        return {"tools": {}, "metadata": {}}
    
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
            'page_management': tools.page_management,
            'design_system': tools.design_system,
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
        
        # Build tool descriptions from tool_dictionary.json
        tool_descriptions = []
        
        # Load descriptions from tool_dictionary with examples
        for category_name, category_tools in self.tool_dictionary.get("tools", {}).items():
            for tool_name, tool_info in category_tools.items():
                if tool_name in self.tool_registry:
                    desc = tool_info.get("description", "No description")
                    params = tool_info.get("parameters", {})
                    example = tool_info.get("example")
                    usage_notes = tool_info.get("usage_notes")
                    
                    # Build tool description
                    tool_desc = f"- **{tool_name}**: {desc}\n"
                    
                    # Add ACTUAL Pydantic schema fields (from TOOL_INPUT_SCHEMAS)
                    if tool_name in TOOL_INPUT_SCHEMAS:
                        schema_class = TOOL_INPUT_SCHEMAS[tool_name]
                        tool_desc += "  REQUIRED Parameters (use these exact names):\n"
                        for field_name, field_info in schema_class.model_fields.items():
                            required = field_info.is_required()
                            field_type = field_info.annotation.__name__ if hasattr(field_info.annotation, '__name__') else str(field_info.annotation)
                            default = f" (default: {field_info.default})" if not required and field_info.default is not None else ""
                            req_marker = "**REQUIRED**" if required else "optional"
                            tool_desc += f"    - {field_name}: {field_type} - {req_marker}{default}\n"
                    elif isinstance(params, dict):
                        tool_desc += "  Parameters:\n"
                        for param_name, param_desc in params.items():
                            tool_desc += f"    - {param_name}: {param_desc}\n"
                    elif isinstance(params, list):
                        tool_desc += f"  Parameters: {', '.join(params)}\n"
                    
                    # Add example if available
                    if example:
                        tool_desc += f"  Example JSON:\n{json.dumps(example, indent=6)}\n"
                    
                    # Add usage notes if available
                    if usage_notes:
                        tool_desc += f"  ⚠️ IMPORTANT: {usage_notes}\n"
                    
                    # Add guidelines if available (NEW: detailed best practices)
                    guidelines = tool_info.get("guidelines")
                    if guidelines:
                        tool_desc += "\n  📋 CRITICAL GUIDELINES:\n"
                        if isinstance(guidelines, dict):
                            for guideline_key, guideline_value in guidelines.items():
                                # Format guideline key as readable title
                                title = guideline_key.replace('_', ' ').title()
                                if isinstance(guideline_value, dict):
                                    tool_desc += f"    {title}:\n"
                                    for sub_key, sub_value in guideline_value.items():
                                        sub_title = sub_key.replace('_', ' ').title()
                                        tool_desc += f"      • {sub_title}: {sub_value}\n"
                                else:
                                    tool_desc += f"    • {title}: {guideline_value}\n"
                        else:
                            tool_desc += f"    {guidelines}\n"
                    
                    tool_descriptions.append(tool_desc)
        
        tools_text = "\n".join(tool_descriptions[:20])  # Show top 20 tools
        
        system_prompt = f"""You are an AI coding assistant. You MUST use tools to accomplish tasks.

Available tools with examples:
{tools_text}

CRITICAL PARAMETER RULES:
1. generate_react_component uses "component_name" NOT "name"
2. generate_react_component uses "component_pattern" NOT "pattern"  
3. generate_page_with_components ALWAYS REQUIRES 3 parameters:
   - "page_name": string (e.g., "Home", "Dashboard")
   - "page_path": string (full file path like "./demo/src/app/page.tsx")
   - "components": array of dicts with "name", "pattern", "variant"
4. generate_page_with_components DOES NOT use "output_dir"
5. Always use relative paths starting with "./" like "./demo/src/components"
6. Component names must be PascalCase: "ProductCard" not "product-card"

⚠️ CRITICAL: COMPONENT PATTERN SELECTION
Pattern field is MANDATORY and must match component purpose:
- sidebar: Navigation panels → ChatSidebar, UserSidebar, NavPanel
- header: Top bars → AppHeader, ChatHeader, PageHeader
- footer: Bottom bars → AppFooter, PageFooter
- messages: Message displays → ChatMessageList, MessageThread
- input: Input fields → ChatInput, MessageInput, SearchBar
- form: Data entry → LoginForm, SignupForm, SettingsForm
- list: Item lists → UserList, ProductList, NotificationList
- card: Info cards → ProductCard, ProfileCard, StatCard
- button: Action buttons → CTAButton, SubmitButton
- hero: Hero sections → HeroSection, Banner
- modal: Dialogs → ConfirmModal, EditModal
- feature: Features → FeatureCard, BenefitSection
- pricing: Pricing → PricingCard, PlanCard

WRONG: {{"name": "ChatSidebar", "pattern": "card"}}  ❌
RIGHT: {{"name": "ChatSidebar", "pattern": "sidebar"}} ✅

WRONG: {{"name": "LoginForm", "pattern": "card"}}  ❌
RIGHT: {{"name": "LoginForm", "pattern": "form"}} ✅

RESPONSIVE DESIGN REQUIREMENTS:
- ALL components MUST be responsive for mobile (320px+), tablet (768px+), and desktop (1024px+)
- Use Tailwind responsive prefixes: sm:, md:, lg:, xl:
- Mobile-first approach: base styles for mobile, then add breakpoints
- Components should stack vertically on mobile, side-by-side on larger screens
- Text sizes should scale appropriately (text-sm on mobile, text-base/lg on desktop)
- Padding and spacing should be responsive (p-4 sm:p-6 lg:p-8)
- Images and media should be fluid width (w-full) with max-width constraints

JSON RESPONSE FORMAT (respond with ONLY valid JSON, no markdown):

EXAMPLE 1 - Chat Interface with correct patterns:
{{
    "type": "tool_use",
    "tool_name": "generate_page_with_components",
    "parameters": {{
        "page_name": "chat",
        "page_path": "./demo/src/app/chat/page.tsx",
        "components": [
            {{"name": "ChatSidebar", "pattern": "sidebar", "variant": "primary"}},
            {{"name": "ChatHeader", "pattern": "header", "variant": "secondary"}},
            {{"name": "MessageList", "pattern": "messages", "variant": "primary"}},
            {{"name": "ChatInput", "pattern": "input", "variant": "primary"}},
            {{"name": "ChatFooter", "pattern": "footer", "variant": "secondary"}}
        ],
        "layout_type": "chat"
    }},
    "message": "Generating chat interface with semantic patterns",
    "reasoning": "Using sidebar pattern for navigation, header/footer for top/bottom bars, messages for chat display, input for message entry"
}}

EXAMPLE 2 - Dashboard with correct patterns:
{{
    "type": "tool_use",
    "tool_name": "generate_page_with_components",
    "parameters": {{
        "page_name": "dashboard",
        "page_path": "./demo/src/app/dashboard/page.tsx",
        "components": [
            {{"name": "DashboardHeader", "pattern": "header", "variant": "primary"}},
            {{"name": "MetricCard", "pattern": "card", "variant": "primary"}},
            {{"name": "ActivityList", "pattern": "list", "variant": "secondary"}},
            {{"name": "FilterForm", "pattern": "form", "variant": "secondary"}}
        ],
        "layout_type": "dashboard"
    }},
    "message": "Generating dashboard with appropriate patterns",
    "reasoning": "Header for page title, cards for metrics, list for activities, form for filters"
}}

EXAMPLE 3 - Single component generation:
{{
    "type": "tool_use",
    "tool_name": "generate_react_component",
    "parameters": {{
        "component_name": "UserSidebar",
        "component_pattern": "sidebar",
        "variant": "primary",
        "styling": "tailwind",
        "output_dir": "./demo/src/components"
    }},
    "message": "Generating ProductCard component",
    "reasoning": "Need to create the card component for products"
}}

For completing:
{{
    "type": "complete",
    "message": "All tasks completed successfully"
}}

CRITICAL RULES:
1. ALWAYS use tools to accomplish tasks - don't just plan
2. Use exact parameter names from examples above
3. Check examples before using a tool
4. For multi-step tasks, do ONE step at a time, then continue
5. Respond with ONLY valid JSON, no markdown code blocks
6. NEVER use "complete" until ALL steps are done - keep iterating
7. If a task has multiple steps (STEP 1, STEP 2, etc), you MUST execute ALL steps
8. After completing one step, immediately proceed to the next step
9. Only use "complete" when you have executed every single required action"""
        
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
        print(f"\n🎯 Planning tasks...")
        task_plan = await self.plan_tasks(user_request, context)
        print(f"📋 Task Plan: {json.dumps(task_plan, indent=2)}")
        context.add_message("assistant", f"Task plan: {json.dumps(task_plan, indent=2)}")
        
        # Execution loop
        print(f"\n🚀 Starting execution loop (max {max_iterations} iterations)...\n")
        while context.iteration < context.max_iterations:
            context.iteration += 1
            print(f"\n{'='*80}")
            print(f"ITERATION {context.iteration}/{context.max_iterations}")
            print(f"{'='*80}")
            
            # Decide next action
            print(f"\n🤔 Deciding next action...")
            action = await self.decide_action(context)
            print(f"📌 Action Type: {action.type}")
            
            if action.type == ActionType.COMPLETE:
                print(f"✅ COMPLETE: {action.message}")
                break
            
            elif action.type == ActionType.TOOL_USE:
                if action.tool_name and action.parameters:
                    print(f"\n🔧 Using Tool: {action.tool_name}")
                    print(f"💬 Message: {action.message}")
                    print(f"📝 Parameters: {json.dumps(action.parameters, indent=2)}")
                    
                    # Execute tool
                    print(f"⚙️  Executing...")
                    result = await self.execute_tool(action.tool_name, action.parameters)
                    
                    if result.success:
                        print(f"✅ SUCCESS!")
                        if result.data:
                            print(f"📦 Data: {json.dumps(result.data, indent=2)[:500]}")
                    else:
                        print(f"❌ FAILED: {result.error}")
                    
                    context.add_tool_result(action.tool_name, result)
                    
                    # Handle errors with retry logic
                    if not result.success and context.iteration < context.max_iterations:
                        context.add_error(f"Tool {action.tool_name} failed: {result.error}")
            
            elif action.type == ActionType.CLARIFY:
                print(f"❓ CLARIFY: {action.message}")
                context.add_message("assistant", action.message or "Need clarification")
                break
            
            elif action.type == ActionType.ERROR:
                print(f"❌ ERROR: {action.message}")
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
