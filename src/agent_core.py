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

from groq import AsyncGroq
from groq import (
    APIError, 
    RateLimitError, 
    BadRequestError,
    AuthenticationError,
    APIConnectionError,
    APITimeoutError
)
from .tool_schemas import ToolResult, TOOL_INPUT_SCHEMAS
from . import tools
from .task_state import (
    TaskState, TaskPlan, TaskStatus, 
    log_task_plan
)
from .utils.logging_config import AgentLogger
from .core.config import get_settings

# Get logger for this module
logger = AgentLogger.get_logger(__name__)


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
    task_plan: Optional[TaskPlan] = None
    current_task: Optional[TaskState] = None
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[ToolResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    consecutive_errors: int = 0
    max_consecutive_errors: int = 4
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
        self.add_message("assistant", f"Tool: {tool_name}\nResult: {json.dumps(result.model_dump(), indent=2)}")
    
    def add_error(self, error: str):
        """Add error to context and increment consecutive error counter"""
        self.errors.append(error)
        self.consecutive_errors += 1
        self.add_message("system", f"Error: {error}")
        logger.warning(f"⚠️  Consecutive errors: {self.consecutive_errors}/{self.max_consecutive_errors}")
    
    def reset_error_counter(self):
        """Reset consecutive error counter after successful operation"""
        if self.consecutive_errors > 0:
            logger.info(f"✅ Resetting error counter (was {self.consecutive_errors})")
            self.consecutive_errors = 0
    
    def should_stop_due_to_errors(self) -> bool:
        """Check if we should stop due to too many consecutive errors"""
        return self.consecutive_errors >= self.max_consecutive_errors


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
    
    def __init__(self, groq_api_key: Optional[str] = None, model: Optional[str] = None, log_file: str = "agent_execution.log"):
        # Setup logging first using centralized logger
        AgentLogger.setup(log_file)
        
        # Load settings from centralized config
        settings = get_settings()
        
        # Use provided values or fall back to config
        if groq_api_key is None:
            groq_api_key = settings.groq.api_key
        
        if model is None:
            model = settings.groq.model
        
        logger.info(f"\n{'#'*80}")
        logger.info(f"🤖 AI CODE AGENT INITIALIZATION")
        logger.info(f"{'#'*80}")
        logger.info(f"📋 Model: {model}")
        logger.info(f"📝 Log file: {log_file}")
        
        self.client = AsyncGroq(api_key=groq_api_key)
        self.model = model
        self.settings = settings
        
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
        from pathlib import Path
        
        # Use config directory from settings
        config_dir = Path(self.settings.paths.config_dir)
        tool_dict_path = config_dir / "tool_dictionary.json"
        
        # Fallback to relative path if config dir doesn't exist
        if not tool_dict_path.exists():
            tool_dict_path = Path(__file__).parent.parent / "config" / "tool_dictionary.json"
        
        if tool_dict_path.exists():
            with open(tool_dict_path, 'r', encoding='utf-8') as f:
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

    
    async def plan_tasks(self, user_request: str) -> TaskPlan:
        """
        Generate structured task plan from user request
        Uses LLM to break down request into actionable tasks
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"📋 TASK PLANNING PHASE")
        logger.info(f"{'='*80}")
        
        system_prompt = """You are a task planning AI for code generation. 
Break down the user's request into specific, actionable tasks.

For each task, specify:
- name: Brief task name (e.g., "Create Header Component")
- description: What needs to be done
- files_expected: Array of file paths that should be created

IMPORTANT: 
- Be specific about file paths (use Next.js conventions)
- Use demo/ as root directory
- Follow Next.js App Router structure: demo/src/app/
- Components go in: demo/src/app/components/
- Store files go in: demo/src/app/store/

Return ONLY valid JSON in this format:
{
  "tasks": [
    {
      "name": "Create DashboardHeader component",
      "description": "Generate a responsive header with navigation and search",
      "files_expected": ["demo/src/app/components/DashboardHeader.tsx"]
    },
    {
      "name": "Create StatCard component", 
      "description": "Generate a card component to display statistics",
      "files_expected": ["demo/src/app/components/StatCard.tsx"]
    },
    {
      "name": "Setup Redux store",
      "description": "Create Redux store with slices for components",
      "files_expected": [
        "demo/src/app/store/store.ts",
        "demo/src/app/store/hooks.ts",
        "demo/src/app/store/dashboardheaderSlice.ts",
        "demo/src/app/store/statcardSlice.ts"
      ]
    },
    {
      "name": "Create dashboard page",
      "description": "Create the main dashboard page that uses the components",
      "files_expected": ["demo/src/app/dashboard/page.tsx"]
    }
  ]
}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Request: {user_request}\n\nBreak this into specific tasks with exact file paths."}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                response_format={"type": "json_object"},
                temperature=0.3
            )
        except (RateLimitError, AuthenticationError, APITimeoutError, APIConnectionError, BadRequestError, APIError) as e:
            logger.error(f"❌ API error during task planning: {str(e)}")
            # Return a minimal task plan with single task
            return TaskPlan(
                tasks=[TaskState(
                    id=1,
                    name="Handle API Error",
                    description=f"API error occurred: {str(e)}",
                    status=TaskStatus.FAILED,
                    files_expected=[]
                )],
                user_request=user_request,
                created_at=time.time(),
                project_dir="."
            )
        
        content = response.choices[0].message.content or ""
        logger.info(f"✅ Task plan generated")
        
        try:
            data = json.loads(content)
            tasks = [
                TaskState(
                    id=i+1,
                    name=t["name"],
                    description=t["description"],
                    status=TaskStatus.PENDING,
                    files_expected=t.get("files_expected", [])
                )
                for i, t in enumerate(data["tasks"])
            ]
            
            task_plan = TaskPlan(
                tasks=tasks,
                user_request=user_request,
                created_at=time.time(),
                project_dir="."
            )
            
            # Log the plan
            log_task_plan(task_plan, logger)
            
            return task_plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse task plan: {e}")
            logger.error(f"Response: {content[:200]}")
            
            # Fallback: create single task
            return TaskPlan(
                tasks=[
                    TaskState(
                        id=1,
                        name="Complete user request",
                        description=user_request,
                        status=TaskStatus.PENDING,
                        files_expected=[]
                    )
                ],
                user_request=user_request,
                created_at=time.time()
            )
    
    async def decide_action_for_task(
        self, 
        context: AgentContext,
        task: TaskState
    ) -> AgentAction:
        """
        Decide which action to take for a specific task
        Context-aware of task state and already-completed work
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🧠 DECISION PHASE - Task: {task.name}")
        logger.info(f"{'='*80}")
        
        # Build context with task state and progress
        task_context = self._build_task_context(context.task_plan, task)
        
        # Build tool descriptions with parameter names
        tool_descriptions = []
        for category_name, category_tools in self.tool_dictionary.get("tools", {}).items():
            for tool_name, tool_info in category_tools.items():
                if tool_name in self.tool_registry:
                    desc = tool_info.get("description", "No description")
                    params = tool_info.get("parameters", [])
                    params_str = ", ".join(params) if params else "no parameters"
                    tool_descriptions.append(f"- **{tool_name}**({params_str}): {desc}")
        
        tools_text = "\n".join(tool_descriptions[:20])
        
        system_prompt = f"""You are an AI coding assistant focused on completing a specific task.

