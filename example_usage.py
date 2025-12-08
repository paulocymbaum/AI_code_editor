"""
Example Usage of AI Coding Agent
Demonstrates various use cases
"""

import asyncio
import os
from src.agent_core import AICodeAgent


async def example_file_operations():
    """Example: File operations"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        "Create a new Python file called 'hello.py' with a function that prints 'Hello, World!'"
    )
    
    print("File Operations Result:")
    print(result["response"])
    print(f"Iterations: {result['iterations']}")
    print()


async def example_code_analysis():
    """Example: Code analysis"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        "Analyze the structure of agent_core.py and list all classes and their methods"
    )
    
    print("Code Analysis Result:")
    print(result["response"])
    print()


async def example_git_operations():
    """Example: Git operations"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        "Show me the current git status and create a new branch called 'feature/test'"
    )
    
    print("Git Operations Result:")
    print(result["response"])
    print()


async def example_test_generation():
    """Example: Test generation"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        "Generate pytest tests for the read_file function in tools/file_operations.py"
    )
    
    print("Test Generation Result:")
    print(result["response"])
    print()


async def example_code_refactoring():
    """Example: Code improvement suggestions"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        "Review tools/execution.py and suggest improvements for performance and readability"
    )
    
    print("Code Refactoring Result:")
    print(result["response"])
    print()


async def example_multi_step_task():
    """Example: Complex multi-step task"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        """
        1. Create a new Python module called 'utils.py'
        2. Add a function to calculate factorial
        3. Generate tests for the function
        4. Run the tests
        5. If tests pass, commit the changes
        """,
        max_iterations=15
    )
    
    print("Multi-Step Task Result:")
    print(result["response"])
    print(f"Total iterations: {result['iterations']}")
    print(f"Tools used: {len(result['tool_results'])}")
    print()


async def main():
    """Run all examples"""
    print("=" * 60)
    print("AI Coding Agent - Example Usage")
    print("=" * 60)
    print()
    
    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable not set")
        print("Please set it in your .env file or export it:")
        print("export GROQ_API_KEY='your_key_here'")
        return
    
    # Run examples
    examples = [
        ("File Operations", example_file_operations),
        ("Code Analysis", example_code_analysis),
        ("Git Operations", example_git_operations),
        ("Test Generation", example_test_generation),
        ("Code Refactoring", example_code_refactoring),
        ("Multi-Step Task", example_multi_step_task),
    ]
    
    for name, example_func in examples:
        print(f"\n{'=' * 60}")
        print(f"Example: {name}")
        print('=' * 60)
        try:
            await example_func()
        except Exception as e:
            print(f"Error: {str(e)}")
        
        # Wait between examples
        await asyncio.sleep(1)
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
