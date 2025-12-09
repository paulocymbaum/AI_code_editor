"""
Page Management Tools
Tools for managing Next.js pages, automatic imports, and file organization
"""

import pathlib
import re
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from ..tool_schemas import ToolResult


# ============================================================================
# Input Schemas
# ============================================================================

class UpdatePageImportsInput(BaseModel):
    """Updates existing page file to import specified components. 
    
    Does NOT generate components - only updates imports in existing page.
    Use this to fix broken imports or add new component references."""
    page_path: str = Field(..., description="Path to the existing page file to update")
    components: List[Dict[str, str]] = Field(
        ..., 
        description="List of components with 'name' and 'path' keys. Path can be relative or absolute."
    )
    replace_all: bool = Field(
        default=False, 
        description="If True, removes all existing component imports and adds only these. If False, adds to existing imports."
    )


class GeneratePageWithComponentsInput(BaseModel):
    """Generates React components AND creates a page that imports them. All-in-one solution.
    
    This is the RECOMMENDED tool for creating new pages with components:
    1. Generates all specified components using design system patterns
    2. Creates the page file
    3. Automatically imports all components into the page
    4. Wires up components with proper props
    
    Use this instead of calling generate_react_component multiple times + update_page_imports."""
    page_name: str = Field(..., description="Name of the page (e.g., 'products', 'about')")
    page_path: str = Field(..., description="Full path where page should be created (e.g., './demo/src/app/products/page.tsx')")
    components: List[Dict[str, Any]] = Field(
        ..., 
        description="REQUIRED: Components to generate. Each dict MUST have: 'name' (string, PascalCase), 'pattern' (REQUIRED: card|button|form|modal|list|hero|feature|pricing|sidebar|header|footer|messages|input|custom), optional 'variant' (primary|secondary|outline|ghost) and 'props_data' (dict). Pattern is MANDATORY - choose based on component purpose."
    )
    title: Optional[str] = Field(default=None, description="Page title text (used in h1)")
    description: Optional[str] = Field(default=None, description="Page description text (used in subtitle)")
    layout_type: Optional[str] = Field(
        default="grid",
        description="Page layout type: 'grid' (responsive grid), 'chat' (sidebar + main area), 'dashboard' (header + grid), 'landing' (stacked sections), 'app' (sidebar + content + details)"
    )


class OrganizeProjectFilesInput(BaseModel):
    """Moves or copies files from source to target directory, organized by file type.
    
    WARNING: This tool physically moves files. Use with caution!
    - Target directory cannot be inside source (prevents infinite loops)
    - If clean_source=True, original files are DELETED after moving
    - Creates subdirectories like 'components/', 'styles/', 'types/', etc.
    
    Use cases: Reorganizing messy project structure, archiving old files"""
    source_dir: str = Field(..., description="Source directory containing files to organize")
    target_base_dir: str = Field(..., description="Target directory where organized files will be placed. MUST be outside source_dir.")
    create_subdirs: bool = Field(
        default=True, 
        description="If True, creates subdirectories (components/, styles/, etc). If False, all files go to target_base_dir root."
    )
    clean_source: bool = Field(
        default=False, 
        description="DANGER: If True, deletes original files from source after moving. Use False to copy instead."
    )


class CleanDemoFolderInput(BaseModel):
    """Archives or deletes files in demo folder except those matching keep patterns.
    
    WARNING: This tool deletes files! ALWAYS use archive_dir to create backups.
    - Keeps files matching patterns in keep_patterns
    - Archives removed files to archive_dir (if provided)
    - If archive_dir is None, files are permanently deleted
    - Will NOT clean system directories (/, ~/Documents, etc)
    
    Use case: Cleaning up test/demo components while keeping essential config files"""
    demo_dir: str = Field(default="./demo", description="Demo directory path to clean")
    keep_patterns: List[str] = Field(
        default=["*.config.*", "package.json", "tsconfig.json"],
        description="Glob patterns for files to keep (e.g., '*.config.*', 'layout.tsx')"
    )
    archive_dir: Optional[str] = Field(
        default=None, 
        description="RECOMMENDED: Directory to archive removed files. If None, files are permanently deleted!"
    )


# ============================================================================
# Helper Functions
# ============================================================================