Available tools:
{tools_text}

TASK-ORIENTED MODE:
You are working on a specific task. Focus ONLY on completing THIS task.
Do NOT work on tasks that are already done.
Do NOT create files that already exist.

{task_context}

Choose the appropriate tool to complete the CURRENT task.
If the task requires multiple steps, do ONE step and return.

Return JSON in this format:
{{
    "type": "tool_use",
    "tool_name": "tool_name_here",
    "parameters": {{ ... }},
    "message": "What you're doing",
    "reasoning": "Why"
}}

Or to complete the task:
{{
    "type": "complete",
    "message": "Task completed"
}}
"""
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Current task: {task.name}\n{task.description}"}
        ]
        
        # Add conversation history
        messages.extend(context.conversation_history[-5:])  # Last 5 messages
        
        logger.info(f"🤔 Calling LLM to decide action for task: {task.name}")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                response_format={"type": "json_object"},
                temperature=0.1
            )
        except (RateLimitError, AuthenticationError, APITimeoutError, APIConnectionError, BadRequestError, APIError) as e:
            logger.error(f"❌ API error during validation decision: {str(e)}")
            return AgentAction(
                type=ActionType.ERROR,
                message=f"API error: {str(e)}"
            )
        
        content = response.choices[0].message.content or ""
        logger.info(f"✅ Received response from LLM")
        
        # Parse action
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list) and len(parsed) > 0:
                action_data = parsed[0]
            elif isinstance(parsed, dict):
                action_data = parsed
            else:
                return AgentAction(type=ActionType.ERROR, message="Invalid JSON format")
            
            action = AgentAction(**action_data)
            
            # Log decision
            logger.info(f"\n🎯 AI DECISION:")
            logger.info(f"   Type: {action.type}")
            if action.tool_name:
                logger.info(f"   Tool: {action.tool_name}")
            if action.message:
                logger.info(f"   Message: {action.message}")
            if action.reasoning:
                logger.info(f"   🧠 Reasoning: {action.reasoning}")
            
            return action
        except Exception as e:
            logger.error(f"Failed to parse action: {e}")
            return AgentAction(type=ActionType.ERROR, message=f"Parse error: {str(e)}")

    def _build_task_context(self, task_plan: Optional[TaskPlan], current_task: TaskState) -> str:
        """Build context string with task state"""
        
        if not task_plan:
            return ""
        
        context = f"""
