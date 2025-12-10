"""
Tool Schema Definitions for AI Coding Agent
Uses Pydantic v2 for validation and serialization
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level for tool operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ToolCategory(str, Enum):
    """Categories of available tools"""
    FILE_OPERATIONS = "file_operations"
    CODE_ANALYSIS = "code_analysis"
    EXECUTION = "execution"
    GIT_OPERATIONS = "git_operations"
    CONTEXT_SEARCH = "context_search"
    AI_ASSISTED = "ai_assisted"


# ============================================================================
# Base Models
# ============================================================================

class ToolParameter(BaseModel):
    """Base model for tool parameters"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None


class ToolResult(BaseModel):
    """Standard result format for all tools"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None


class ToolDefinition(BaseModel):
    """Complete tool definition"""
    name: str
    description: str
    category: ToolCategory
    risk_level: RiskLevel
    requires_approval: bool
    parameters: List[ToolParameter]
    returns: str


# ============================================================================
# File Operations Schemas
# ============================================================================

class ReadFileInput(BaseModel):
    """Input schema for read_file tool"""
    file_path: str = Field(..., description="Path to file to read")
    encoding: Optional[str] = Field(default="utf-8", description="File encoding")
    
    @field_validator('file_path')
    @classmethod
    def validate_path(cls, v: str) -> str:
        if '..' in v:
            raise ValueError("Path traversal not allowed")
        return v


class WriteFileInput(BaseModel):
    """Input schema for write_file tool"""
    file_path: str = Field(..., description="Path to file to write")
    content: str = Field(..., description="Content to write")
    create_dirs: bool = Field(default=True, description="Create parent directories")
    
    @field_validator('file_path')
    @classmethod
    def validate_path(cls, v: str) -> str:
        if '..' in v:
            raise ValueError("Path traversal not allowed")
        return v


class EditFileInput(BaseModel):
    """Input schema for edit_file tool"""
    file_path: str = Field(..., description="Path to file to edit")
    edit_type: Literal["line_range", "search_replace", "ast_edit"] = Field(
        ..., description="Type of edit operation"
    )
    target: str = Field(..., description="Target to edit (line numbers, search pattern, or AST node)")
    new_content: str = Field(..., description="New content to insert")


class DeleteFileInput(BaseModel):
    """Input schema for delete_file tool"""
    file_path: str = Field(..., description="Path to file to delete")
    force: bool = Field(default=False, description="Force deletion without confirmation")


class ListDirectoryInput(BaseModel):
    """Input schema for list_directory tool"""
    directory_path: str = Field(..., description="Path to directory")
    recursive: bool = Field(default=False, description="List recursively")
    pattern: Optional[str] = Field(default=None, description="Filter pattern (glob)")


class SearchFilesInput(BaseModel):
    """Input schema for search_files tool"""
    query: str = Field(..., description="Search query")
    root_path: str = Field(default=".", description="Root path to search from")
    file_types: Optional[List[str]] = Field(default=None, description="File extensions to include")


# ============================================================================
# Code Analysis Schemas
# ============================================================================

class ParseCodeInput(BaseModel):
    """Input schema for parse_code tool"""
    file_path: str = Field(..., description="Path to code file")
    language: Optional[str] = Field(default=None, description="Programming language (auto-detect if None)")


class FindDefinitionsInput(BaseModel):
    """Input schema for find_definitions tool"""
    symbol_name: str = Field(..., description="Name of symbol to find")
    scope: Optional[str] = Field(default=None, description="Scope to search in")
    file_path: Optional[str] = Field(default=None, description="Specific file to search")


class FindReferencesInput(BaseModel):
    """Input schema for find_references tool"""
    symbol_name: str = Field(..., description="Name of symbol to find references for")
    scope: Optional[str] = Field(default="project", description="Scope to search (file, project, workspace)")


class GetDiagnosticsInput(BaseModel):
    """Input schema for get_diagnostics tool"""
    file_path: str = Field(..., description="Path to file to check")
    check_types: bool = Field(default=True, description="Run type checking")
    check_style: bool = Field(default=True, description="Run style checking")


class AnalyzeDependenciesInput(BaseModel):
    """Input schema for analyze_dependencies tool"""
    root_path: str = Field(default=".", description="Root path to analyze")
    depth: int = Field(default=3, description="Maximum depth to analyze")


# ============================================================================
# Execution Schemas
# ============================================================================

class ExecuteCommandInput(BaseModel):
    """Input schema for execute_command tool"""
    command: str = Field(..., description="Command to execute")
    working_dir: Optional[str] = Field(default=None, description="Working directory")
    timeout: int = Field(default=30, description="Timeout in seconds")
    env_vars: Optional[Dict[str, str]] = Field(default=None, description="Environment variables")
    
    @field_validator('command')
    @classmethod
    def validate_command(cls, v: str) -> str:
        # Blacklist dangerous commands
        dangerous = ['rm -rf /', 'dd if=', 'mkfs', ':(){:|:&};:']
        if any(cmd in v for cmd in dangerous):
            raise ValueError("Dangerous command detected")
        return v


class RunTestsInput(BaseModel):
    """Input schema for run_tests tool"""
    test_path: str = Field(..., description="Path to test file or directory")
    framework: Literal["pytest", "unittest", "jest", "mocha", "vitest"] = Field(
        ..., description="Test framework to use"
    )
    coverage: bool = Field(default=False, description="Generate coverage report")


class ValidateSyntaxInput(BaseModel):
    """Input schema for validate_syntax tool"""
    file_path: str = Field(..., description="Path to file to validate")
    language: Optional[str] = Field(default=None, description="Programming language")


class BenchmarkCodeInput(BaseModel):
    """Input schema for benchmark_code tool"""
    file_path: str = Field(..., description="Path to file containing code")
    function_name: str = Field(..., description="Function to benchmark")
    iterations: int = Field(default=1000, description="Number of iterations")


# ============================================================================
# Git Operations Schemas
# ============================================================================

class GitStatusInput(BaseModel):
    """Input schema for git_status tool"""
    repo_path: str = Field(default=".", description="Path to repository")


class GitDiffInput(BaseModel):
    """Input schema for git_diff tool"""
    repo_path: str = Field(default=".", description="Path to repository")
    target: Optional[str] = Field(default=None, description="Commit/branch to diff against")
    staged: bool = Field(default=False, description="Show staged changes only")


class GitCommitInput(BaseModel):
    """Input schema for git_commit tool"""
    repo_path: str = Field(default=".", description="Path to repository")
    message: str = Field(..., description="Commit message")
    files: Optional[List[str]] = Field(default=None, description="Specific files to commit")


class GitPushInput(BaseModel):
    """Input schema for git_push tool"""
    repo_path: str = Field(default=".", description="Path to repository")
    remote: str = Field(default="origin", description="Remote name")
    branch: Optional[str] = Field(default=None, description="Branch to push (current if None)")


class CreateBranchInput(BaseModel):
    """Input schema for create_branch tool"""
    repo_path: str = Field(default=".", description="Path to repository")
    branch_name: str = Field(..., description="Name of new branch")
    checkout: bool = Field(default=True, description="Checkout branch after creation")


# ============================================================================
# Context & Search Schemas
# ============================================================================

class SemanticSearchInput(BaseModel):
    """Input schema for semantic_search tool"""
    query: str = Field(..., description="Search query")
    top_k: int = Field(default=5, description="Number of results to return")
    file_types: Optional[List[str]] = Field(default=None, description="File types to search")


class GrepSearchInput(BaseModel):
    """Input schema for grep_search tool"""
    pattern: str = Field(..., description="Search pattern (regex)")
    path: str = Field(default=".", description="Path to search in")
    case_sensitive: bool = Field(default=False, description="Case sensitive search")


class GetContextInput(BaseModel):
    """Input schema for get_context tool"""
    task_description: str = Field(..., description="Description of current task")
    max_tokens: int = Field(default=4000, description="Maximum tokens to return")


class SummarizeCodebaseInput(BaseModel):
    """Input schema for summarize_codebase tool"""
    root_path: str = Field(default=".", description="Root path to summarize")
    detail_level: Literal["high", "medium", "low"] = Field(
        default="medium", description="Level of detail"
    )


# ============================================================================
# AI-Assisted Schemas
# ============================================================================

class GenerateTestsInput(BaseModel):
    """Input schema for generate_tests tool"""
    file_path: str = Field(..., description="Path to file to generate tests for")
    function_name: Optional[str] = Field(default=None, description="Specific function to test")
    framework: Literal["pytest", "unittest", "jest", "mocha"] = Field(
        default="pytest", description="Test framework"
    )


class ExplainCodeInput(BaseModel):
    """Input schema for explain_code tool"""
    code_snippet: str = Field(..., description="Code to explain")
    detail_level: Literal["high", "medium", "low"] = Field(
        default="medium", description="Level of detail"
    )


class SuggestImprovementsInput(BaseModel):
    """Input schema for suggest_improvements tool"""
    file_path: str = Field(..., description="Path to file to analyze")
    focus_areas: Optional[List[str]] = Field(
        default=None, description="Specific areas to focus on (performance, readability, etc.)"
    )


class GenerateDocsInput(BaseModel):
    """Input schema for generate_docs tool"""
    file_path: str = Field(..., description="Path to file to document")
    format: Literal["markdown", "rst", "docstring"] = Field(
        default="markdown", description="Documentation format"
    )
    include_examples: bool = Field(default=True, description="Include usage examples")


# ============================================================================
# Tool Registry
# ============================================================================

TOOL_INPUT_SCHEMAS = {
    # File Operations
    "read_file": ReadFileInput,
    "write_file": WriteFileInput,
    "edit_file": EditFileInput,
    "delete_file": DeleteFileInput,
    "list_directory": ListDirectoryInput,
    "search_files": SearchFilesInput,
    
    # Code Analysis
    "parse_code": ParseCodeInput,
    "find_definitions": FindDefinitionsInput,
    "find_references": FindReferencesInput,
    "get_diagnostics": GetDiagnosticsInput,
    "analyze_dependencies": AnalyzeDependenciesInput,
    
    # Execution
    "execute_command": ExecuteCommandInput,
    "run_tests": RunTestsInput,
    "validate_syntax": ValidateSyntaxInput,
    "benchmark_code": BenchmarkCodeInput,
    
    # Git Operations
    "git_status": GitStatusInput,
    "git_diff": GitDiffInput,
    "git_commit": GitCommitInput,
    "git_push": GitPushInput,
    "create_branch": CreateBranchInput,
    
    # Context & Search
    "semantic_search": SemanticSearchInput,
    "grep_search": GrepSearchInput,
    "get_context": GetContextInput,
    "summarize_codebase": SummarizeCodebaseInput,
    
    # AI-Assisted
    "generate_tests": GenerateTestsInput,
    "explain_code": ExplainCodeInput,
    "suggest_improvements": SuggestImprovementsInput,
    "generate_docs": GenerateDocsInput,
}


# ============================================================================
# JavaScript/TypeScript/React Schemas
# ============================================================================

class GenerateReactComponentInput(BaseModel):
    """Input for generating React components"""
    component_name: str = Field(..., description="Name of the component (PascalCase)")
    component_type: str = Field(default="functional", description="functional or class")
    use_typescript: bool = Field(default=True, description="Generate TypeScript")
    props: Optional[List[Dict[str, str]]] = Field(default=None, description="Component props")
    hooks: Optional[List[str]] = Field(default=None, description="React hooks to use")
    styling: str = Field(default="tailwind", description="tailwind, css-modules, styled-components")
    component_pattern: Optional[str] = Field(
        default=None, 
        description="Component pattern: card, button, form, modal, list, hero, feature, pricing, sidebar, header, footer, messages, input, or custom"
    )
    variant: Optional[str] = Field(
        default="primary",
        description="Style variant: primary, secondary, outline, ghost, success, warning, error"
    )
    with_redux: bool = Field(
        default=False,
        description="Connect component to Redux store with useAppSelector hooks"
    )
    file_path: Optional[str] = Field(
        default=None, 
        description="Full file path including filename (e.g., demo/src/app/store/uiSlice.ts). If provided, takes precedence over output_dir."
    )
    output_dir: str = Field(default="./src/components", description="Output directory (used only if file_path is not provided)")


class GenerateNextJSPageInput(BaseModel):
    """Input for generating Next.js pages"""
    page_name: str = Field(..., description="Page name (kebab-case)")
    route: str = Field(..., description="Route path (e.g., /about, /blog/[slug])")
    use_typescript: bool = Field(default=True, description="Generate TypeScript")
    data_fetching: Optional[str] = Field(default=None, description="SSR, SSG, ISR, or CSR")
    layout: Optional[str] = Field(default=None, description="Layout to use")
    output_dir: str = Field(default="./src/app", description="Output directory")


class GenerateAPIRouteInput(BaseModel):
    """Input for generating API routes"""
    route_name: str = Field(..., description="API route name")
    method: str = Field(default="GET", description="HTTP method")
    use_typescript: bool = Field(default=True, description="Generate TypeScript")
    framework: str = Field(default="nextjs", description="nextjs, express, fastify")
    output_dir: str = Field(default="./src/app/api", description="Output directory")


class TypeScriptCheckInput(BaseModel):
    """Input for TypeScript checking"""
    file_path: Optional[str] = Field(default=None, description="Specific file to check")
    project_root: str = Field(default=".", description="Project root directory")
    strict: bool = Field(default=True, description="Use strict mode")


class ESLintCheckInput(BaseModel):
    """Input for ESLint checking"""
    file_path: Optional[str] = Field(default=None, description="Specific file to check")
    fix: bool = Field(default=False, description="Auto-fix issues")
    project_root: str = Field(default=".", description="Project root directory")


class PrettierFormatInput(BaseModel):
    """Input for Prettier formatting"""
    file_path: str = Field(..., description="File to format")
    write: bool = Field(default=True, description="Write changes to file")


class NpmCommandInput(BaseModel):
    """Input for npm commands"""
    command: str = Field(..., description="npm command to run (e.g., 'install', 'run build')")
    args: Optional[List[str]] = Field(default=None, description="Additional arguments for the command")
    working_dir: Optional[str] = Field(default=None, description="Working directory")


class GenerateTypeDefinitionsInput(BaseModel):
    """Input for generating TypeScript type definitions"""
    source: str = Field(..., description="Source (API response, JSON, etc.)")
    type_name: str = Field(..., description="Name for the type/interface")
    output_file: str = Field(..., description="Output file path")


# ============================================================================
# Page Management Schemas
# ============================================================================

class UpdatePageImportsInput(BaseModel):
    """Updates existing page file to import specified components. 
    
    Does NOT generate components - only updates imports in existing page.
    Use this to fix broken imports or add new component references."""
    page_path: str = Field(..., description="Path to the existing page file to update")
    components: List[Dict[str, str]] = Field(
        ..., 
        description="List of components with 'name' and 'path' keys. Path can be relative or absolute."
    )
    replace_all: bool = Field(
        default=False, 
        description="If True, removes all existing component imports and adds only these. If False, adds to existing imports."
    )


class GeneratePageWithComponentsInput(BaseModel):
    """Generates React components AND creates a page that imports them. All-in-one solution.
    
    This is the RECOMMENDED tool for creating new pages with components:
    1. Generates all specified components using design system patterns
    2. Creates the page file
    3. Automatically imports all components into the page
    4. Wires up components with proper props
    
    Use this instead of calling generate_react_component multiple times + update_page_imports."""
    page_name: str = Field(..., description="Name of the page (e.g., 'products', 'about')")
    page_path: str = Field(..., description="Full path where page should be created (e.g., './demo/src/app/products/page.tsx')")
    components: List[Dict[str, Any]] = Field(
        ..., 
        description="REQUIRED: Components to generate. Each dict MUST have: 'name' (string, PascalCase), 'pattern' (REQUIRED: card|button|form|modal|list|hero|feature|pricing|sidebar|header|footer|messages|input|custom), optional 'variant' (primary|secondary|outline|ghost) and 'props_data' (dict). Pattern is MANDATORY - choose based on component purpose."
    )
    title: Optional[str] = Field(default=None, description="Page title text (used in h1)")
    description: Optional[str] = Field(default=None, description="Page description text (used in subtitle)")
    layout_type: Optional[str] = Field(
        default="grid",
        description="Page layout type: 'grid' (responsive grid), 'chat' (sidebar + main area), 'dashboard' (header + grid), 'landing' (stacked sections), 'app' (sidebar + content + details)"
    )


class OrganizeProjectFilesInput(BaseModel):
    """Moves or copies files from source to target directory, organized by file type.
    
    WARNING: This tool physically moves files. Use with caution!
    - Target directory cannot be inside source (prevents infinite loops)
    - If clean_source=True, original files are DELETED after moving
    - Creates subdirectories like 'components/', 'styles/', 'types/', etc.
    
    Use cases: Reorganizing messy project structure, archiving old files"""
    source_dir: str = Field(..., description="Source directory containing files to organize")
    target_base_dir: str = Field(..., description="Target directory where organized files will be placed. MUST be outside source_dir.")
    create_subdirs: bool = Field(
        default=True, 
        description="If True, creates subdirectories (components/, styles/, etc). If False, all files go to target_base_dir root."
    )
    clean_source: bool = Field(
        default=False, 
        description="DANGER: If True, deletes original files from source after moving. Use False to copy instead."
    )


class CleanDemoFolderInput(BaseModel):
    """Archives or deletes files in demo folder except those matching keep patterns.
    
    WARNING: This tool deletes files! ALWAYS use archive_dir to create backups.
    - Keeps files matching patterns in keep_patterns
    - Archives removed files to archive_dir (if provided)
    - If archive_dir is None, files are permanently deleted
    - Will NOT clean system directories (/, ~/Documents, etc)
    
    Use case: Cleaning up test/demo components while keeping essential config files"""
    demo_dir: str = Field(default="./demo", description="Demo directory path to clean")
    keep_patterns: List[str] = Field(
        default=["*.config.*", "package.json", "tsconfig.json"],
        description="Glob patterns for files to keep (e.g., '*.config.*', 'layout.tsx')"
    )
    archive_dir: Optional[str] = Field(
        default=None, 
        description="RECOMMENDED: Directory to archive removed files. If None, files are permanently deleted!"
    )


# ============================================================================
# Design System Schema
# ============================================================================

class GenerateDesignSystemInput(BaseModel):
    """Input for generating a complete design system"""
    project_path: str = Field(..., description="Root path of the project")
    framework: str = Field(
        default="nextjs",
        description="Framework: nextjs, react, vite"
    )
    include_dark_mode: bool = Field(
        default=True,
        description="Include dark mode support"
    )
    include_component_patterns: bool = Field(
        default=True,
        description="Generate component pattern CSS"
    )
    include_docs: bool = Field(
        default=True,
        description="Generate documentation"
    )
    include_layout: bool = Field(
        default=True,
        description="Generate Next.js layout file (for Next.js projects)"
    )
    css_output_path: Optional[str] = Field(
        default=None,
        description="Custom CSS output path (default: src/app/globals.css for Next.js)"
    )
    tailwind_config_path: Optional[str] = Field(
        default=None,
        description="Custom Tailwind config path (default: ./tailwind.config.js)"
    )


# ============================================================================
# Redux Schema
# ============================================================================

class ComponentSchema(BaseModel):
    """Schema for a component's props"""
    name: str
    props: Dict[str, Any] = Field(default_factory=dict)


