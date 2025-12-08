#!/usr/bin/env python3
"""Test imports after reorganization"""

import sys

try:
    print("Testing imports...")
    
    from src.agent_core import AICodeAgent
    print("✓ agent_core imported")
    
    from src.tool_schemas import ToolResult
    print("✓ tool_schemas imported")
    
    from src.tools import file_operations
    print("✓ tools.file_operations imported")
    
    from src.api_server import app
    print("✓ api_server imported")
    
    print("\n✓ All imports working correctly!")
    sys.exit(0)
    
except Exception as e:
    print(f"\n✗ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