def _extract_imports(content: str) -> List[Dict[str, str]]:
    """Extract import statements from file content"""
    imports = []
    # Match: import ComponentName from 'path'
    # Match: import { ComponentName } from 'path'
    import_pattern = r"import\s+(?:{?\s*(\w+)\s*}?|(\w+))\s+from\s+['\"]([^'\"]+)['\"]"
    
    for match in re.finditer(import_pattern, content):
        component_name = match.group(1) or match.group(2)
        import_path = match.group(3)
        imports.append({
            "name": component_name,
            "path": import_path,
            "full_line": match.group(0)
        })
    
    return imports


def _generate_import_statement(component_name: str, component_path: str) -> str:
    """Generate import statement"""
    # Remove file extension if present
    clean_path = component_path.replace('.tsx', '').replace('.jsx', '').replace('.ts', '').replace('.js', '')
    return f"import {component_name} from '{clean_path}';"


def _calculate_relative_path(from_path: str, to_path: str) -> str:
    """Calculate relative path between two files"""
    from_file = pathlib.Path(from_path).resolve()
    to_file = pathlib.Path(to_path).resolve()
    
    # Get directory of from_file
    from_dir = from_file.parent
    
    # Calculate relative path
    try:
        relative = pathlib.Path(to_file).relative_to(from_dir)
        # Convert to string with forward slashes and add ./
        rel_str = str(relative).replace('\\', '/')
        if not rel_str.startswith('.'):
            rel_str = './' + rel_str
        # Remove extension
        rel_str = re.sub(r'\.(tsx|jsx|ts|js)$', '', rel_str)
        return rel_str
    except ValueError:
        # Files are on different drives or can't be made relative
        # Use absolute path from project root
        return str(to_file).replace('\\', '/')


def _generate_layout(layout_type: str, components: List[Dict[str, str]], title: str, description: str) -> str:
    """Generate responsive page layout HTML based on layout type
    
    Supported layouts:
    - chat: Sidebar + Main content (header, messages, input, footer)
    - dashboard: Header + Grid of cards
    - landing: Stacked hero + sections
    - app: Sidebar + Content + Details panel
    - grid: Simple responsive grid (default)
    """
    
    # Helper to get component by name pattern
    def get_comp(pattern: str):
        for comp in components:
            if pattern.lower() in comp['name'].lower():
                return comp['tag']
        return None
    
    if layout_type == "chat":
        # Chat layout: Sidebar + Main content area
        sidebar = get_comp('sidebar') or (components[0]['tag'] if len(components) > 0 else '')
        header = get_comp('header') or (components[1]['tag'] if len(components) > 1 else '')
        messages = get_comp('message') or get_comp('list') or (components[2]['tag'] if len(components) > 2 else '')
        input_comp = get_comp('input') or get_comp('form') or (components[3]['tag'] if len(components) > 3 else '')
        footer = get_comp('footer') or (components[4]['tag'] if len(components) > 4 else '')
        
        return f'''<div className="flex h-screen bg-neutral-50">
      {{/* Sidebar - Hidden on mobile, visible on md+ */}}
      <aside className="hidden md:flex md:w-64 lg:w-80 flex-col border-r border-neutral-200 bg-white">
        {sidebar}
      </aside>
      
      {{/* Main Content */}}
      <main className="flex-1 flex flex-col overflow-hidden">
        {{/* Header */}}
        <header className="border-b border-neutral-200 bg-white p-4">
          {header}
        </header>
        
        {{/* Messages Area - Scrollable */}}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
          {messages}
        </div>
        
        {{/* Input Area */}}
        <div className="border-t border-neutral-200 bg-white p-4">
          {input_comp}
        </div>
        
        {{/* Footer */}}
        <footer className="border-t border-neutral-200 bg-neutral-50 p-2 sm:p-3">
          {footer}
        </footer>
      </main>
    </div>'''
    
    elif layout_type == "dashboard":
        # Dashboard layout: Header + Grid
        header = get_comp('header') or (components[0]['tag'] if len(components) > 0 else '')
        remaining = [c['tag'] for c in components[1:]] if len(components) > 1 else []
        remaining_html = '\n            '.join(remaining)
        
        return f'''<div className="min-h-screen bg-neutral-50">
      <header className="bg-white border-b border-neutral-200 sticky top-0 z-10">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4">
          {header}
        </div>
      </header>
      
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 lg:py-12">
        <div className="mb-8 sm:mb-12">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-neutral-900 mb-2 sm:mb-3">
            {title}
          </h1>
          <p className="text-base sm:text-lg text-neutral-600">
            {description}
          </p>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
            {remaining_html}
        </div>
      </main>
    </div>'''
    
    elif layout_type == "landing":
        # Landing page: Stacked sections
        hero = get_comp('hero') or (components[0]['tag'] if len(components) > 0 else '')
        sections = [c['tag'] for c in components[1:]] if len(components) > 1 else []
        sections_html = ''
        for i, section in enumerate(sections):
            bg_class = 'bg-white' if i % 2 == 0 else 'bg-neutral-50'
            sections_html += f'''
      <section className="{bg_class} py-12 sm:py-16 lg:py-24">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          {section}
        </div>
      </section>'''
        
        return f'''<div className="min-h-screen">
      <section className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          {hero}
        </div>
      </section>
      {sections_html}
    </div>'''
    
    else:  # Default: "grid"
        # Simple responsive grid layout
        all_components = '\n            '.join([c['tag'] for c in components])
        
        return f'''<div className="min-h-screen bg-neutral-50 py-6 sm:py-8 lg:py-12">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8 sm:mb-12">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-neutral-900 mb-2 sm:mb-3">
            {title}
          </h1>
          <p className="text-base sm:text-lg text-neutral-600">
            {description}
          </p>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            {all_components}
        </div>
      </div>
    </div>'''


