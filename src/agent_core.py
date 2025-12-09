"""
AI Coding Agent Core
Main execution loop and task management
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import time
from pathlib import Path
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from groq import AsyncGroq
from .tool_schemas import ToolResult, TOOL_INPUT_SCHEMAS
from . import tools

# Configure logger with detailed formatting
logger = logging.getLogger(__name__)

def setup_logging(log_file: str = "agent_execution.log", level: int = logging.INFO):
    """Setup detailed logging to both file and console"""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler - detailed logs
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler - important logs only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logger.info(f"📝 Logging configured: {log_file}")
    
    return log_file


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
    
    def __init__(self, groq_api_key: Optional[str] = None, model: str = "llama-3.1-8b-instant", log_file: str = "agent_execution.log"):
        # Setup logging first
        setup_logging(log_file)
        
        # Load API key from environment if not provided
        if groq_api_key is None:
            groq_api_key = os.getenv('GROQ_API_KEY')
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables or parameters")
        
        logger.info(f"\n{'#'*80}")
        logger.info(f"🤖 AI CODE AGENT INITIALIZATION")
        logger.info(f"{'#'*80}")
        logger.info(f"📋 Model: {model}")
        logger.info(f"📝 Log file: {log_file}")
        
        self.client = AsyncGroq(api_key=groq_api_key)
        self.model = model
        
        logger.info(f"📚 Loading tool dictionary...")
        self.tool_dictionary = self._load_tool_dictionary()
        logger.info(f"✅ Tool dictionary loaded: version {self.tool_dictionary.get('metadata', {}).get('version', 'unknown')}")
        
        logger.info(f"🔧 Building tool registry...")
        self.tool_registry = self._build_tool_registry()
        logger.info(f"✅ Tool registry built: {len(self.tool_registry)} tools available")
        
        # Log available tools by category
        logger.info(f"\n📦 Available Tools by Category:")
        for category, tools_dict in self.tool_dictionary.get('tools', {}).items():
            tool_names = [name for name in tools_dict.keys() if name in self.tool_registry]
            if tool_names:
                logger.info(f"   {category}: {', '.join(tool_names)}")
        
        logger.info(f"\n✅ Agent initialization complete!")
        logger.info(f"{'#'*80}\n")
    
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
            'redux_tools': tools.redux_tools,
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
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🧠 DECISION PHASE - Iteration {context.iteration}")
        logger.info(f"{'='*80}")
        logger.info(f"📊 Context State:")
        logger.info(f"   - Conversation messages: {len(context.conversation_history)}")
        logger.info(f"   - Tool results: {len(context.tool_results)}")
        logger.info(f"   - Errors: {len(context.errors)}")
        
        # Log recent tool usage to detect loops
        if len(context.tool_results) >= 3:
            recent_tools = [r.metadata.get('tool_name', 'unknown') for r in context.tool_results[-3:]]
            logger.info(f"   - Recent tools: {' -> '.join(recent_tools)}")
            
            # DETECT INFINITE LOOPS
            if len(set(recent_tools)) == 1:
                logger.warning(f"⚠️  LOOP DETECTED! Same tool called 3 times in a row: {recent_tools[0]}")
        
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
7. ⚠️ CRITICAL: For Redux state management, use "generate_redux_setup" NOT "generate_redux_store"
   - This tool is ONLY called AFTER components are generated
   - It automatically creates Redux slices based on component prop schemas

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
⚠️ CRITICAL: Return a SINGLE JSON OBJECT, NOT an array. Only ONE action per response.
❌ WRONG: [{{"type": "tool_use", ...}}, {{"type": "tool_use", ...}}]
✅ CORRECT: {{"type": "tool_use", "tool_name": "...", "parameters": {{...}}}}

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

EXAMPLE 4 - Redux setup (ONLY after components exist):
{{
    "type": "tool_use",
    "tool_name": "generate_redux_setup",
    "parameters": {{
        "components": [],
        "output_dir": "./demo/src/store",
        "store_name": "store"
    }},
    "message": "Setting up Redux store",
    "reasoning": "Creating Redux state management after components are ready"
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
        
        logger.info(f"\n🤔 Calling LLM to decide action...")
        logger.info(f"📝 Sending {len(messages)} messages to model: {self.model}")
        logger.debug(f"� Last user message: {context.conversation_history[-1].get('content', '')[:200]}...")
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        logger.info(f"✅ Received response from LLM")
        
        try:
            content = response.choices[0].message.content
            logger.info(f"\n� LLM RESPONSE (Raw):")
            logger.info(f"{'-'*80}")
            logger.info(f"{content[:500]}...")
            logger.info(f"{'-'*80}")
            
            # Parse JSON - handle both objects and arrays
            parsed = json.loads(content)
            
            # ⚠️ ROBUST HANDLING: Support both JSON object and array formats
            if isinstance(parsed, list):
                logger.warning(f"⚠️  Model returned array with {len(parsed)} elements. Processing first element.")
                if len(parsed) == 0:
                    logger.error(f"❌ Empty array returned!")
                    return AgentAction(
                        type=ActionType.ERROR,
                        message="Model returned empty array"
                    )
                action_data = parsed[0]
                logger.debug(f"✓ Extracted first element from array")
            elif isinstance(parsed, dict):
                action_data = parsed
                logger.debug(f"✓ Received JSON object (correct format)")
            else:
                logger.error(f"❌ Unexpected JSON type: {type(parsed)}")
                return AgentAction(
                    type=ActionType.ERROR,
                    message=f"Unexpected JSON type: {type(parsed)}"
                )
            
            # Validate we have an action object
            if not isinstance(action_data, dict):
                logger.error(f"❌ Action data is not a dict: {type(action_data)}")
                return AgentAction(
                    type=ActionType.ERROR,
                    message=f"Invalid action data type: {type(action_data)}"
                )
            
            # LOG THE DECISION DETAILS
            logger.info(f"\n🎯 AI DECISION:")
            logger.info(f"   Type: {action_data.get('type', 'unknown')}")
            if action_data.get('tool_name'):
                logger.info(f"   Tool: {action_data.get('tool_name')}")
            if action_data.get('message'):
                logger.info(f"   Message: {action_data.get('message')}")
            if action_data.get('reasoning'):
                logger.info(f"   🧠 Reasoning: {action_data.get('reasoning')}")
            if action_data.get('parameters'):
                logger.info(f"   📝 Parameters:")
                for key, value in action_data.get('parameters', {}).items():
                    value_str = str(value)[:100] if not isinstance(value, (list, dict)) else json.dumps(value)[:100]
                    logger.info(f"      - {key}: {value_str}")
            
            return AgentAction(**action_data)
        except Exception as e:
            logger.error(f"❌ Failed to parse LLM response: {str(e)}")
            logger.debug(f"Response content: {response.choices[0].message.content}")
            return AgentAction(
                type=ActionType.ERROR,
                message=f"Failed to parse action: {str(e)}\nResponse: {response.choices[0].message.content[:200]}"
            )
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute a tool with given parameters"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🔧 TOOL EXECUTION: {tool_name}")
        logger.info(f"{'='*80}")
        logger.info(f"📝 Parameters:")
        for key, value in parameters.items():
            value_str = str(value)[:200] if not isinstance(value, (list, dict)) else json.dumps(value, indent=2)[:300]
            logger.info(f"   {key}: {value_str}")
        
        if tool_name not in self.tool_registry:
            logger.error(f"❌ Tool not found: {tool_name}")
            logger.error(f"📚 Available tools ({len(self.tool_registry)}): {', '.join(list(self.tool_registry.keys())[:20])}")
            return ToolResult(
                success=False,
                error=f"Tool not found: {tool_name}",
                metadata={"tool_name": tool_name}
            )
        
        tool_info = self.tool_registry[tool_name]
        
        try:
            # Validate parameters
            schema = tool_info['schema']
            logger.info(f"✓ Validating against schema: {schema.__name__}")
            validated_params = schema(**parameters)
            logger.info(f"✅ Parameters validated successfully")
            
            # Execute tool
            start_time = time.time()
            logger.info(f"⚙️  Calling tool function...")
            result = await tool_info['function'](validated_params)
            execution_time = (time.time() - start_time) * 1000
            
            # Add tool name to metadata for tracking
            if not result.metadata:
                result.metadata = {}
            result.metadata['tool_name'] = tool_name
            
            if result.execution_time_ms is None:
                result.execution_time_ms = execution_time
            
            if result.success:
                logger.info(f"✅ Tool {tool_name} succeeded in {execution_time:.2f}ms")
                if result.data:
                    logger.info(f"📦 Result data keys: {list(result.data.keys()) if isinstance(result.data, dict) else 'non-dict'}")
                    # Log important file operations
                    if 'files_created' in result.data:
                        logger.info(f"📁 Files created: {result.data.get('files_created', [])}")
                    if 'component_file' in result.data:
                        logger.info(f"📄 Component file: {result.data.get('component_file')}")
            else:
                logger.error(f"❌ Tool {tool_name} failed: {result.error}")
            
            return result
        except Exception as e:
            logger.error(f"❌ Tool execution exception: {str(e)}", exc_info=True)
            return ToolResult(
                success=False,
                error=f"Tool execution failed: {str(e)}",
                metadata={"tool_name": tool_name, "exception": str(e)}
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
        logger.info(f"\n{'#'*80}")
        logger.info(f"🚀 AGENT EXECUTION START")
        logger.info(f"{'#'*80}")
        logger.info(f"📋 User Request: {user_request[:200]}...")
        logger.info(f"⚙️  Max Iterations: {max_iterations}")
        
        context = AgentContext(
            user_request=user_request,
            max_iterations=max_iterations
        )
        
        # Add initial user request
        context.add_message("user", user_request)
        
        # Plan tasks
        print(f"\n🎯 Planning tasks...")
        logger.info(f"\n{'='*80}")
        logger.info(f"📋 TASK PLANNING PHASE")
        logger.info(f"{'='*80}")
        task_plan = await self.plan_tasks(user_request, context)
        print(f"📋 Task Plan: {json.dumps(task_plan, indent=2)}")
        logger.info(f"✅ Task Plan Generated: {json.dumps(task_plan, indent=2)}")
        context.add_message("assistant", f"Task plan: {json.dumps(task_plan, indent=2)}")
        
        # Execution loop
        print(f"\n🚀 Starting execution loop (max {max_iterations} iterations)...\n")
        logger.info(f"\n{'='*80}")
        logger.info(f"🔄 EXECUTION LOOP START")
        logger.info(f"{'='*80}")
        
        # Track tool usage to detect loops
        tool_usage_history = []
        
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
                    
                    # Track tool usage for loop detection
                    tool_usage_history.append(action.tool_name)
                    
                    # HALLUCINATION DETECTION: Check for infinite loops
                    if len(tool_usage_history) >= 5:
                        recent_5 = tool_usage_history[-5:]
                        # If same tool called 5 times in a row, STOP
                        if len(set(recent_5)) == 1:
                            error_msg = f"🚨 INFINITE LOOP DETECTED! Tool '{action.tool_name}' called 5 times consecutively. Stopping execution."
                            logger.error(error_msg)
                            print(f"\n❌ {error_msg}")
                            context.add_error(error_msg)
                            break
                        
                        # If alternating between 2 tools, also suspicious
                        if len(set(recent_5)) == 2 and len(recent_5) == 5:
                            logger.warning(f"⚠️  Possible loop detected: alternating between {set(recent_5)}")
                    
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
                    
                    # HALLUCINATION CHECK: Did the tool actually create what it claimed?
                    if result.success and action.tool_name in ['generate_page_with_components', 'generate_react_component']:
                        files_created = result.data.get('files_created', []) if result.data else []
                        component_file = result.data.get('component_file', '') if result.data else ''
                        
                        if not files_created and not component_file:
                            logger.warning(f"⚠️  HALLUCINATION WARNING: {action.tool_name} reported success but no files were created!")
                            print(f"⚠️  WARNING: Tool claimed success but no files created!")
                    
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
        logger.info(f"\n{'='*80}")
        logger.info(f"📝 SYNTHESIZING FINAL RESPONSE")
        logger.info(f"{'='*80}")
        final_response = await self.synthesize_response(context)
        
        # Generate execution summary
        logger.info(f"\n{'#'*80}")
        logger.info(f"📊 EXECUTION SUMMARY")
        logger.info(f"{'#'*80}")
        logger.info(f"✅ Success: {len(context.errors) == 0}")
        logger.info(f"🔄 Iterations: {context.iteration}/{max_iterations}")
        logger.info(f"🔧 Tools executed: {len(context.tool_results)}")
        logger.info(f"❌ Errors: {len(context.errors)}")
        
        # Log tool breakdown
        tool_counts = {}
        files_created_all = []
        for tr in context.tool_results:
            tool_name = tr.metadata.get('tool_name', 'unknown')
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
            
            # Collect all files created
            if tr.data:
                if 'files_created' in tr.data:
                    files_created_all.extend(tr.data['files_created'])
                if 'component_file' in tr.data:
                    files_created_all.append(tr.data['component_file'])
        
        logger.info(f"\n📋 Tool Usage Breakdown:")
        for tool_name, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"   {tool_name}: {count} times")
        
        logger.info(f"\n📁 Total Files Created: {len(files_created_all)}")
        for f in files_created_all[:20]:  # Show first 20
            logger.info(f"   - {f}")
        
        if context.errors:
            logger.error(f"\n❌ Errors Encountered:")
            for i, err in enumerate(context.errors, 1):
                logger.error(f"   {i}. {err}")
        
        # HALLUCINATION ANALYSIS
        logger.info(f"\n🔍 HALLUCINATION ANALYSIS:")
        
        # Check if agent claimed completion without doing work
        if context.iteration < 3 and len(context.tool_results) < 2:
            logger.warning(f"⚠️  POSSIBLE HALLUCINATION: Agent completed in {context.iteration} iterations with only {len(context.tool_results)} tool calls")
        
        # Check if tools were called but no files created
        component_tools = [tr for tr in context.tool_results if tr.metadata.get('tool_name') in ['generate_page_with_components', 'generate_react_component']]
        if component_tools and not files_created_all:
            logger.error(f"🚨 HALLUCINATION DETECTED: {len(component_tools)} component generation tools called but NO files created!")
        
        # Check for repetitive tool calls (same tool >3 times)
        for tool_name, count in tool_counts.items():
            if count > 3:
                logger.warning(f"⚠️  Tool '{tool_name}' called {count} times - possible stuck loop")
        
        logger.info(f"\n{'#'*80}\n")
        
        return {
            "success": len(context.errors) == 0,
            "response": final_response,
            "iterations": context.iteration,
            "tool_results": [r.dict() for r in context.tool_results],
            "errors": context.errors,
            "tool_usage": tool_counts,
            "files_created": files_created_all
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