CURRENT TASK (ID: {current_task.id}):
Name: {current_task.name}
Description: {current_task.description}
Expected files: {', '.join(current_task.files_expected) if current_task.files_expected else 'None'}

OVERALL PROGRESS:
"""
        
        status_icons = {
            TaskStatus.DONE: "✅",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.PENDING: "⏳",
            TaskStatus.FAILED: "❌"
        }
        
        for task in task_plan.tasks:
            icon = status_icons.get(task.status, "❓")
            context += f"{icon} Task {task.id}: {task.name}\n"
            
            if task.status == TaskStatus.DONE and task.files_verified:
                context += f"     ✓ Files created: {', '.join(task.files_verified)}\n"
            
            if task.status == TaskStatus.FAILED and task.error:
                context += f"     ✗ Error: {task.error}\n"
        
        return context

    def update_task_state(
        self,
        task: TaskState,
        action: AgentAction,
        result: ToolResult,
        iteration: int
    ):
        """
        Update task state after tool execution with bash verification
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 UPDATING TASK STATE")
        logger.info(f"{'='*80}")
        
        task.tool_used = action.tool_name
        
        if not result.success:
            task.status = TaskStatus.FAILED
            task.error = result.error
            logger.error(f"❌ Task '{task.name}' failed: {result.error}")
            return
        
        # Extract files from result
        files_claimed = []
        
        if result.data and "files_created" in result.data:
            files_claimed = result.data["files_created"]
        elif result.data and "component_file" in result.data:
            files_claimed = [result.data["component_file"]]
        elif result.data and "page_path" in result.data:
            files_claimed = [result.data["page_path"]]
        
        task.files_created = files_claimed
        
        logger.info(f"📝 Tool claimed to create {len(files_claimed)} file(s)")
        
        # BASH VERIFICATION - Check files actually exist
        logger.info(f"🔍 Verifying files with bash...")
        
        verification = task.verify_files_exist()
        
        verified_count = sum(1 for exists in verification.values() if exists)
        total_expected = len(task.files_expected)
        
        logger.info(f"📊 Verification results: {verified_count}/{total_expected} files found")
        
        for filepath, exists in verification.items():
            if exists:
                logger.info(f"   ✅ {filepath}")
            else:
                logger.warning(f"   ❌ {filepath} - NOT FOUND")
        
        # Determine task status
        if task.files_expected:
            # Task specified expected files
            if verified_count == total_expected:
                task.status = TaskStatus.DONE
                task.iteration_completed = iteration
                logger.info(f"✅ Task '{task.name}' completed successfully")
            elif verified_count > 0:
                task.status = TaskStatus.FAILED
                task.error = f"Only {verified_count}/{total_expected} files verified"
                logger.warning(f"⚠️  Task '{task.name}' partially complete: {task.error}")
            else:
                task.status = TaskStatus.FAILED
                task.error = "No expected files found on filesystem"
                logger.error(f"❌ Task '{task.name}' failed: {task.error}")
        else:
            # No specific files expected, trust the tool
            if files_claimed:
                # Verify claimed files exist
                claimed_verification = {
                    f: task._bash_file_exists(f) for f in files_claimed
                }
                verified_claimed = sum(1 for exists in claimed_verification.values() if exists)
                
                if verified_claimed == len(files_claimed):
                    task.status = TaskStatus.DONE
                    task.files_verified = files_claimed
                    task.iteration_completed = iteration
                    logger.info(f"✅ Task '{task.name}' completed (verified claimed files)")
                else:
                    task.status = TaskStatus.FAILED
                    task.error = f"Tool claimed files but only {verified_claimed}/{len(files_claimed)} verified"
                    logger.warning(f"⚠️  {task.error}")
            else:
                # No files claimed or expected, mark done
                task.status = TaskStatus.DONE
                task.iteration_completed = iteration
                logger.info(f"✅ Task '{task.name}' completed (no file outputs)")
    
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
                    
                    # Add capabilities (NEW: what the tool CAN do)
                    capabilities = tool_info.get("capabilities")
                    if capabilities:
                        tool_desc += f"  ✅ CAPABILITIES: {', '.join(capabilities)}\n"
                    
                    # Add limitations (NEW: what the tool CANNOT do)
                    limitations = tool_info.get("limitations")
                    if limitations:
                        tool_desc += f"  ❌ LIMITATIONS: {', '.join(limitations)}\n"
                    
                    # Add not_suitable_for (NEW: when NOT to use this tool)
                    not_suitable = tool_info.get("not_suitable_for")
                    if not_suitable:
                        tool_desc += f"  🚫 NOT SUITABLE FOR: {', '.join(not_suitable)}\n"
                    
                    # Add use_instead (NEW: better alternatives)
                    use_instead = tool_info.get("use_instead")
                    if use_instead:
                        tool_desc += f"  💡 USE INSTEAD:\n"
                        for use_case, better_tool in use_instead.items():
                            tool_desc += f"    • For {use_case}: use {better_tool}\n"
                    
                    # Add advantages (NEW: why use this tool)
                    advantages = tool_info.get("advantages_over_write_file")
                    if advantages:
                        tool_desc += f"  🌟 ADVANTAGES:\n"
                        for advantage in advantages:
                            tool_desc += f"    • {advantage}\n"
                    
                    # Add guidelines if available (detailed best practices)
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

