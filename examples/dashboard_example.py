"""
Complex Dashboard Example with Redux State Management
Demonstrates creating a sophisticated UX dashboard with:
- Animated collapsible sidebar menu
- Tab navigation with state management
- Redux integration for UI state
- Responsive layout
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent_core import AICodeAgent


async def create_dashboard_with_redux():
    """
    Create a complete dashboard with Redux state management
    
    Features:
    1. Redux store with slices for:
       - Menu state (collapsed/expanded)
       - Active tab management
       - Dashboard data
    
    2. Animated sidebar menu with:
       - Smooth collapse/expand transitions
       - Active state indicators
       - Icon animations
       - Responsive behavior
    
    3. Tab navigation with:
       - Multiple tabs (Overview, Analytics, Settings)
       - Redux-connected active state
       - Smooth transitions
       - Content switching
    
    4. Professional UX patterns:
       - Loading states
       - Error boundaries
       - Accessibility support
       - Dark mode ready
    """
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    agent = AICodeAgent(groq_api_key=api_key)
    
    # Complex prompt with detailed requirements
    prompt = """
Create a professional admin dashboard with Redux state management and animations.

STEP 1 - REDUX STORE SETUP:
Create Redux store with the following slices:

1. uiSlice.ts - UI state management:
   - menuCollapsed: boolean (sidebar collapsed state)
   - activeTab: string (current active tab: 'overview' | 'analytics' | 'settings' | 'users')
   - theme: 'light' | 'dark'
   - Actions: toggleMenu(), setActiveTab(tab), toggleTheme()

2. dashboardSlice.ts - Dashboard data:
   - stats: { totalUsers: number, revenue: number, orders: number, growth: number }
   - recentActivity: Array<{ id: string, user: string, action: string, timestamp: string }>
   - Actions: setStats(), setRecentActivity()

3. store.ts - Configure store with all slices

STEP 2 - COMPONENTS:
Generate the following React components with TypeScript:

1. DashboardLayout.tsx - Main layout component:
   - Uses Redux to access menuCollapsed state
   - Responsive grid layout: sidebar + main content
   - Smooth transitions when menu collapses (use Tailwind transitions)
   - Props: children: ReactNode

2. Sidebar.tsx - Animated collapsible sidebar:
   - Redux connected to menuCollapsed and activeTab
   - Width: 240px (expanded), 64px (collapsed)
   - Smooth width transition (duration-300 ease-in-out)
   - Menu items with icons and labels:
     * Overview (Home icon)
     * Analytics (Chart icon)
     * Users (Users icon)
     * Settings (Settings icon)
   - Active state highlighting (primary color background)
   - On collapsed: show only icons, hide labels with fade effect
   - Toggle button at bottom to dispatch toggleMenu()
   - Use lucide-react for icons

3. TopBar.tsx - Header component:
   - Shows page title based on activeTab
   - Toggle menu button (dispatches toggleMenu())
   - Theme toggle button (dispatches toggleTheme())
   - User profile dropdown (mock)
   - Height: 64px, sticky top
   - Shadow and border bottom

4. TabNavigation.tsx - Tab switching component:
   - Redux connected to activeTab
   - Tabs: Overview, Analytics, Settings, Users
   - Dispatches setActiveTab(tab) on click
   - Active tab indicator (underline with slide animation)
   - Use Framer Motion or Tailwind for smooth transitions

5. TabContent.tsx - Dynamic content based on active tab:
   - Redux connected to activeTab and dashboardSlice data
   - Renders different content for each tab:
     * Overview: Stats cards grid (4 cards with stats data from Redux)
     * Analytics: Charts placeholder with title and description
     * Settings: Form with toggle switches and inputs
     * Users: Table with user list (mock data)
   - Use fade-in animation when switching tabs

6. StatsCard.tsx - Reusable stat card:
   - Props: title, value, change (percentage), icon
   - Shows trend indicator (up/down arrow)
   - Color coding based on positive/negative change
   - Hover effect with shadow increase

STEP 3 - PAGE:
Create dashboard page at: ./demo/src/app/dashboard/page.tsx
- Import and use DashboardLayout
- Include TopBar
- Include Sidebar
- Include TabNavigation
- Include TabContent
- Redux Provider should be in root layout

STEP 4 - STYLING REQUIREMENTS:
- Use Tailwind CSS for all styling
- Color palette:
  * Primary: blue-600
  * Sidebar bg: neutral-900 (dark), neutral-50 (light)
  * Main bg: neutral-50 (light), neutral-900 (dark)
  * Borders: neutral-200 (light), neutral-700 (dark)
- Smooth transitions: duration-300 ease-in-out
- Responsive breakpoints:
  * Mobile: menu auto-collapsed
  * Tablet (md): menu collapsible
  * Desktop (lg+): menu expanded by default

STEP 5 - ANIMATIONS:
- Menu collapse/expand: smooth width transition
- Tab switch: fade in/out content
- Active tab indicator: slide animation
- Menu item hover: background color fade
- Stats cards: hover lift effect
- Icons: subtle rotate/scale on interaction

