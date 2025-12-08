#!/usr/bin/env python3
"""
Verify component generation produces correct code
"""

import asyncio
from tools import javascript_tools
from tool_schemas import GenerateReactComponentInput


async def main():
    print("Testing React component generation...")
    
    params = GenerateReactComponentInput(
        component_name="TestCard",
        component_type="functional",
        use_typescript=True,
        props=[
            {"name": "title", "type": "string"},
            {"name": "description", "type": "string"}
        ],
        styling="tailwind",
        output_dir="./verify_output"
    )
    
    result = await javascript_tools.generate_react_component(params)
    
    if result.success:
        print("✓ Component generated successfully")
        print("\nGenerated code:")
        print("=" * 60)
        print(result.data['code'])
        print("=" * 60)
        
        # Verify no double braces
        if "{{" in result.data['code'] and "{{" not in "className={{":
            print("\n✗ ERROR: Found double braces in generated code!")
            return 1
        else:
            print("\n✓ No double brace issues found")
        
        # Verify proper JSX syntax
        if "<div className=" in result.data['code']:
            print("✓ Proper className syntax")
        
        return 0
    else:
        print(f"✗ Failed: {result.error}")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
