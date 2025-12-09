"""
Tool Usage Instructions for Agent
Provides detailed examples of how to use each tool correctly
"""

TOOL_USAGE_GUIDE = """
# Tool Usage Guide for AI Agent

## React/JavaScript Component Tools

### generate_react_component
Generate React/TypeScript components with design system patterns.

CORRECT USAGE:
{
    "tool_name": "generate_react_component",
    "parameters": {
        "component_name": "ProductCard",
        "component_pattern": "card",
        "variant": "primary",
        "styling": "tailwind",
        "output_dir": "./demo/src/components"
    }
}

Available patterns: button, card, form, modal, list, hero, feature, pricing
Available variants: primary, secondary, outline, ghost, success, warning, error

⚡ RESPONSIVE DESIGN: All components are automatically responsive with:
- Mobile-first Tailwind classes (base → sm: → md: → lg: → xl:)
- Adaptive layouts that stack on mobile, arrange side-by-side on desktop
- Responsive typography, spacing, and sizing
- Touch-friendly tap targets (min 44x44px on mobile)

### generate_page_with_components
Generate a complete page with multiple components automatically.

CORRECT USAGE:
{
    "tool_name": "generate_page_with_components",
    "parameters": {
        "page_name": "products",
        "page_path": "./demo/src/app/products/page.tsx",
        "components": [
            {
                "name": "ProductCard",
                "pattern": "card",
                "variant": "primary",
                "props_data": {"title": "Product"}
            }
        ],
        "title": "Products Page",
        "description": "Our products",
        "layout_type": "grid"
    }
}

Available layout_type values:
- "grid": Responsive grid layout (default) - cards arranged in columns
- "chat": Chat interface - sidebar + messages + input
- "dashboard": Dashboard layout - header + grid of metrics/charts
- "landing": Landing page - hero section + stacked content sections
- "app": App interface - sidebar + content + details panel

⚡ RESPONSIVE LAYOUTS: All layouts automatically adapt to screen size:
- Mobile (< 640px): Single column, stacked components
- Tablet (640-1024px): Sidebars hidden/collapsible, 2-column grids
- Desktop (1024px+): Full layout with sidebars, 3-4 column grids

### update_page_imports
Update imports in an existing page file.

CORRECT USAGE:
{
    "tool_name": "update_page_imports",
    "parameters": {
        "page_path": "./demo/src/app/page.tsx",
        "components": [
            {
                "name": "ProductCard",
                "path": "../components/ProductCard"
            }
        ],
        "replace_all": false
    }
}

## Design System Tools

### generate_design_system
Generate complete design system with Tailwind config, CSS, and docs.

CORRECT USAGE:
{
    "tool_name": "generate_design_system",
    "parameters": {
        "project_path": "./demo",
        "framework": "nextjs",
        "include_dark_mode": true,
        "include_component_patterns": true,
        "include_docs": true
    }
}

This generates:
- tailwind.config.js
- src/app/globals.css  
- DESIGN_SYSTEM.md

## Redux State Management Tools

### generate_redux_setup
Generate Redux Toolkit store with slices and mock data based on component schemas.

CORRECT USAGE:
{
    "tool_name": "generate_redux_setup",
    "parameters": {
        "components": [
            {
                "name": "ChatMessageList",
                "props": {
                    "items": "Array<{title: string; description: string}>",
                    "isLoading": "boolean"
                }
            },
            {
                "name": "ChatSidebar",
                "props": {
                    "conversations": "Array<{id: string; name: string}>",
                    "activeId": "string"
                }
            }
        ],
        "output_dir": "./demo/src/store",
        "store_name": "store"
    }
}

This generates:
- src/store/store.ts (Redux store config)
- src/store/hooks.ts (Typed useAppSelector/useAppDispatch)
- src/store/chatmessagelistSlice.ts (Slice with mock data)
- src/store/chatsidebarSlice.ts (Slice with mock data)

Features:
- Automatically generates realistic mock data based on prop types
- Creates TypeScript interfaces for state
- Sets up typed Redux hooks
- Handles arrays, objects, primitives, and complex nested types

### generate_react_component with Redux
Generate components that connect to Redux store.

CORRECT USAGE:
{
    "tool_name": "generate_react_component",
    "parameters": {
        "component_name": "ChatMessageList",
        "component_pattern": "list",
        "variant": "primary",
        "styling": "tailwind",
        "with_redux": true,
        "output_dir": "./demo/src/components"
    }
}

When with_redux=true:
- Imports useAppSelector from '../store/hooks'
- Adds useAppSelector hook to get data from store
- Component uses Redux state instead of requiring props
- Automatically connects to matching slice name

### generate_page_with_components with Redux
Generate page with components connected to Redux.

CORRECT USAGE:
{
    "tool_name": "generate_page_with_components",
    "parameters": {
        "page_name": "chat",
        "page_path": "./demo/src/app/page.tsx",
        "components": [
            {"name": "ChatSidebar", "pattern": "card", "variant": "primary"},
            {"name": "ChatMessageList", "pattern": "list", "variant": "primary"},
            {"name": "ChatInput", "pattern": "form", "variant": "primary"}
        ],
        "title": "Chat Interface",
        "description": "Real-time messaging"
    }
}

This automatically:
- Generates components with with_redux=true
- Collects component prop schemas
- Calls generate_redux_setup to create store
- Wraps page in Redux Provider
- Adds Redux Toolkit and react-redux to package.json
- Generates mock data for all component props

## File Operations Tools

### write_file
Write content to a file (creates directories automatically).

CORRECT USAGE:
{
    "tool_name": "write_file",
    "parameters": {
        "file_path": "./demo/src/app/layout.tsx",
        "content": "import React from 'react';\\n\\nexport default function Layout({ children }) {\\n  return <html><body>{children}</body></html>;\\n}",
        "create_dirs": true
    }
}

### read_file
Read file contents.

CORRECT USAGE:
{
    "tool_name": "read_file",
    "parameters": {
        "file_path": "./demo/src/app/page.tsx",
        "encoding": "utf-8"
    }
}

## File Organization Tools

### organize_project_files
Organize files by type into structured directories.

CORRECT USAGE:
{
    "tool_name": "organize_project_files",
    "parameters": {
        "source_dir": "./demo/src/components",
        "target_base_dir": "./demo/organized",
        "create_subdirs": true,
        "clean_source": false
    }
}

### clean_demo_folder
Clean demo folder keeping only essential files.

CORRECT USAGE:
{
    "tool_name": "clean_demo_folder",
    "parameters": {
        "demo_dir": "./demo",
        "keep_patterns": ["*.config.*", "package.json"],
        "archive_dir": "./archived_demos/backup_20231208"
    }
}

## Common Workflows

### Workflow 1: Create Complete Demo with Redux
1. generate_design_system (project_path: "./demo")
2. generate_page_with_components (automatically generates Redux store + components)
   - Components generated with with_redux=true
   - Redux store created with mock data
   - Page wrapped in Redux Provider

### Workflow 2: Create Demo Without Redux (Static Components)
1. generate_design_system (project_path: "./demo")
2. generate_react_component (for each component, with_redux=false)
3. generate_page_with_components (renders static components)

### Workflow 3: Add Redux to Existing Components
1. generate_redux_setup (pass existing component schemas)
2. Manually update components to use useAppSelector
3. Wrap page in Redux Provider

### Workflow 4: Add Component to Existing Page
1. generate_react_component (create new component)
2. update_page_imports (add import to page)
3. User manually adds component to JSX (or use write_file to replace content)

### Workflow 5: Organize Project
1. organize_project_files (categorize by type)
2. update_page_imports (fix import paths if needed)

## Parameter Tips

### File Paths
- Use relative paths from project root: "./demo/src/app/page.tsx"
- Not absolute paths: "/Users/username/..."

### Component Names
- Use PascalCase: "ProductCard", "HeroSection"
- Not kebab-case: "product-card"

### Output Directories
- For components: "./demo/src/components"
- For pages: "./demo/src/app"
- Always include "./" prefix for relative paths

### Styling
- Default to "tailwind" for Next.js projects
- Use "css-modules" only if specifically requested

### Patterns
- Match the UI need: "card" for cards, "hero" for hero sections, "form" for forms
- Use descriptive component names that indicate purpose

## Error Prevention

### Common Mistakes to AVOID:

❌ Wrong parameter names:
{
    "parameters": {
        "name": "Card",  // WRONG - should be "component_name"
        "pattern": "card"
    }
}

✅ Correct:
{
    "parameters": {
        "component_name": "Card",  // CORRECT
        "component_pattern": "card"
    }
}

❌ Missing required parameters:
{
    "tool_name": "generate_react_component",
    "parameters": {
        "component_name": "Card"
        // Missing output_dir!
    }
}

✅ Correct:
{
    "tool_name": "generate_react_component",
    "parameters": {
        "component_name": "Card",
        "output_dir": "./demo/src/components"
    }
}

❌ Wrong data types:
{
    "parameters": {
        "components": "ProductCard"  // WRONG - should be array
    }
}

✅ Correct:
{
    "parameters": {
        "components": [{"name": "ProductCard", "pattern": "card"}]
    }
}
"""
