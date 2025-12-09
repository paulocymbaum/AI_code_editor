#!/usr/bin/env python3
"""
Dynamic Page Generator - Universal Function
Creates ANY page/UI by passing parameters to agent core
"""

import asyncio
import os
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from src.agent_core import AICodeAgent

load_dotenv()


async def generate_page(
    page_name: str,
    page_description: str,
    components: Optional[List[Dict[str, str]]] = None,
    features: Optional[List[str]] = None,
    with_redux: bool = False,
    output_dir: str = "./demo",
    max_iterations: int = 20
) -> Dict[str, Any]:
    """
    Universal page generator - creates ANY page with ANY components
    
    Args:
        page_name: Name of the page (e.g., "dashboard", "profile", "checkout")
        page_description: What the page should do/contain
        components: List of components to generate, each with:
            - name: Component name (e.g., "Sidebar", "ProductCard")
            - pattern: Component pattern (sidebar, header, card, form, list, etc.)
            - variant: Style variant (primary, secondary, etc.)
        features: List of specific features (e.g., "animations", "responsive", "dark mode")
        with_redux: Whether to include Redux state management
        output_dir: Where to generate files
        max_iterations: Max agent iterations
    
    Returns:
        Dict with success status, response, and generated files
    
    Example:
        result = await generate_page(
            page_name="dashboard",
            page_description="Admin dashboard with metrics and charts",
            components=[
                {"name": "Sidebar", "pattern": "sidebar", "variant": "primary"},
                {"name": "StatCard", "pattern": "card", "variant": "primary"}
            ],
            features=["animations", "responsive", "dark mode"],
            with_redux=True
        )
    """
    
    # Get API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {
            "success": False,
            "error": "GROQ_API_KEY not set",
            "response": None
        }
    
    # Initialize agent with detailed logging
    log_file = f"{page_name}_generation.log"
    print(f"🤖 Initializing agent for '{page_name}' page...")
    print(f"📝 Detailed logs will be written to: {log_file}")
    agent = AICodeAgent(groq_api_key=api_key, log_file=log_file)
    
    # Build the request dynamically
    request_parts = [f"Create a {page_name} page with the following requirements:\n"]
    
    # Add description
    request_parts.append(f"PURPOSE: {page_description}\n")
    
    # IMPORTANT: Generate design system first
    request_parts.append("\nSTEP 1 - DESIGN SYSTEM:")
    request_parts.append("  First, use generate_design_system tool with REQUIRED parameters:")
    request_parts.append(f'  project_path: "{output_dir}"')
    request_parts.append('  framework: "nextjs"')
    request_parts.append('  include_dark_mode: true')
    request_parts.append('  include_component_patterns: true')
    request_parts.append('  This will generate globals.css with all design system classes')
    request_parts.append("")
    
    # Add components
    if components:
        request_parts.append("\nSTEP 2 - COMPONENTS TO GENERATE:")
        for comp in components:
            name = comp.get("name", "Component")
            pattern = comp.get("pattern", "custom")
            variant = comp.get("variant", "primary")
            request_parts.append(f"  - {name}: pattern={pattern}, variant={variant}")
    
    # Add features
    if features:
        request_parts.append("\nFEATURES:")
        for feature in features:
            request_parts.append(f"  - {feature}")
    
    # Build component list for tool call
    if components:
        request_parts.append("\nSTEP 3 - USE generate_page_with_components tool with:")
        request_parts.append(f'  page_name: "{page_name}"')
        # ⚠️ CRITICAL: For home/main pages, use root path (src/app/page.tsx)
        # For nested pages like "about", "contact", use nested path (src/app/about/page.tsx)
        if page_name.lower() in ["home", "dashboard", "index", "main"]:
            page_path = f'"{output_dir}/src/app/page.tsx"'
        else:
            page_path = f'"{output_dir}/src/app/{page_name}/page.tsx"'
        request_parts.append(f'  page_path: {page_path}')
        
        # Add layout instructions for dashboard
        if page_name.lower() == "dashboard":
            request_parts.append('  layout_type: "dashboard"')
            request_parts.append("")
            request_parts.append("  📐 LAYOUT STRUCTURE (CRITICAL - Follow this structure):")
            request_parts.append("  Create a professional dashboard layout with:")
            request_parts.append("  - Sidebar: Fixed on left side (w-64), full height, collapsible")
            request_parts.append("  - Main Area: Flex-1 on right side with:")
            request_parts.append("    * Header: Full width at top, sticky")
            request_parts.append("    * Stats Grid: 3-4 StatCards in responsive grid below header")
            request_parts.append("    * TabNavigation: Below stats, controls main content area")
            request_parts.append("    * Footer: At bottom of main area")
            request_parts.append("  - Use flex layout: Sidebar | Main Content (flex-col)")
            request_parts.append("  - Mobile: Sidebar collapses to hamburger menu")
            request_parts.append("")
        
        request_parts.append("  components: [")
        for comp in components:
            request_parts.append(f'    {{"name": "{comp.get("name")}", "pattern": "{comp.get("pattern")}", "variant": "{comp.get("variant")}"}}')
        request_parts.append("  ]")
    
    # Add Redux if requested
    if with_redux:
        request_parts.append("\nSTEP 4 - STATE MANAGEMENT:")
        request_parts.append("  Then use generate_redux_setup tool with:")
        request_parts.append("  components: [] (auto-detect)")
        request_parts.append(f'  output_dir: "{output_dir}/src/store"')
        request_parts.append('  store_name: "store"')
    
    # Add general requirements
    request_parts.append("\nGENERAL REQUIREMENTS:")
    request_parts.append("  - Use TypeScript for type safety")
    request_parts.append("  - Components MUST use design system CSS classes from globals.css")
    request_parts.append("  - Make it responsive (mobile, tablet, desktop)")
    request_parts.append("  - Add proper accessibility (ARIA labels)")
    request_parts.append(f"  - Output directory: {output_dir}")
    
    request = "\n".join(request_parts)
    
    # Execute
    print(f"🚀 Generating '{page_name}' page...")
    print("=" * 80)
    print(f"\n📋 Request:\n{request}\n")
    print("=" * 80)
    
    result = await agent.execute(request, max_iterations=max_iterations)
    
    # Display results
    print("\n" + "=" * 80)
    if result["success"]:
        print("✅ SUCCESS!")
    else:
        print("❌ FAILED!")
    
    print(f"\n📊 Statistics:")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Tools used: {len(result['tool_results'])}")
    
    if result['tool_results']:
        print(f"\n🔧 Tools executed:")
        for tr in result['tool_results']:
            status = "✅" if tr.success else "❌"
            tool_name = tr.metadata.get('tool_name', 'unknown')
            print(f"  {status} {tool_name}")
    
    print(f"\n💬 Response:\n{result['response']}")
    print("=" * 80)
    
    return result