🚨 CRITICAL TOOL SELECTION RULES 🚨

ALWAYS use specialized tools over generic ones:
┌─────────────────────────────────────────────────────────────┐
│ FILE TYPE            │ ❌ WRONG TOOL      │ ✅ CORRECT TOOL  │
├─────────────────────────────────────────────────────────────┤
│ React Components     │ write_file         │ generate_react_component │
│ (.tsx, .jsx)         │                    │ (with design tokens!)    │
├─────────────────────────────────────────────────────────────┤
│ Next.js Pages        │ write_file         │ generate_page_with_components │
│                      │                    │ (creates all components!)     │
├─────────────────────────────────────────────────────────────┤
│ Config Files         │ generate_react_*   │ write_file       │
│ (.json, .yml, .env)  │                    │                  │
└─────────────────────────────────────────────────────────────┘

WHY? Specialized tools provide:
✅ Design system integration (282+ tokens from config/design-tokens.json)
✅ Component patterns (13 patterns from config/component_patterns.json)
✅ Proper TypeScript types with validation
✅ Responsive Tailwind CSS classes (mobile-first)
✅ React best practices and hooks
✅ Automatic prop interfaces

⚠️ write_file LIMITATIONS:
• NO design tokens applied
• NO component patterns
• NO TypeScript type generation
• NO responsive design
• NO validation
• Just raw text → file

CRITICAL PARAMETER RULES:
1. generate_react_component uses "component_name" NOT "name"
2. generate_react_component uses "component_pattern" NOT "pattern"
3. component_pattern is MANDATORY - must be one of: sidebar, header, footer, messages, input, card, button, form, modal, list, hero, feature, pricing
4. generate_page_with_components ALWAYS REQUIRES 3 parameters:
   - "page_name": string (e.g., "Home", "Dashboard")
   - "page_path": string (full file path like "./demo/src/app/page.tsx")
   - "components": array of dicts with "name", "pattern", "variant"
5. Always use relative paths starting with "./" like "./demo/src/components"
6. Component names must be PascalCase: "ProductCard" not "product-card"

⚠️ COMPONENT PATTERN SELECTION:
Match pattern to component PURPOSE (not just name):
- ChatSidebar → sidebar pattern ✅ (NOT card ❌)
- LoginForm → form pattern ✅ (NOT card ❌)
- DashboardHeader → header pattern ✅ (NOT card ❌)
- StatCard → card pattern ✅
- UserList → list pattern ✅ (NOT card ❌)