STEP 6 - TYPESCRIPT:
- Proper TypeScript interfaces for all props
- Type-safe Redux with RootState and AppDispatch
- Strict null checks
- Export all types

Please generate ALL files:
1. Redux store setup (store/, slices/)
2. All React components (components/)
3. Dashboard page (app/dashboard/page.tsx)
4. TypeScript interfaces (types/ if needed)

Use the design system and follow best practices for:
- Component composition
- State management
- Accessibility (ARIA labels, keyboard navigation)
- Performance (React.memo where appropriate)
"""
    
    print("🚀 Starting Dashboard Generation with Redux...")
    print("=" * 80)
    print()
    
    result = await agent.execute(
        prompt,
        max_iterations=25  # Complex task needs more iterations
    )
    
    print()
    print("=" * 80)
    print("✅ Dashboard Generation Complete!")
    print()
    print("📋 Summary:")
    print(result["response"])
    print()
    print("📁 Generated Files:")
    for tool_result in result.get("tool_results", []):
        if tool_result.success and "path" in str(tool_result.output):
            print(f"  ✓ {tool_result.tool_name}: {tool_result.output.get('path', 'N/A')}")
    print()
    print("🎨 Next Steps:")
    print("  1. cd demo")
    print("  2. npm install (if not done)")
    print("  3. npm install @reduxjs/toolkit react-redux lucide-react")
    print("  4. npm run dev")
    print("  5. Open http://localhost:3000/dashboard")
    print()
    print("🎯 Features to Test:")
    print("  - Click menu toggle button to collapse/expand sidebar")
    print("  - Click tabs to switch between Overview, Analytics, Settings, Users")
    print("  - Hover over menu items and stats cards for animations")
    print("  - Resize window to see responsive behavior")
    print("  - Check Redux DevTools to see state changes")
    print()


async def create_simple_dashboard_demo():
    """
    Simplified version for quick testing
    Creates a basic dashboard without full Redux setup
    """
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    agent = AICodeAgent(groq_api_key=api_key)
    
    prompt = """
Create a simple dashboard demo page at ./demo/src/app/simple-dashboard/page.tsx

Include:
1. A collapsible sidebar (use React useState for collapsed state)
2. Tab navigation (use React useState for activeTab)
3. Main content area showing different content per tab
4. Smooth animations using Tailwind transitions

Components to generate:
- SimpleDashboard: Main component with layout and state
- SidebarMenu: Collapsible menu (width: 240px → 64px)
- TabBar: Tab navigation (Overview, Stats, Settings)
- ContentArea: Shows different content based on active tab

Use Tailwind CSS, TypeScript, and add smooth transitions.
"""
    
    print("🚀 Starting Simple Dashboard Demo...")
    print()
    
    result = await agent.execute(prompt, max_iterations=15)
    
    print()
    print("✅ Simple Dashboard Complete!")
    print(result["response"])


async def add_advanced_features():
    """
    Add advanced features to existing dashboard
    """
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    agent = AICodeAgent(groq_api_key=api_key)
    
    prompt = """
Enhance the existing dashboard at ./demo/src/app/dashboard/page.tsx with:

1. Add search bar in TopBar with:
   - Redux state for search query
   - Debounced search (useEffect + setTimeout)
   - Search results dropdown

2. Add notifications panel:
   - Bell icon in TopBar
   - Redux state for notifications array
   - Dropdown panel with notification list
   - Mark as read functionality

3. Add data refresh functionality:
   - Refresh button in each tab
   - Loading spinner during refresh
   - Success/error toast notifications

4. Add keyboard shortcuts:
   - Ctrl/Cmd + B: Toggle sidebar
   - Ctrl/Cmd + 1-4: Switch tabs
   - Escape: Close dropdowns

Please update existing files and add new Redux actions/reducers as needed.
"""
    
    print("🔧 Adding Advanced Features...")
    print()
    
    result = await agent.execute(prompt, max_iterations=20)
    
    print()
    print("✅ Advanced Features Added!")
    print(result["response"])


# ============================================================================
# Main Execution
# ============================================================================

async def main():
    """Main execution function"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║         🎨 Complex Dashboard Generator with Redux Example 🎨             ║
║                                                                          ║
║  This example demonstrates creating a professional admin dashboard      ║
║  with Redux state management, animations, and complex interactions.     ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("\nSelect an example to run:\n")
    print("1. Full Dashboard with Redux (Complex - Recommended)")
    print("2. Simple Dashboard Demo (Quick test without Redux)")
    print("3. Add Advanced Features to Existing Dashboard")
    print("4. Exit")
    print()
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        await create_dashboard_with_redux()
    elif choice == "2":
        await create_simple_dashboard_demo()
    elif choice == "3":
        await add_advanced_features()
    elif choice == "4":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice. Please run again and select 1-4.")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Error: GROQ_API_KEY environment variable not set")
        print("Please set it with: export GROQ_API_KEY='your-key-here'")
        exit(1)
    
    # Run the async main function
    asyncio.run(main())
