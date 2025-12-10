"""
Page Management Tools
Tools for managing Next.js pages, automatic imports, and file organization
"""

import pathlib
import re
import json
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from ..tool_schemas import (
    ToolResult,
    UpdatePageImportsInput,
    GeneratePageWithComponentsInput,
    OrganizeProjectFilesInput,
    CleanDemoFolderInput
)
from ..utils.path_utils import PathUtils


# ============================================================================
# Layout Templates Loader
# ============================================================================

def _load_layout_templates() -> Dict[str, Any]:
    """Load layout templates from JSON configuration"""
    config_dir = pathlib.Path(__file__).parent.parent.parent / "config"
    templates_file = config_dir / "layout_templates.json"
    
    if not templates_file.exists():
        return {"layouts": {}}  # Return empty if file doesn't exist
    
    with open(templates_file, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============================================================================
# Input Schemas - Now imported from tool_schemas.py
# ============================================================================

# Schema definitions moved to tool_schemas.py to avoid circular imports


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
    """Calculate relative path between two files - uses PathUtils"""
    # Use centralized PathUtils for consistent relative path calculation
    rel_path = PathUtils.calculate_relative_path(from_path, to_path)
    # Remove extension for imports
    rel_path = re.sub(r'\.(tsx|jsx|ts|js)$', '', rel_path)
    return rel_path


def _generate_layout(layout_type: str, components: List[Dict[str, str]], title: str, description: str) -> str:
    """Generate responsive page layout HTML based on layout type (loads from JSON)
    
    Supported layouts:
    - chat: Sidebar + Main content (header, messages, input, footer)
    - dashboard: Header + Grid of cards
    - landing: Stacked hero + sections
    - app: Sidebar + Content + Details panel
    - grid: Simple responsive grid (default)
    """
    
    # Load layouts from JSON
    templates_data = _load_layout_templates()
    layouts = templates_data.get("layouts", {})
    
    # Fallback to grid if layout not found
    if layout_type not in layouts:
        layout_type = "grid"
    
    layout_config = layouts[layout_type]
    
    # Helper to get component by name pattern
    def get_comp(pattern: str):
        for comp in components:
            if pattern.lower() in comp['name'].lower():
                return comp['tag']
        return None
    
    # Handle each layout type
    if layout_type == "chat":
        # Simple template replacement
        template = layout_config["template"]
        sidebar = get_comp('sidebar') or (components[0]['tag'] if len(components) > 0 else '')
        header = get_comp('header') or (components[1]['tag'] if len(components) > 1 else '')
        messages = get_comp('message') or get_comp('list') or (components[2]['tag'] if len(components) > 2 else '')
        input_comp = get_comp('input') or get_comp('form') or (components[3]['tag'] if len(components) > 3 else '')
        footer = get_comp('footer') or (components[4]['tag'] if len(components) > 4 else '')
        
        return template.replace('{sidebar}', sidebar).replace('{header}', header).replace('{messages}', messages).replace('{input}', input_comp).replace('{footer}', footer)
    
    elif layout_type == "dashboard":
        sidebar = get_comp('sidebar')
        header = get_comp('header')
        footer = get_comp('footer')
        tabs = get_comp('tab') or get_comp('navigation')
        
        # Collect stat cards and other components
        cards = [c['tag'] for c in components if 'card' in c['name'].lower() or 'stat' in c['name'].lower()]
        other_comps = [c['tag'] for c in components if c['tag'] not in [sidebar, header, footer, tabs] and c['tag'] not in cards]
        
        cards_html = '\n              '.join(cards) if cards else ''
        other_html = '\n            '.join(other_comps) if other_comps else ''
        
        # Build sections
        header_section = (f'<header className="bg-white border-b border-neutral-200 sticky top-0 z-10 px-4 sm:px-6 lg:px-8 py-4">\n          {header}\n        </header>') if header else ''
        cards_section = (f'<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6 mb-8">\n              {cards_html}\n            </div>') if cards else ''
        tabs_section = (f'<div className="mb-6">\n              {tabs}\n            </div>') if tabs else ''
        other_section = (f'<div className="space-y-6">\n              {other_html}\n            </div>') if other_html else ''
        footer_section = (f'<footer className="border-t border-neutral-200 bg-white px-4 sm:px-6 lg:px-8 py-4">\n          {footer}\n        </footer>') if footer else ''
        
        # Choose template based on sidebar presence
        template = layout_config["template_with_sidebar"] if sidebar else layout_config["template_no_sidebar"]
        
        return template.replace('{sidebar}', sidebar or '').replace('{header_section}', header_section).replace('{title}', title).replace('{description}', description).replace('{cards_section}', cards_section).replace('{tabs_section}', tabs_section).replace('{other_section}', other_section).replace('{footer_section}', footer_section)
    
    elif layout_type == "landing":
        template = layout_config["template"]
        section_template = layout_config["section_template"]
        
        hero = get_comp('hero') or (components[0]['tag'] if len(components) > 0 else '')
        sections = [c['tag'] for c in components[1:]] if len(components) > 1 else []
        sections_html = ''
        for i, section in enumerate(sections):
            bg_class = 'bg-white' if i % 2 == 0 else 'bg-neutral-50'
            sections_html += '\n      ' + section_template.replace('{bg_class}', bg_class).replace('{content}', section)
        
        return template.replace('{hero}', hero).replace('{sections}', sections_html)
    
    elif layout_type == "app":
        template = layout_config["template"]
        sidebar = get_comp('sidebar') or (components[0]['tag'] if len(components) > 0 else '')
        content = '\n          '.join([c['tag'] for c in components[1:] if 'detail' not in c['name'].lower()])
        details = get_comp('detail')
        details_section = (f'<aside className="w-80 xl:w-96 flex-shrink-0 border-l border-neutral-200 bg-white overflow-y-auto">\n        {details}\n      </aside>') if details else ''
        
        return template.replace('{sidebar}', sidebar).replace('{content}', content).replace('{details_section}', details_section)
    
    else:  # Default: "grid"
        template = layout_config["template"]
        all_components = '\n            '.join([c['tag'] for c in components])
        
        return template.replace('{title}', title).replace('{description}', description).replace('{components}', all_components)


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
        # Sanitize and validate path
        safe_path = PathUtils.sanitize_path(params.page_path)
        page_path = pathlib.Path(safe_path)
        
        if not PathUtils.file_exists(safe_path):
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
