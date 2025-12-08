"""
Tools Package for AI Coding Agent
Provides modular tool implementations
"""

from .file_operations import (
    read_file,
    write_file,
    edit_file,
    delete_file,
    list_directory,
    search_files
)

from .code_analysis import (
    parse_code,
    find_definitions,
    find_references,
    get_diagnostics,
    analyze_dependencies
)

from .execution import (
    execute_command,
    run_tests,
    validate_syntax,
    benchmark_code
)

from .git_operations import (
    git_status,
    git_diff,
    git_commit,
    git_push,
    create_branch
)

from .context_search import (
    semantic_search,
    grep_search,
    get_context,
    summarize_codebase
)

from .ai_assisted import (
    generate_tests,
    explain_code,
    suggest_improvements,
    generate_docs
)

from .javascript_tools import (
    generate_react_component,
    generate_nextjs_page,
    generate_api_route,
    typescript_check,
    eslint_check,
    prettier_format,
    npm_command,
    generate_type_definitions
)

__all__ = [
    # File Operations
    'read_file', 'write_file', 'edit_file', 'delete_file', 
    'list_directory', 'search_files',
    
    # Code Analysis
    'parse_code', 'find_definitions', 'find_references', 
    'get_diagnostics', 'analyze_dependencies',
    
    # Execution
    'execute_command', 'run_tests', 'validate_syntax', 'benchmark_code',
    
    # Git Operations
    'git_status', 'git_diff', 'git_commit', 'git_push', 'create_branch',
    
    # Context & Search
    'semantic_search', 'grep_search', 'get_context', 'summarize_codebase',
    
    # AI-Assisted
    'generate_tests', 'explain_code', 'suggest_improvements', 'generate_docs',
    
    # JavaScript/TypeScript/React
    'generate_react_component', 'generate_nextjs_page', 'generate_api_route',
    'typescript_check', 'eslint_check', 'prettier_format', 'npm_command',
    'generate_type_definitions',
]
