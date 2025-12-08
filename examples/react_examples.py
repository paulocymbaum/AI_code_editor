"""
React/TypeScript Code Generation Examples
Demonstrates how to use the AI agent for React development
"""

import asyncio
import os
from src.agent_core import AICodeAgent


async def example_create_react_component():
    """Example: Create a React component"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        """
        Create a React TypeScript component called 'UserCard' that:
        - Takes props: name (string), email (string), avatar (string)
        - Uses useState hook for managing hover state
        - Uses CSS modules for styling
        - Displays user information in a card layout
        """
    )
    
    print("React Component Generation:")
    print(result["response"])
    print()


async def example_create_nextjs_app():
    """Example: Create a Next.js application structure"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        """
        Create a Next.js 14 app with:
        1. A home page with SSR data fetching
        2. An about page
        3. A blog page with dynamic routes [slug]
        4. API route for /api/posts that returns JSON
        5. Use TypeScript for all files
        """,
        max_iterations=15
    )
    
    print("Next.js App Creation:")
    print(result["response"])
    print()


async def example_generate_api_routes():
    """Example: Generate API routes"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        """
        Create REST API routes for a blog:
        - GET /api/posts - List all posts
        - GET /api/posts/[id] - Get single post
        - POST /api/posts - Create new post
        - PUT /api/posts/[id] - Update post
        - DELETE /api/posts/[id] - Delete post
        
        Use TypeScript and Next.js App Router format
        """
    )
    
    print("API Routes Generation:")
    print(result["response"])
    print()


async def example_create_form_with_validation():
    """Example: Create a form with validation"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        """
        Create a React TypeScript form component for user registration:
        - Fields: email, password, confirmPassword, firstName, lastName
        - Use React Hook Form for form management
        - Add Zod schema validation
        - Show error messages
        - Handle form submission
        - Use Tailwind CSS for styling
        """
    )
    
    print("Form Component with Validation:")
    print(result["response"])
    print()


async def example_create_custom_hooks():
    """Example: Create custom React hooks"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        """
        Create custom React hooks:
        1. useLocalStorage - Sync state with localStorage
        2. useFetch - Fetch data with loading and error states
        3. useDebounce - Debounce a value
        4. useMediaQuery - Detect media query matches
        
        Use TypeScript with proper type definitions
        """
    )
    
    print("Custom Hooks Creation:")
    print(result["response"])
    print()


async def example_create_state_management():
    """Example: Set up state management"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        """
        Set up Zustand state management for a todo app:
        - Create store with todos array
        - Actions: addTodo, removeTodo, toggleTodo, updateTodo
        - Use TypeScript interfaces
        - Add persistence middleware
        - Create custom hooks for accessing store
        """
    )
    
    print("State Management Setup:")
    print(result["response"])
    print()


async def example_generate_tests():
    """Example: Generate tests for React components"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        """
        Generate Jest + React Testing Library tests for a Button component:
        - Test rendering with different props
        - Test click handlers
        - Test disabled state
        - Test loading state
        - Test accessibility
        - Use TypeScript
        """
    )
    
    print("Test Generation:")
    print(result["response"])
    print()


async def example_create_dashboard():
    """Example: Create a complete dashboard"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        """
        Create a dashboard application with:
        1. Layout component with sidebar and header
        2. Dashboard page with stats cards
        3. Charts using Recharts library
        4. Data table with sorting and filtering
        5. Dark mode toggle
        6. Responsive design with Tailwind CSS
        7. TypeScript throughout
        8. API integration for fetching data
        """,
        max_iterations=20
    )
    
    print("Dashboard Creation:")
    print(result["response"])
    print()


async def example_setup_project():
    """Example: Set up a complete project"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        """
        Set up a new Next.js 14 project with:
        1. Initialize with create-next-app (TypeScript, App Router, Tailwind)
        2. Install dependencies: zustand, react-hook-form, zod, axios
        3. Set up ESLint and Prettier configuration
        4. Create folder structure: components, hooks, lib, types, app
        5. Add TypeScript path aliases in tsconfig.json
        6. Create .env.example file
        7. Set up basic layout and global styles
        """,
        max_iterations=15
    )
    
    print("Project Setup:")
    print(result["response"])
    print()


async def example_refactor_to_typescript():
    """Example: Refactor JavaScript to TypeScript"""
    agent = AICodeAgent(groq_api_key=os.getenv("GROQ_API_KEY"))
    
    result = await agent.execute(
        """
        Refactor all .jsx files in src/components to TypeScript:
        1. Rename .jsx to .tsx
        2. Add proper type definitions for props
        3. Add return type annotations
        4. Fix any type errors
        5. Run TypeScript compiler to verify
        """
    )
    
    print("TypeScript Refactoring:")
    print(result["response"])
    print()


async def main():
    """Run all React/TypeScript examples"""
    print("=" * 70)
    print("AI Coding Agent - React/TypeScript Examples")
    print("=" * 70)
    print()
    
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable not set")
        return
    
    examples = [
        ("Create React Component", example_create_react_component),
        ("Create Next.js App", example_create_nextjs_app),
        ("Generate API Routes", example_generate_api_routes),
        ("Create Form with Validation", example_create_form_with_validation),
        ("Create Custom Hooks", example_create_custom_hooks),
        ("Set up State Management", example_create_state_management),
        ("Generate Tests", example_generate_tests),
        ("Create Dashboard", example_create_dashboard),
        ("Setup Project", example_setup_project),
        ("Refactor to TypeScript", example_refactor_to_typescript),
    ]
    
    for name, example_func in examples:
        print(f"\n{'=' * 70}")
        print(f"Example: {name}")
        print('=' * 70)
        try:
            await example_func()
        except Exception as e:
            print(f"Error: {str(e)}")
        
        await asyncio.sleep(1)
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
