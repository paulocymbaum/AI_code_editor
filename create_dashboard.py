#!/usr/bin/env python3
"""
Dynamic Page Creator - Works for ANY page type
Uses agent core with correct parameters
"""

import asyncio
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from src.agent_core import AICodeAgent

load_dotenv()


async def create_page(
    page_name: str,
    components: List[Dict[str, str]],
    layout_type: str = "default",
    enable_redux: bool = False,
    additional_requirements: Optional[str] = None,
    output_dir: str = "./demo"
):
    """
    Create dashboard with sidebar, tabs, and Redux state management
    """
    
    # Get API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not set!")
        return
    
    # Initialize agent
    print("🤖 Initializing agent...")
    agent = AICodeAgent(groq_api_key=api_key)
    
    # The request
    request = """
Create a dashboard application at ./demo with:

STEP 1 - Generate page with components:
Use generate_page_with_components to create:
- Page: dashboard
- Path: ./demo/src/app/dashboard/page.tsx
- Components:
  * Sidebar (pattern: sidebar, variant: primary)
  * Header (pattern: header, variant: primary)
  * TabNavigation (pattern: list, variant: primary)
  * Footer (pattern: footer, variant: secondary)
  * StatCard (pattern: card, variant: primary)
- Layout: dashboard
- Enable Redux: true

STEP 2 - Setup Redux:
After components are generated, use generate_redux_setup:
- Components: [] (auto-detect from generated components)
- Output dir: ./demo/src/store
- Store name: store

REQUIREMENTS:
- Sidebar should be collapsible with animations
- Header should have menu toggle button
- TabNavigation should have tabs: Overview, Analytics, Settings
- StatCard should display metrics
- Use Tailwind CSS for styling
- All components should be responsive
- Redux should manage: sidebar state, active tab, dashboard data
"""
    
    print("🚀 Creating dashboard...")
    print("=" * 80)
    
    # Execute
    result = await agent.execute(request, max_iterations=20)
    
    # Results
    print("\n" + "=" * 80)
    if result["success"]:
        print("✅ SUCCESS!")
    else:
        print("❌ FAILED!")
    
    print(f"\n📊 Stats:")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Tools used: {len(result['tool_results'])}")
    
    if result['tool_results']:
        print(f"\n🔧 Tools executed:")
        for tr in result['tool_results']:
            status = "✅" if tr.success else "❌"
            print(f"  {status} {tr.metadata.get('tool_name', 'unknown')}")
    
    print(f"\n💬 Response:")
    print(result['response'])
    
    return result


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════╗
║   🎨 DASHBOARD CREATOR                     ║
║   Simple direct function to create         ║
║   dashboard with agent core                ║
╚════════════════════════════════════════════╝
""")
    
    asyncio.run(create_dashboard())
    
    print("""
╔════════════════════════════════════════════╗
║   📋 NEXT STEPS                            ║
╚════════════════════════════════════════════╝

1. cd demo
2. npm install
3. npm install @reduxjs/toolkit react-redux
4. npm run dev
5. Open http://localhost:3000/dashboard

""")
