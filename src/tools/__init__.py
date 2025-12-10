"""
Tools Package
Provides all tools for the AI coding agent
"""

# Use lazy imports to avoid circular import issues with tool_schemas.py
# Modules are imported on first access via __getattr__

__all__ = [
    'file_operations',
    'code_analysis',
    'execution',
    'git_operations',
    'context_search',
    'ai_assisted',
    'javascript_tools',
    'page_management',
    'design_system',
    'redux_tools',
]

def __getattr__(name):
    """Lazy import tool modules to avoid circular imports"""
    if name in __all__:
        # Import the module on demand
        from importlib import import_module
        module = import_module(f'.{name}', package='src.tools')
        globals()[name] = module
        return module
    raise AttributeError(f"module 'src.tools' has no attribute '{name}'")