RESPONSIVE DESIGN: All components MUST be mobile-first responsive (320px+, 768px+, 1024px+) using Tailwind prefixes (sm:, md:, lg:, xl:).

JSON RESPONSE FORMAT:
⚠️ Return a SINGLE JSON OBJECT, NOT an array. Only ONE action per response.
✅ CORRECT: {{"type": "tool_use", "tool_name": "...", "parameters": {{...}}}}

For completing:
{{
    "type": "complete",
    "message": "All tasks completed successfully"
}}

CRITICAL RULES:
1. ALWAYS use specialized tools for React components (never write_file!)
2. Use exact parameter names from examples above
3. Check tool descriptions and guidelines before using
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
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            logger.info(f"✅ Received response from LLM")
            
        except RateLimitError as e:
            error_details = {
                'type': 'RateLimitError',
                'message': str(e),
                'status_code': getattr(e, 'status_code', None),
                'headers': getattr(e, 'headers', None)
            }
            logger.error(f"❌ Rate limit exceeded: {str(e)}")
            logger.error(f"   Status: {error_details.get('status_code')}")
            logger.error(f"   Retry after: {error_details.get('headers', {}).get('retry-after', 'unknown')}")
            return AgentAction(
                type=ActionType.ERROR,
                message=f"Rate limit exceeded. Please wait and try again. Details: {str(e)}"
            )
        except AuthenticationError as e:
            logger.error(f"❌ Authentication failed: {str(e)}")
            logger.error(f"   Check your GROQ_API_KEY environment variable or config/settings.yaml")
            logger.error(f"   Status code: {getattr(e, 'status_code', 'unknown')}")
            return AgentAction(
                type=ActionType.ERROR,
                message=f"API authentication failed. Check your Groq API key. Details: {str(e)}"
            )
        except APITimeoutError as e:
            logger.error(f"❌ API timeout: {str(e)}")
            logger.error(f"   Request took too long to complete")
            logger.error(f"   Consider increasing timeout or retrying")
            return AgentAction(
                type=ActionType.ERROR,
                message=f"Groq API request timed out. Try again. Details: {str(e)}"
            )
        except APIConnectionError as e:
            logger.error(f"❌ API connection error: {str(e)}")
            logger.error(f"   Check your internet connection")
            logger.error(f"   Verify Groq API is accessible (https://api.groq.com)")
            return AgentAction(
                type=ActionType.ERROR,
                message=f"Failed to connect to Groq API. Check your internet connection. Details: {str(e)}"
            )
        except BadRequestError as e:
            logger.error(f"❌ Bad request: {str(e)}")
            logger.error(f"   Status code: {getattr(e, 'status_code', 'unknown')}")
            logger.error(f"   Response: {getattr(e, 'response', 'no response')}")
            return AgentAction(
                type=ActionType.ERROR,
                message=f"Invalid request to Groq API. Details: {str(e)}"
            )
        except APIError as e:
            logger.error(f"❌ Groq API error: {str(e)}")
            logger.error(f"   Error type: {type(e).__name__}")
            logger.error(f"   Status code: {getattr(e, 'status_code', 'unknown')}")
            logger.error(f"   Check Groq API status: https://status.groq.com")
            return AgentAction(
                type=ActionType.ERROR,
                message=f"Groq API error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ Unexpected error calling LLM: {str(e)}", exc_info=True)
            logger.error(f"   Error type: {type(e).__name__}")
            return AgentAction(
                type=ActionType.ERROR,
                message=f"Unexpected error: {str(e)}"
            )
        
        try:
            content = response.choices[0].message.content
            if content is None:
                logger.error(f"❌ LLM returned None content")
                return AgentAction(
                    type=ActionType.ERROR,
                    message="LLM returned empty response"
                )
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
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            return content if content else "Summary generation failed - no content returned"
            
        except (RateLimitError, AuthenticationError, APITimeoutError, APIConnectionError, BadRequestError, APIError) as e:
            logger.error(f"❌ API error during response synthesis: {str(e)}")
            return f"Unable to generate summary due to API error: {str(e)}"
        except Exception as e:
            logger.error(f"❌ Unexpected error during response synthesis: {str(e)}")
            return f"Unable to generate summary due to unexpected error: {str(e)}"
    
    async def execute(self, user_request: str, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Execute user request with task-based state management
        """
        logger.info(f"\n{'#'*80}")
        logger.info(f"🚀 AGENT EXECUTION START")
        logger.info(f"{'#'*80}")
        logger.info(f"📋 User Request: {user_request[:100]}...")
        logger.info(f"⚙️  Max Iterations: {max_iterations}")
        
        # Initialize context
        context = AgentContext(
            user_request=user_request,
            max_iterations=max_iterations
        )
        
        try:
            # 1. Generate task plan
            task_plan = await self.plan_tasks(user_request)
            context.task_plan = task_plan
            
            # 2. Execute tasks iteratively
            logger.info(f"\n{'='*80}")
            logger.info(f"🔄 TASK EXECUTION LOOP START")
            logger.info(f"{'='*80}\n")
            
            while context.iteration < max_iterations:
                context.iteration += 1
                
                # Get next task
                current_task = task_plan.get_next_task()
                if not current_task:
                    logger.info(f"✅ All tasks completed or no more retryable tasks")
                    break
                
                context.current_task = current_task
                
                # Log iteration start
                logger.info(f"\n{'='*80}")
                logger.info(f"🔄 ITERATION {context.iteration}")
                logger.info(f"{'='*80}")
                logger.info(f"🎯 Current Task: {current_task.name}")
                logger.info(f"📝 Description: {current_task.description}")
                if current_task.files_expected:
                    logger.info(f"� Expected files:")
                    for f in current_task.files_expected:
                        logger.info(f"   - {f}")
                if current_task.retry_count > 0:
                    logger.info(f"🔄 Retry attempt: {current_task.retry_count}/{current_task.max_retries}")
                
                # Mark task as in progress
                current_task.status = TaskStatus.IN_PROGRESS
                current_task.iteration_started = context.iteration
                
                # Decide action for this specific task
                action = await self.decide_action_for_task(context, current_task)
                
                if action.type == ActionType.COMPLETE:
                    # Task says it's complete, verify it
                    verified = current_task.verify_completion()
                    if verified:
                        current_task.status = TaskStatus.DONE
                        current_task.iteration_completed = context.iteration
                        logger.info(f"✅ Task verified and marked complete")
                        # Reset error counter on successful verification
                        context.reset_error_counter()
                    else:
                        current_task.status = TaskStatus.FAILED
                        error_msg = f"Task '{current_task.name}' claims complete but verification failed"
                        logger.warning(f"⚠️  {error_msg}")
                        context.add_error(error_msg)
                        
                        # Check if we should stop due to consecutive errors (AI hallucinating)
                        if context.should_stop_due_to_errors():
                            logger.error(f"\n{'='*80}")
                            logger.error(f"🛑 STOPPING: {context.consecutive_errors} consecutive validation failures")
                            logger.error(f"{'='*80}")
                            logger.error(f"Recent errors:")
                            for i, error in enumerate(context.errors[-4:], 1):
                                logger.error(f"  {i}. {error}")
                            logger.error(f"{'='*80}\n")
                            
                            current_task.error = f"Stopped after {context.consecutive_errors} consecutive validation failures"
                            break
                    continue
                
                # Check for API errors
                if action.type == ActionType.ERROR:
                    error_msg = action.message or "Unknown error"
                    logger.error(f"❌ Action returned ERROR: {error_msg}")
                    context.add_error(error_msg)
                    current_task.error = f"Action error: {error_msg}"
                    
                    # Check if we should stop due to consecutive errors
                    if context.should_stop_due_to_errors():
                        logger.error(f"\n{'='*80}")
                        logger.error(f"🛑 STOPPING: {context.consecutive_errors} consecutive errors")
                        logger.error(f"{'='*80}")
                        logger.error(f"Recent errors:")
                        for i, error in enumerate(context.errors[-4:], 1):
                            logger.error(f"  {i}. {error}")
                        logger.error(f"{'='*80}\n")
                        
                        # Mark task as failed
                        current_task.status = TaskStatus.FAILED
                        current_task.error = f"Stopped after {context.consecutive_errors} consecutive errors"
                        
                        break
                    
                    continue
                
                # Execute tool
                if action.tool_name and action.parameters:
                    result = await self.execute_tool(action.tool_name, action.parameters)
                    
                    # Update task state based on result (includes file verification)
                    self.update_task_state(current_task, action, result, context.iteration)
                    
                    # Add to context
                    context.add_tool_result(action.tool_name, result)
                    
                    # Check if tool execution AND verification succeeded
                    if result.success and current_task.status == TaskStatus.DONE:
                        # Both tool execution and file verification succeeded
                        context.reset_error_counter()
                    elif not result.success:
                        # Tool execution failed
                        context.add_error(f"Tool {action.tool_name} failed: {result.error}")
                        
                        # Check if we should stop due to consecutive errors
                        if context.should_stop_due_to_errors():
                            logger.error(f"\n{'='*80}")
                            logger.error(f"🛑 STOPPING: {context.consecutive_errors} consecutive errors")
                            logger.error(f"{'='*80}")
                            logger.error(f"Recent errors:")
                            for i, error in enumerate(context.errors[-4:], 1):
                                logger.error(f"  {i}. {error}")
                            logger.error(f"{'='*80}\n")
                            
                            # Mark task as failed
                            current_task.status = TaskStatus.FAILED
                            current_task.error = f"Stopped after {context.consecutive_errors} consecutive errors"
                            
                            break
                    elif current_task.status == TaskStatus.FAILED:
                        # Tool succeeded but verification failed (files not found)
                        error_msg = current_task.error or "File verification failed"
                        context.add_error(f"Verification failed for {action.tool_name}: {error_msg}")
                        
                        # Check if we should stop due to consecutive verification failures
                        if context.should_stop_due_to_errors():
                            logger.error(f"\n{'='*80}")
                            logger.error(f"🛑 STOPPING: {context.consecutive_errors} consecutive verification failures")
                            logger.error(f"{'='*80}")
                            logger.error(f"Recent errors:")
                            for i, error in enumerate(context.errors[-4:], 1):
                                logger.error(f"  {i}. {error}")
                            logger.error(f"{'='*80}\n")
                            
                            current_task.error = f"Stopped after {context.consecutive_errors} consecutive verification failures"
                            
                            break
                
                # Log progress
                progress = task_plan.get_progress()
                completion = task_plan.get_completion_percentage()
                logger.info(f"\n📊 Overall Progress: {progress['done']}/{progress['total']} ({completion:.1f}%)")
                
                # Check if we're done
                if task_plan.is_complete():
                    logger.info(f"🎉 All tasks completed and verified!")
                    break
            
            # 3. Final verification
            logger.info(f"\n{'='*80}")
            logger.info(f"🔍 FINAL VERIFICATION")
            logger.info(f"{'='*80}")
            
            verification = task_plan.verify_all_tasks()
            failed_verifications = [task_id for task_id, verified in verification.items() if not verified]
            
            if failed_verifications:
                logger.warning(f"⚠️  {len(failed_verifications)} tasks failed final verification")
                for task_id in failed_verifications:
                    task = next(t for t in task_plan.tasks if t.id == task_id)
                    logger.warning(f"   Task {task_id}: {task.name} - {task.error}")
            else:
                logger.info(f"✅ All completed tasks verified successfully")
            
            # 4. Summary
            logger.info(f"\n{'#'*80}")
            logger.info(f"📊 EXECUTION SUMMARY")
            logger.info(f"{'#'*80}")
            
            log_task_plan(task_plan, logger)
            
            files_created = task_plan.get_files_created()
            logger.info(f"� Total files created and verified: {len(files_created)}")
            for f in files_created:
                logger.info(f"   ✓ {f}")
            
            logger.info(f"🔄 Iterations used: {context.iteration}/{max_iterations}")
            logger.info(f"{'#'*80}\n")
            
            # Build response message
            if task_plan.is_complete():
                response_msg = f"Successfully completed all {len(task_plan.tasks)} tasks. Created {len(files_created)} files."
            else:
                completed = len([t for t in task_plan.tasks if t.status == TaskStatus.DONE])
                response_msg = f"Completed {completed}/{len(task_plan.tasks)} tasks."
            
            return {
                "success": task_plan.is_complete(),
                "response": response_msg,
                "task_plan": task_plan.to_dict(),
                "iterations": context.iteration,
                "files_created": files_created,
                "actions_taken": [tr.metadata.get("tool_name") for tr in context.tool_results]
            }
            
        except Exception as e:
            logger.error(f"❌ Agent execution failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "iterations": context.iteration
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