class GenerateReduxSetupInput(BaseModel):
    """Input for generating Redux store setup"""
    components: List[ComponentSchema] = Field(
        description="List of component schemas with their props"
    )
    output_dir: str = Field(
        description="Directory to create Redux files (typically demo/src/store)"
    )
    store_name: str = Field(
        default="store",
        description="Name of the store file"
    )

# Update TOOL_INPUT_SCHEMAS registry
TOOL_INPUT_SCHEMAS.update({
    # JavaScript/TypeScript/React
    "generate_react_component": GenerateReactComponentInput,
    "generate_nextjs_page": GenerateNextJSPageInput,
    "generate_api_route": GenerateAPIRouteInput,
    "typescript_check": TypeScriptCheckInput,
    "eslint_check": ESLintCheckInput,
    "prettier_format": PrettierFormatInput,
    "npm_command": NpmCommandInput,
    "generate_type_definitions": GenerateTypeDefinitionsInput,
    # Page Management
    "update_page_imports": UpdatePageImportsInput,
    "generate_page_with_components": GeneratePageWithComponentsInput,
    "organize_project_files": OrganizeProjectFilesInput,
    "clean_demo_folder": CleanDemoFolderInput,
    # Design System
    "generate_design_system": GenerateDesignSystemInput,
    # Redux State Management
    "generate_redux_setup": GenerateReduxSetupInput,
})