# ============================================================================
# Example Usage Functions
# ============================================================================

async def example_dashboard():
    """Example: Create dashboard page"""
    return await generate_page(
        page_name="dashboard",
        page_description="Admin dashboard with sidebar, metrics, and data visualization",
        components=[
            {"name": "Sidebar", "pattern": "sidebar", "variant": "primary"},
            {"name": "Header", "pattern": "header", "variant": "primary"},
            {"name": "StatCard", "pattern": "card", "variant": "primary"},
            {"name": "TabNavigation", "pattern": "list", "variant": "primary"},
            {"name": "Footer", "pattern": "footer", "variant": "secondary"}
        ],
        features=["animations", "responsive", "dark mode", "collapsible sidebar"],
        with_redux=True
    )


async def example_ecommerce():
    """Example: Create e-commerce product page"""
    return await generate_page(
        page_name="products",
        page_description="E-commerce product listing with filters and shopping cart",
        components=[
            {"name": "ProductCard", "pattern": "card", "variant": "primary"},
            {"name": "FilterSidebar", "pattern": "sidebar", "variant": "secondary"},
            {"name": "CartButton", "pattern": "button", "variant": "primary"},
            {"name": "ProductList", "pattern": "list", "variant": "primary"}
        ],
        features=["responsive", "grid layout", "hover effects"],
        with_redux=True
    )


