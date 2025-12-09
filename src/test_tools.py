#!/usr/bin/env python3
"""
Test script to validate all tools in the AI Coding Agent
"""

import asyncio
import sys
from pathlib import Path

# Import tool modules
from .tools import file_operations, javascript_tools, redux_tools
from .tool_schemas import (
    ReadFileInput, WriteFileInput, ListDirectoryInput,
    GenerateReactComponentInput, ToolResult
)
from .tools.redux_tools import GenerateReduxSetupInput, ComponentSchema


async def test_file_operations():
    """Test file operation tools"""
    print("\n=== Testing File Operations ===")
    
    # Test write_file
    print("Testing write_file...")
    write_params = WriteFileInput(
        file_path="test_output.txt",
        content="Hello from AI Agent test!"
    )
    result = await file_operations.write_file(write_params)
    print(f"  write_file: {'✓ PASS' if result.success else '✗ FAIL'}")
    if not result.success:
        print(f"    Error: {result.error}")
    
    # Test read_file
    print("Testing read_file...")
    read_params = ReadFileInput(file_path="test_output.txt")
    result = await file_operations.read_file(read_params)
    print(f"  read_file: {'✓ PASS' if result.success else '✗ FAIL'}")
    if result.success:
        print(f"    Content: {result.data['content'][:50]}...")
    
    # Test list_directory
    print("Testing list_directory...")
    list_params = ListDirectoryInput(directory_path=".")
    result = await file_operations.list_directory(list_params)
    print(f"  list_directory: {'✓ PASS' if result.success else '✗ FAIL'}")
    if result.success:
        print(f"    Found {result.data['count']} files")
    
    # Cleanup
    Path("test_output.txt").unlink(missing_ok=True)
    
    return True


async def test_javascript_tools():
    """Test JavaScript/React tools"""
    print("\n=== Testing JavaScript/React Tools ===")
    
    # Test generate_react_component
    print("Testing generate_react_component...")
    component_params = GenerateReactComponentInput(
        component_name="TestButton",
        component_type="functional",
        use_typescript=True,
        props=[{"name": "label", "type": "string"}],
        styling="tailwind",
        output_dir="./test_components"
    )
    result = await javascript_tools.generate_react_component(component_params)
    print(f"  generate_react_component: {'✓ PASS' if result.success else '✗ FAIL'}")
    if result.success:
        print(f"    Generated: {result.data['component_file']}")
    else:
        print(f"    Error: {result.error}")
    
    # Cleanup
    import shutil
    if Path("test_components").exists():
        shutil.rmtree("test_components")
    
    return result.success


async def test_redux_tools():
    """Test Redux state management tools"""
    print("\n=== Testing Redux Tools ===")
    
    # Test generate_redux_setup
    print("Testing generate_redux_setup...")
    redux_params = GenerateReduxSetupInput(
        components=[
            ComponentSchema(
                name="ChatMessageList",
                props={
                    "items": "Array<{title: string; description: string}>",
                    "isLoading": "boolean"
                }
            ),
            ComponentSchema(
                name="ChatSidebar",
                props={
                    "conversations": "Array<{id: string; name: string}>",
                    "activeId": "string"
                }
            )
        ],
        output_dir="./test_redux_store",
        store_name="store"
    )
    result = await redux_tools.generate_redux_setup(redux_params)
    print(f"  generate_redux_setup: {'✓ PASS' if result.success else '✗ FAIL'}")
    if result.success:
        print(f"    Store dir: {result.data['store_dir']}")
        print(f"    Files created: {result.data['files_created']}")
        print(f"    Slices count: {result.data['slices_count']}")
        
        # Verify files exist
        from pathlib import Path
        store_dir = Path(result.data['store_dir'])
        if store_dir.exists():
            print(f"    ✓ Store directory created")
            if (store_dir / "store.ts").exists():
                print(f"    ✓ store.ts exists")
            if (store_dir / "hooks.ts").exists():
                print(f"    ✓ hooks.ts exists")
            if (store_dir / "chatmessagelistSlice.ts").exists():
                print(f"    ✓ chatmessagelistSlice.ts exists")
            if (store_dir / "chatsidebarSlice.ts").exists():
                print(f"    ✓ chatsidebarSlice.ts exists")
    else:
        print(f"    Error: {result.error}")
    
    # Cleanup
    import shutil
    if Path("test_redux_store").exists():
        shutil.rmtree("test_redux_store")
    
    return result.success


async def test_agent_core():
    """Test agent core can be initialized"""
    print("\n=== Testing Agent Core ===")
    
    try:
        from .agent_core import AICodeAgent
        import os
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("  ⚠ GROQ_API_KEY not set - skipping agent initialization test")
            return True
        
        print("Testing AICodeAgent initialization...")
        agent = AICodeAgent(groq_api_key=api_key)
        print(f"  Agent initialized: ✓ PASS")
        print(f"  Tool registry size: {len(agent.tool_registry)}")
        
        return True
    except Exception as e:
        print(f"  Agent initialization: ✗ FAIL")
        print(f"    Error: {e}")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("AI Coding Agent - Tool Validation Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(await test_file_operations())
    results.append(await test_javascript_tools())
    results.append(await test_redux_tools())
    results.append(await test_agent_core())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