def _ensure_nextjs_project_files(project_root: pathlib.Path) -> List[str]:
    """Create essential Next.js project files if they don't exist"""
    created_files = []
    
    # package.json
    package_json = project_root / "package.json"
    if not package_json.exists():
        package_content = '''{
  "name": "ai-agent-demo",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "next": "14.2.33",
    "@reduxjs/toolkit": "^2.0.1",
    "react-redux": "^9.0.4"
  },
  "devDependencies": {
    "typescript": "^5.6.3",
    "@types/node": "^22.10.1",
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "tailwindcss": "^3.4.15",
    "postcss": "^8.4.49",
    "autoprefixer": "^10.4.20"
  }
}
'''
        package_json.write_text(package_content, encoding='utf-8')
        created_files.append(str(package_json))
    
    # tsconfig.json
    tsconfig = project_root / "tsconfig.json"
    if not tsconfig.exists():
        tsconfig_content = '''{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
'''
        tsconfig.write_text(tsconfig_content, encoding='utf-8')
        created_files.append(str(tsconfig))
    
    # next.config.js
    next_config = project_root / "next.config.js"
    if not next_config.exists():
        next_config_content = '''/** @type {import('next').NextConfig} */
const nextConfig = {}

module.exports = nextConfig
'''
        next_config.write_text(next_config_content, encoding='utf-8')
        created_files.append(str(next_config))
    
    # postcss.config.js
    postcss_config = project_root / "postcss.config.js"
    if not postcss_config.exists():
        postcss_content = '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
'''
        postcss_config.write_text(postcss_content, encoding='utf-8')
        created_files.append(str(postcss_config))
    
    # next-env.d.ts
    next_env = project_root / "next-env.d.ts"
    if not next_env.exists():
        next_env_content = '''/// <reference types="next" />
/// <reference types="next/image-types/global" />