async def example_blog():
    """Example: Create blog page"""
    return await generate_page(
        page_name="blog",
        page_description="Blog with article cards and categories",
        components=[
            {"name": "ArticleCard", "pattern": "card", "variant": "primary"},
            {"name": "CategoryFilter", "pattern": "list", "variant": "secondary"},
            {"name": "Hero", "pattern": "hero", "variant": "primary"}
        ],
        features=["responsive", "search", "pagination"],
        with_redux=False
    )


async def example_login():
    """Example: Create login page"""
    return await generate_page(
        page_name="login",
        page_description="User authentication with login form",
        components=[
            {"name": "LoginForm", "pattern": "form", "variant": "primary"},
            {"name": "Hero", "pattern": "hero", "variant": "primary"}
        ],
        features=["validation", "responsive", "error handling"],
        with_redux=False
    )


async def example_chat():
    """Example: Create chat interface"""
    return await generate_page(
        page_name="chat",
        page_description="Real-time chat interface with message list and input",
        components=[
            {"name": "ChatSidebar", "pattern": "sidebar", "variant": "primary"},
            {"name": "MessageList", "pattern": "messages", "variant": "primary"},
            {"name": "ChatInput", "pattern": "input", "variant": "primary"},
            {"name": "ChatHeader", "pattern": "header", "variant": "primary"}
        ],
        features=["real-time updates", "responsive", "animations"],
        with_redux=True
    )


# ============================================================================
# Interactive CLI
# ============================================================================

async def interactive_mode():
    """Interactive mode for custom page generation"""
    
    print("\n🎨 CUSTOM PAGE GENERATOR\n")
    
    # Get page details
    page_name = input("Page name (e.g., dashboard, profile, checkout): ").strip()
    page_description = input("Page description: ").strip()
    
    # Get components
    print("\nAdd components (press Enter with empty name to finish):")
    components = []
    while True:
        name = input("  Component name (or Enter to finish): ").strip()
        if not name:
            break
        pattern = input(f"  Pattern for {name} (sidebar/header/card/form/list/button/etc): ").strip()
        variant = input(f"  Variant (primary/secondary/etc): ").strip() or "primary"
        components.append({"name": name, "pattern": pattern, "variant": variant})
    
    # Get features
    print("\nAdd features (comma-separated, e.g., animations, responsive, dark mode):")
    features_input = input("  Features: ").strip()
    features = [f.strip() for f in features_input.split(",")] if features_input else []
    
    # Redux?
    with_redux_input = input("\nUse Redux state management? (y/n): ").strip().lower()
    with_redux = with_redux_input == "y"
    
    # Generate
    return await generate_page(
        page_name=page_name,
        page_description=page_description,
        components=components if components else None,
        features=features if features else None,
        with_redux=with_redux
    )


async def main():
    """Main function with menu"""
    
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║          🎨 DYNAMIC PAGE GENERATOR - Universal Function 🎨        ║
║                                                                   ║
║  Generate ANY page with ANY components using agent core          ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    print("\nSelect an example or create custom:\n")
    print("1. Dashboard (with sidebar, tabs, Redux)")
    print("2. E-commerce Products (with cart, filters)")
    print("3. Blog (with articles, categories)")
    print("4. Login Page (with form, validation)")
    print("5. Chat Interface (with messages, sidebar)")
    print("6. Custom Page (interactive mode)")
    print("7. Exit")
    print()
    
    choice = input("Enter choice (1-7): ").strip()
    
    if choice == "1":
        await example_dashboard()
    elif choice == "2":
        await example_ecommerce()
    elif choice == "3":
        await example_blog()
    elif choice == "4":
        await example_login()
    elif choice == "5":
        await example_chat()
    elif choice == "6":
        await interactive_mode()
    elif choice == "7":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Error: GROQ_API_KEY not set!")
        exit(1)
    
    asyncio.run(main())
