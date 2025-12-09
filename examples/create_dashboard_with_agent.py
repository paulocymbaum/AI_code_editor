#!/usr/bin/env python3
"""
Create a Complex UX Dashboard using the AI Agent
This demonstrates how to properly use the agent with natural language prompts
"""

import asyncio
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent_core import AICodeAgent


async def create_complex_dashboard():
    """
    Use the AI agent to create a complex dashboard with:
    - Animated collapsible sidebar menu
    - Tab navigation
    - Redux state management
    - Professional UX patterns
    """
    logger = logging.getLogger(__name__)
    start_time = datetime.now()
    
    logger.info("="*80)
    logger.info("🤖 STARTING COMPLEX DASHBOARD CREATION")
    logger.info("="*80)
    
    # Get API key
    logger.info("🔑 Checking for GROQ_API_KEY...")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("❌ Error: GROQ_API_KEY environment variable not set")
        print("Please set it in your .env file or export it:")
        print("  export GROQ_API_KEY='your-api-key-here'")
        return
    logger.info("✅ API key found")
    
    # Initialize agent
    logger.info("🤖 Initializing AI Agent...")
    print("\n" + "="*80)
    print("🤖 AI AGENT - COMPLEX DASHBOARD CREATION")
    print("="*80)
    
    try:
        agent = AICodeAgent(groq_api_key=api_key)
        logger.info("✅ Agent initialized successfully")
        logger.info(f"📚 Loaded {len(agent.tool_registry)} tools")
        logger.info(f"📖 Tool dictionary version: {agent.tool_dictionary.get('metadata', {}).get('version', 'unknown')}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent: {e}")
        return
    
    # The natural language prompt for the agent
    user_request = """
Create a complex professional dashboard application with the following features:

1. SIDEBAR MENU with animations:
   - Collapsible/expandable sidebar navigation
   - Smooth animations for collapse/expand transitions
   - Active menu item highlighting
   - Icons with hover effects
   - Responsive behavior (auto-collapse on mobile)
   - Menu items: Dashboard, Analytics, Reports, Settings, Profile

2. TAB NAVIGATION:
   - Tab bar with 4 tabs: Overview, Analytics, Data, Settings
   - Active tab indicator with smooth transitions
   - Tab content switching
   - Responsive tab layout

3. REDUX STATE MANAGEMENT:
   - Redux store setup with slices for:
     * UI state (sidebar collapsed/expanded, active tab)
     * Dashboard data
     * User preferences
   - Actions and reducers for:
     * toggleSidebar()
     * setActiveTab(tabId)
     * updateDashboardData()
   - Redux Provider setup

4. DASHBOARD CONTENT:
   - Header with title and user menu
   - Main content area that changes based on active tab
   - Footer with info
   - Stat cards showing metrics
   - Data visualization components (charts, graphs)
   - Loading states and error handling

5. PROFESSIONAL UX:
   - Smooth transitions and animations
   - Consistent color scheme and spacing
   - Responsive design (mobile, tablet, desktop)
   - Accessibility features
   - Dark mode ready design
   - Professional typography and shadows

Please create:
- Redux store configuration file
- Redux slices for UI state and data
- Sidebar component with collapse/expand logic
- Tab navigation component
- Main dashboard page that integrates everything
- Individual tab content components
- Utility components (Header, Footer, StatCard)

Use modern React patterns with TypeScript, Tailwind CSS for styling, and proper Redux Toolkit patterns.
Save all files in the ./demo directory.
"""
    
    # Execute the request
    logger.info("📤 Sending request to agent...")
    logger.info(f"📏 Request length: {len(user_request)} characters")
    print(f"\n📋 REQUEST:\n{user_request}\n")
    
    try:
        logger.info("🚀 Starting agent execution...")
        result = await agent.execute(user_request, max_iterations=15)
        logger.info("✅ Agent execution completed")
    except Exception as e:
        logger.error(f"❌ Agent execution failed with exception: {e}", exc_info=True)
        return
    
    execution_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"⏱️  Total execution time: {execution_time:.2f} seconds")
    
    # Display results
    print("\n" + "="*80)
    print("📊 EXECUTION RESULTS")
    print("="*80)
    
    if result["success"]:
        print(f"✅ SUCCESS!")
    else:
        print(f"❌ FAILED")
    
    print(f"\n📈 Statistics:")
    print(f"   - Iterations: {result['iterations']}")
    print(f"   - Tools Used: {len(result['tool_results'])}")
    print(f"   - Errors: {len(result['errors'])}")
    
    if result['tool_results']:
        print(f"\n🔧 Tools Executed:")
        logger.info(f"🔧 {len(result['tool_results'])} tools executed")
        for i, tool_result in enumerate(result['tool_results'], 1):
            status = "✅" if tool_result['success'] else "❌"
            tool_name = tool_result.get('tool_name', 'unknown')
            print(f"   {i}. {status} {tool_name}")
            logger.info(f"  Tool {i}: {status} {tool_name}")
            
            if not tool_result['success'] and tool_result.get('error'):
                error_msg = tool_result['error']
                print(f"      Error: {error_msg}")
                logger.error(f"    Error: {error_msg}")
            elif tool_result['success'] and tool_result.get('data'):
                data = tool_result['data']
                if isinstance(data, dict):
                    logger.debug(f"    Data keys: {list(data.keys())}")
    
    if result['errors']:
        print(f"\n❌ Errors Encountered:")
        logger.warning(f"⚠️  {len(result['errors'])} errors encountered")
        for i, error in enumerate(result['errors'], 1):
            print(f"   {i}. {error}")
            logger.error(f"  Error {i}: {error}")
    
    print(f"\n💬 Agent Response:")
    print(f"{result['response']}")
    
    # Check generated files
    logger.info("📁 Checking for generated files...")
    demo_dir = Path("./demo")
    file_count = 0
    total_size = 0
    files_by_type = {}
    
    if demo_dir.exists():
        print(f"\n📁 Generated Files:")
        
        for file_path in sorted(demo_dir.rglob("*")):
            if file_path.is_file():
                rel_path = file_path.relative_to(demo_dir)
                size = file_path.stat().st_size
                ext = file_path.suffix
                
                print(f"   - {rel_path} ({size:,} bytes)")
                
                file_count += 1
                total_size += size
                files_by_type[ext] = files_by_type.get(ext, 0) + 1
        
        logger.info(f"📊 Generated {file_count} files, total size: {total_size:,} bytes")
        logger.info(f"📝 Files by type: {files_by_type}")
    else:
        logger.warning("⚠️  Demo directory not found!")
    
    # Save execution report
    report_path = Path("dashboard_creation_report.json")
    logger.info(f"💾 Saving execution report to {report_path}...")
    try:
        # Add metadata to report
        result['metadata'] = {
            'execution_time_seconds': execution_time,
            'timestamp': datetime.now().isoformat(),
            'files_generated': file_count,
            'total_size_bytes': total_size
        }
        
        with open(report_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        logger.info(f"✅ Report saved successfully")
        print(f"\n📄 Full report saved to: {report_path}")
    except Exception as e:
        logger.error(f"❌ Failed to save report: {e}")
    
    print("\n" + "="*80)
    print("✨ Dashboard creation complete!")
    print("="*80)
    logger.info("="*80)
    logger.info("✨ DASHBOARD CREATION COMPLETE")
    logger.info(f"⏱️  Total time: {execution_time:.2f}s | Files: {file_count} | Success: {result['success']}")
    logger.info("="*80)
    

async def create_simple_test():
    """Simple test to verify agent is working"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    print("\n🧪 Running simple test...")
    agent = AICodeAgent(groq_api_key=api_key)
    
    result = await agent.execute(
        "Create a simple React button component called TestButton in ./demo/TestButton.tsx",
        max_iterations=3
    )
    
    print(f"\n✅ Test result: {'SUCCESS' if result['success'] else 'FAILED'}")
    print(f"Response: {result['response']}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create dashboard using AI agent")
    parser.add_argument("--test", action="store_true", help="Run simple test first")
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(create_simple_test())
    else:
        asyncio.run(create_complex_dashboard())