// NOTE: This file should not be edited
// see https://nextjs.org/docs/app/building-your-application/configuring/typescript for more information.
'''
        next_env.write_text(next_env_content, encoding='utf-8')
        created_files.append(str(next_env))
    
    return created_files


# ============================================================================
# Tool Implementations
# ============================================================================

async def update_page_imports(params: UpdatePageImportsInput) -> ToolResult:
    """Update imports in a page file"""
    try:
        page_path = pathlib.Path(params.page_path)
        
        if not page_path.exists():
            return ToolResult(
                success=False, 
                error=f"Page file not found: {params.page_path}"
            )
        
        # Read current content
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract existing imports
        existing_imports = _extract_imports(content)
        
        if params.replace_all:
            # Remove all component imports
            for imp in existing_imports:
                content = content.replace(imp['full_line'], '')
        
        # Generate new import statements
        new_imports = []
        for component in params.components:
            # Calculate relative path if component path is absolute
            component_path = component['path']
            if pathlib.Path(component_path).is_absolute():
                component_path = _calculate_relative_path(params.page_path, component_path)
            
            import_statement = _generate_import_statement(
                component['name'], 
                component_path
            )
            
            # Check if import already exists
            if not any(imp['name'] == component['name'] for imp in existing_imports):
                new_imports.append(import_statement)
        
        # Find the position to insert imports (after 'use client' or at top)
        lines = content.split('\n')
        insert_position = 0
        
        for i, line in enumerate(lines):
            if line.strip().startswith("'use client'") or line.strip().startswith('"use client"'):
                insert_position = i + 1
                break
            elif line.strip().startswith('import '):
                insert_position = i
                break
        
        # Insert new imports
        if new_imports:
            import_block = '\n'.join(new_imports) + '\n'
            lines.insert(insert_position, import_block)
            content = '\n'.join(lines)
        
        # Clean up multiple blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Write updated content
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return ToolResult(
            success=True,
            data={
                "page_path": str(page_path),
                "imports_added": len(new_imports),
                "new_imports": new_imports
            }
        )
    
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def generate_page_with_components(params: GeneratePageWithComponentsInput) -> ToolResult:
    """Generate a complete page with component imports and usage"""
    try:
        from .javascript_tools import generate_react_component, GenerateReactComponentInput
        
        page_path = pathlib.Path(params.page_path)
        page_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure Next.js project files exist (package.json, tsconfig.json, etc.)
        project_root = page_path
        while project_root.parent != project_root:
            if (project_root / "src").exists() or project_root.name == "demo":
                break
            project_root = project_root.parent
        
        created_project_files = _ensure_nextjs_project_files(project_root)
        if created_project_files:
            print(f"📦 Created missing project files: {created_project_files}")
        
        # Determine components directory
        components_dir = page_path.parent.parent / 'components'
        components_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate components (only if they don't exist)
        generated_components = []
        component_schemas = []  # Collect schemas for Redux setup
        
        for comp_spec in params.components:
            comp_name = comp_spec['name']
            comp_file_path = components_dir / f"{comp_name}.tsx"
            
            # Check if component already exists
            if comp_file_path.exists():
                print(f"♻️  Using existing component: {comp_name}")
                generated_components.append({
                    "name": comp_name,
                    "path": str(comp_file_path),
                    "props_data": comp_spec.get('props_data')
                })
                # TODO: Extract schemas from existing components
            else:
                # Generate new component with Redux integration
                print(f"🔧 Generating new component: {comp_name}")
                
                # REQUIRE pattern - no default fallback
                if 'pattern' not in comp_spec:
                    return ToolResult(
                        success=False,
                        error=f"Component '{comp_name}' missing REQUIRED 'pattern' field. Must specify one of: card, button, form, modal, list, hero, feature, pricing, sidebar, header, footer, messages, input, custom"
                    )
                
                comp_params = GenerateReactComponentInput(
                    component_name=comp_name,
                    component_pattern=comp_spec['pattern'],  # No fallback - must be provided
                    variant=comp_spec.get('variant', 'primary'),
                    styling='tailwind',
                    with_redux=True,  # Enable Redux integration
                    output_dir=str(components_dir)
                )
                
                result = await generate_react_component(comp_params)
                if result.success and result.data:
                    generated_components.append({
                        "name": comp_name,
                        "path": result.data['component_file'],
                        "props_data": comp_spec.get('props_data'),
                        "prop_schemas": result.data.get('prop_schemas', {})
                    })
                    
                    # Collect schema for Redux setup
                    if result.data.get('prop_schemas'):
                        from .redux_tools import ComponentSchema
                        component_schemas.append(ComponentSchema(
                            name=comp_name,
                            props=result.data['prop_schemas']
                        ))
        
        # Generate Redux store if components have props
        use_redux = len(component_schemas) > 0
        store_dir = page_path.parent.parent / 'store'
        
        if use_redux:
            from .redux_tools import generate_redux_setup, GenerateReduxSetupInput
            
            redux_params = GenerateReduxSetupInput(
                components=component_schemas,
                output_dir=str(store_dir),
                store_name="store"
            )
            
            redux_result = await generate_redux_setup(redux_params)
            if redux_result.success:
                print(f"✅ Generated Redux store with {len(component_schemas)} slices")
            else:
                print(f"⚠️  Failed to generate Redux store: {redux_result.error}")
                use_redux = False
        
        # Build page content
        title = params.title or params.page_name.replace('-', ' ').title()
        description = params.description or f"A page showcasing {params.page_name}"
        
        # Generate imports
        imports = ["'use client';", "", "import React from 'react';"]
        
        # Add Redux Provider import if using Redux
        if use_redux:
            imports.append("import { Provider } from 'react-redux';")
            store_file_path = str(store_dir / "store")
            rel_store_path = _calculate_relative_path(str(page_path), store_file_path)
            imports.append(f"import {{ store }} from '{rel_store_path}';")
        
        for comp in generated_components:
            rel_path = _calculate_relative_path(str(page_path), comp['path'])
            imports.append(_generate_import_statement(comp['name'], rel_path))
        
        # Generate component usage dict for smart layout
        components_with_props = []
        for comp in generated_components:
            props_str = ""
            if comp['props_data']:
                props_parts = []
                for key, value in comp['props_data'].items():
                    if isinstance(value, str):
                        props_parts.append(f'{key}="{value}"')
                    elif isinstance(value, bool):
                        props_parts.append(f'{key}={{{str(value).lower()}}}')
                    else:
                        props_parts.append(f'{key}={{{value}}}')
                props_str = " " + " ".join(props_parts)
            
            components_with_props.append({
                'name': comp['name'],
                'props_str': props_str,
                'tag': f"<{comp['name']}{props_str} />"
            })
        
        # Generate layout based on layout_type
        layout_type = params.layout_type or "grid"
        layout_html = _generate_layout(layout_type, components_with_props, title, description)
        
        # Build page code
        page_code = '\n'.join(imports) + '\n\n'
        page_code += f"const {params.page_name.replace('-', '').title()}Page = () => {{\n"
        page_code += "  return (\n"
        
        # Wrap in Redux Provider if using Redux
        if use_redux:
            page_code += "    <Provider store={store}>\n"
            # Add proper indentation to layout HTML
            for line in layout_html.split('\n'):
                if line.strip():
                    page_code += f"      {line}\n"
                else:
                    page_code += "\n"
            page_code += "    </Provider>\n"
        else:
            # Add layout HTML directly
            for line in layout_html.split('\n'):
                if line.strip():
                    page_code += f"    {line}\n"
                else:
                    page_code += "\n"
        
        page_code += '  );\n'
        page_code += '};\n\n'
        page_code += f"export default {params.page_name.replace('-', '').title()}Page;\n"
        
        # Write page file
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(page_code)
        
        return ToolResult(
            success=True,
            data={
                "page_path": str(page_path),
                "components_generated": len(generated_components),
                "components": [c['name'] for c in generated_components],
                "redux_enabled": use_redux,
                "redux_slices": len(component_schemas) if use_redux else 0
            }
        )
    
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def organize_project_files(params: OrganizeProjectFilesInput) -> ToolResult:
    """Organize project files into structured directories
    
    WARNING: This tool moves files. Use with caution.
    - Validates paths to prevent infinite loops
    - Will not allow target inside source directory
    - Archives can be lost if clean_source=True without backup
    """
    try:
        import shutil
        
        source_dir = pathlib.Path(params.source_dir).resolve()
        target_base = pathlib.Path(params.target_base_dir).resolve()
        
        # Safety validations
        if not source_dir.exists():
            return ToolResult(
                success=False, 
                error=f"Source directory not found: {params.source_dir}"
            )
        
        if target_base == source_dir:
            return ToolResult(
                success=False,
                error="Source and target directories cannot be the same"
            )
        
        # Prevent target inside source (would create infinite loop)
        try:
            target_base.relative_to(source_dir)
            return ToolResult(
                success=False,
                error="Target directory cannot be inside source directory (would create infinite loop)"
            )
        except ValueError:
            # target is NOT relative to source - this is good
            pass
        
        # Prevent source inside target with clean_source (dangerous)
        if params.clean_source:
            try:
                source_dir.relative_to(target_base)
                return ToolResult(
                    success=False,
                    error="Source directory cannot be inside target when clean_source=True"
                )
            except ValueError:
                # source is NOT relative to target - this is good
                pass
        
        target_base.mkdir(parents=True, exist_ok=True)
        
        # Define file categorization
        categories = {
            'components': ['.tsx', '.jsx'],
            'styles': ['.css', '.scss', '.sass', '.less'],
            'types': ['.d.ts', '.types.ts'],
            'utils': ['.util.ts', '.helper.ts', '.utils.ts'],
            'tests': ['.test.tsx', '.test.ts', '.spec.tsx', '.spec.ts'],
            'config': ['.config.js', '.config.ts', '.json'],
        }
        
        moved_files = []
        
        # Process files
        for file_path in source_dir.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Determine category
            category = 'other'
            for cat, extensions in categories.items():
                if any(str(file_path).endswith(ext) for ext in extensions):
                    category = cat
                    break
            
            # Create target directory
            if params.create_subdirs:
                target_dir = target_base / category
            else:
                target_dir = target_base
            
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Move or copy file
            target_file = target_dir / file_path.name
            
            # Handle duplicates
            counter = 1
            original_stem = target_file.stem
            while target_file.exists():
                target_file = target_dir / f"{original_stem}_{counter}{target_file.suffix}"
                counter += 1
            
            if params.clean_source:
                shutil.move(str(file_path), str(target_file))
            else:
                shutil.copy2(str(file_path), str(target_file))
            
            moved_files.append({
                "original": str(file_path),
                "new_location": str(target_file),
                "category": category
            })
        
        return ToolResult(
            success=True,
            data={
                "files_moved": len(moved_files),
                "target_directory": str(target_base),
                "files": moved_files
            }
        )
    
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def clean_demo_folder(params: CleanDemoFolderInput) -> ToolResult:
    """Clean demo folder, keeping only essential files
    
    WARNING: This tool deletes files. Use archive_dir to create backups.
    - Validates directory is safe to clean
    - Will not clean system directories or root paths
    - Keeps files matching keep_patterns
    """
    try:
        import shutil
        import fnmatch
        
        demo_dir = pathlib.Path(params.demo_dir).resolve()
        
        if not demo_dir.exists():
            return ToolResult(
                success=False, 
                error=f"Demo directory not found: {params.demo_dir}"
            )
        
        # Safety check: prevent cleaning dangerous directories
        dangerous_paths = [
            pathlib.Path.home(),
            pathlib.Path('/'),
            pathlib.Path.home() / 'Documents',
            pathlib.Path.home() / 'Desktop',
        ]
        
        for dangerous in dangerous_paths:
            if demo_dir == dangerous:
                return ToolResult(
                    success=False,
                    error=f"Refusing to clean system directory: {demo_dir}"
                )
            # Check if demo_dir is too close to a dangerous path (less than 4 levels deep)
            try:
                rel_path = demo_dir.relative_to(dangerous)
                if len(rel_path.parts) < 2:
                    return ToolResult(
                        success=False,
                        error=f"Directory too close to system directory: {demo_dir}"
                    )
            except ValueError:
                # Not relative to this dangerous path - continue checking others
                pass
        
        # Create archive directory if specified
        archive_dir = None
        if params.archive_dir:
            archive_dir = pathlib.Path(params.archive_dir)
            archive_dir.mkdir(parents=True, exist_ok=True)
        
        removed_files = []
        kept_files = []
        
        # Process files in components directory
        components_dir = demo_dir / 'src' / 'components'
        if components_dir.exists():
            for file_path in components_dir.iterdir():
                if not file_path.is_file():
                    continue
                
                # Check if file should be kept
                should_keep = any(
                    fnmatch.fnmatch(file_path.name, pattern) 
                    for pattern in params.keep_patterns
                )
                
                if should_keep:
                    kept_files.append(str(file_path))
                else:
                    if params.archive_dir and archive_dir:
                        # Move to archive
                        archive_file = archive_dir / 'components' / file_path.name
                        archive_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(file_path), str(archive_file))
                        removed_files.append({
                            "file": str(file_path),
                            "archived_to": str(archive_file)
                        })
                    else:
                        # Delete
                        file_path.unlink()
                        removed_files.append({
                            "file": str(file_path),
                            "archived_to": None
                        })
        
        # Clean pages directory (keep only essential pages)
        pages_dir = demo_dir / 'src' / 'app'
        essential_pages = ['page.tsx', 'layout.tsx', 'globals.css']
        
        if pages_dir.exists():
            for item in pages_dir.rglob('*'):
                if not item.is_file():
                    continue
                
                # Check if it's an essential file
                if item.name in essential_pages:
                    kept_files.append(str(item))
                    continue
                
                # Check against keep patterns
                should_keep = any(
                    fnmatch.fnmatch(item.name, pattern) 
                    for pattern in params.keep_patterns
                )
                
                if not should_keep:
                    if params.archive_dir and archive_dir:
                        # Preserve directory structure in archive
                        rel_path = item.relative_to(demo_dir)
                        archive_file = archive_dir / rel_path
                        archive_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(item), str(archive_file))
                        removed_files.append({
                            "file": str(item),
                            "archived_to": str(archive_file)
                        })
                    else:
                        item.unlink()
                        removed_files.append({
                            "file": str(item),
                            "archived_to": None
                        })
        
        return ToolResult(
            success=True,
            data={
                "files_removed": len(removed_files),
                "files_kept": len(kept_files),
                "archive_directory": params.archive_dir,
                "removed": removed_files
            }
        )
    
    except Exception as e:
        return ToolResult(success=False, error=str(e))
