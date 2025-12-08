"""
JavaScript/TypeScript/React Tools
Specialized tools for JS/TS code generation and analysis
"""

import subprocess
import json
import pathlib
from typing import Optional, List, Dict, Any
from ..tool_schemas import ToolResult
from pydantic import BaseModel, Field


# ============================================================================
# Input Schemas for JS/TS Tools
# ============================================================================

class GenerateReactComponentInput(BaseModel):
    """Input for generating React components"""
    component_name: str = Field(..., description="Name of the component (PascalCase)")
    component_type: str = Field(default="functional", description="functional or class")
    use_typescript: bool = Field(default=True, description="Generate TypeScript")
    props: Optional[List[Dict[str, str]]] = Field(default=None, description="Component props")
    hooks: Optional[List[str]] = Field(default=None, description="React hooks to use")
    styling: str = Field(default="css-modules", description="css-modules, styled-components, tailwind")
    output_dir: str = Field(default="./src/components", description="Output directory")


class GenerateNextJSPageInput(BaseModel):
    """Input for generating Next.js pages"""
    page_name: str = Field(..., description="Page name (kebab-case)")
    route: str = Field(..., description="Route path (e.g., /about, /blog/[slug])")
    use_typescript: bool = Field(default=True, description="Generate TypeScript")
    data_fetching: Optional[str] = Field(default=None, description="SSR, SSG, ISR, or CSR")
    layout: Optional[str] = Field(default=None, description="Layout to use")
    output_dir: str = Field(default="./src/app", description="Output directory")


class GenerateAPIRouteInput(BaseModel):
    """Input for generating API routes"""
    route_name: str = Field(..., description="API route name")
    method: str = Field(default="GET", description="HTTP method")
    use_typescript: bool = Field(default=True, description="Generate TypeScript")
    framework: str = Field(default="nextjs", description="nextjs, express, fastify")
    output_dir: str = Field(default="./src/app/api", description="Output directory")


class TypeScriptCheckInput(BaseModel):
    """Input for TypeScript type checking"""
    file_path: Optional[str] = Field(default=None, description="Specific file to check")
    project_root: str = Field(default=".", description="Project root directory")
    strict: bool = Field(default=True, description="Use strict mode")


class ESLintCheckInput(BaseModel):
    """Input for ESLint checking"""
    file_path: Optional[str] = Field(default=None, description="Specific file to check")
    fix: bool = Field(default=False, description="Auto-fix issues")
    project_root: str = Field(default=".", description="Project root directory")


class PrettierFormatInput(BaseModel):
    """Input for Prettier formatting"""
    file_path: str = Field(..., description="File to format")
    write: bool = Field(default=True, description="Write changes to file")


class NPMCommandInput(BaseModel):
    """Input for NPM commands"""
    command: str = Field(..., description="NPM command (install, run, test, etc.)")
    args: Optional[List[str]] = Field(default=None, description="Additional arguments")
    working_dir: str = Field(default=".", description="Working directory")


class GenerateTypeDefinitionsInput(BaseModel):
    """Input for generating TypeScript type definitions"""
    source: str = Field(..., description="Source (API response, JSON, etc.)")
    type_name: str = Field(..., description="Name for the type/interface")
    output_file: str = Field(..., description="Output file path")


# ============================================================================
# Tool Implementations
# ============================================================================

async def generate_react_component(params: GenerateReactComponentInput) -> ToolResult:
    """Generate a React component"""
    try:
        # Determine file extension
        ext = "tsx" if params.use_typescript else "jsx"
        
        # Build props interface (TypeScript)
        props_interface = ""
        if params.use_typescript and params.props:
            props_interface = f"interface {params.component_name}Props {{\n"
            for prop in params.props:
                props_interface += f"  {prop['name']}: {prop['type']};\n"
            props_interface += "}\n\n"
        
        # Build imports
        imports = ["import React"]
        if params.hooks:
            hooks_str = ", ".join(params.hooks)
            imports[0] = f"import React, {{ {hooks_str} }}"
        
        # Add styling imports
        if params.styling == "css-modules":
            imports.append(f"import styles from './{params.component_name}.module.css'")
        elif params.styling == "styled-components":
            imports.append("import styled from 'styled-components'")
        
        imports_str = ";\n".join(imports) + ";\n\n"
        
        # Build component
        if params.component_type == "functional":
            props_param = f"props: {params.component_name}Props" if params.use_typescript and params.props else ""
            if not props_param and params.props:
                props_param = "props"
            
            # Build component code without f-string for JSX content to avoid brace issues
            component_code = imports_str + props_interface
            component_code += f"const {params.component_name} = ({props_param}) => {{\n"
            component_code += "  return (\n"
            if params.styling == "tailwind":
                component_code += f'    <div className="p-4">\n'
            else:
                component_code += f'    <div className={{styles.container}}>\n'
            component_code += f"      <h1>{params.component_name}</h1>\n"
            component_code += "      {/* Add your component logic here */}\n"
            component_code += "    </div>\n"
            component_code += "  );\n"
            component_code += "};\n\n"
            component_code += f"export default {params.component_name};\n"
            
        else:  # class component
            props_generic = f'<{params.component_name}Props>' if params.use_typescript and params.props else ''
            component_code = imports_str + props_interface
            component_code += f"class {params.component_name} extends React.Component{props_generic} {{\n"
            component_code += "  render() {\n"
            component_code += "    return (\n"
            if params.styling == "tailwind":
                component_code += f'      <div className="p-4">\n'
            else:
                component_code += f'      <div className={{styles.container}}>\n'
            component_code += f"        <h1>{params.component_name}</h1>\n"
            component_code += "        {/* Add your component logic here */}\n"
            component_code += "      </div>\n"
            component_code += "    );\n"
            component_code += "  }\n"
            component_code += "}\n\n"
            component_code += f"export default {params.component_name};\n"
        
        # Validate generated code for common issues
        # Check for double braces (except in comments)
        lines = component_code.split('\n')
        for i, line in enumerate(lines, 1):
            if '{{' in line or '}}' in line:
                # Allow in comments
                if not ('/*' in line or '//' in line):
                    # This might be a bug - log warning but don't fail
                    # (could be intentional in some cases)
                    pass
        
        # Create output directory
        output_dir = pathlib.Path(params.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write component file
        component_file = output_dir / f"{params.component_name}.{ext}"
        with open(component_file, 'w', encoding='utf-8') as f:
            f.write(component_code)
        
        # Generate CSS module if needed
        if params.styling == "css-modules":
            css_file = output_dir / f"{params.component_name}.module.css"
            css_content = f""".container {{
  padding: 1rem;
}}
"""
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(css_content)
        
        return ToolResult(
            success=True,
            data={
                "component_file": str(component_file),
                "component_name": params.component_name,
                "code": component_code
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def generate_nextjs_page(params: GenerateNextJSPageInput) -> ToolResult:
    """Generate a Next.js page"""
    try:
        ext = "tsx" if params.use_typescript else "jsx"
        
        # Build data fetching code
        data_fetching_code = ""
        if params.data_fetching == "SSR":
            data_fetching_code = """
export async function getServerSideProps(context) {
  // Fetch data on each request
  const data = await fetchData();
  
  return {
    props: { data },
  };
}
"""
        elif params.data_fetching == "SSG":
            data_fetching_code = """
export async function getStaticProps() {
  // Fetch data at build time
  const data = await fetchData();
  
  return {
    props: { data },
    revalidate: 60, // Revalidate every 60 seconds
  };
}
"""
        
        # Build page component - avoid f-string for JSX content
        page_title = params.page_name.replace('-', ' ').title()
        page_component_name = params.page_name.replace('-', '').title()
        
        page_code = "import React from 'react';\n\n"
        page_code += f"export default function {page_component_name}Page() {{\n"
        page_code += "  return (\n"
        page_code += "    <div>\n"
        page_code += f"      <h1>{page_title}</h1>\n"
        page_code += "      {/* Add your page content here */}\n"
        page_code += "    </div>\n"
        page_code += "  );\n"
        page_code += "}\n"
        page_code += data_fetching_code
        
        # Create output directory
        output_dir = pathlib.Path(params.output_dir) / params.page_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write page file
        page_file = output_dir / f"page.{ext}"
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(page_code)
        
        return ToolResult(
            success=True,
            data={
                "page_file": str(page_file),
                "route": params.route,
                "code": page_code
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def generate_api_route(params: GenerateAPIRouteInput) -> ToolResult:
    """Generate an API route"""
    try:
        ext = "ts" if params.use_typescript else "js"
        
        if params.framework == "nextjs":
            # Next.js App Router API route - avoid nested braces in f-strings
            api_code = "import { NextRequest, NextResponse } from 'next/server';\n\n"
            api_code += f"export async function {params.method}(request: NextRequest) {{\n"
            api_code += "  try {\n"
            api_code += "    // Add your API logic here\n"
            api_code += "    const data = { message: 'Success' };\n"
            api_code += "    \n"
            api_code += "    return NextResponse.json(data);\n"
            api_code += "  } catch (error) {\n"
            api_code += "    return NextResponse.json(\n"
            api_code += "      { error: 'Internal Server Error' },\n"
            api_code += "      { status: 500 }\n"
            api_code += "    );\n"
            api_code += "  }\n"
            api_code += "}\n"
        elif params.framework == "express":
            # Express route
            api_code = "import { Request, Response } from 'express';\n\n"
            api_code += f"export const {params.route_name} = async (req: Request, res: Response) => {{\n"
            api_code += "  try {\n"
            api_code += "    // Add your API logic here\n"
            api_code += "    const data = { message: 'Success' };\n"
            api_code += "    \n"
            api_code += "    res.json(data);\n"
            api_code += "  } catch (error) {\n"
            api_code += "    res.status(500).json({ error: 'Internal Server Error' });\n"
            api_code += "  }\n"
            api_code += "};\n"
        else:
            api_code = f"// API route for {params.route_name}\n"
            api_code += "export default async function handler(req, res) {\n"
            api_code += f"  if (req.method === '{params.method}') {{\n"
            api_code += "    // Add your API logic here\n"
            api_code += "    res.status(200).json({ message: 'Success' });\n"
            api_code += "  } else {\n"
            api_code += "    res.status(405).json({ error: 'Method not allowed' });\n"
            api_code += "  }\n"
            api_code += "}\n"
        
        # Create output directory
        output_dir = pathlib.Path(params.output_dir) / params.route_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write API route file
        route_file = output_dir / f"route.{ext}"
        with open(route_file, 'w', encoding='utf-8') as f:
            f.write(api_code)
        
        return ToolResult(
            success=True,
            data={
                "route_file": str(route_file),
                "code": api_code
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def typescript_check(params: TypeScriptCheckInput) -> ToolResult:
    """Run TypeScript type checking"""
    try:
        cmd = ['npx', 'tsc', '--noEmit']
        
        if params.strict:
            cmd.append('--strict')
        
        if params.file_path:
            cmd.append(params.file_path)
        
        result = subprocess.run(
            cmd,
            cwd=params.project_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return ToolResult(
            success=result.returncode == 0,
            data={
                "output": result.stdout,
                "errors": result.stderr,
                "has_errors": result.returncode != 0
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def eslint_check(params: ESLintCheckInput) -> ToolResult:
    """Run ESLint checking"""
    try:
        cmd = ['npx', 'eslint']
        
        if params.fix:
            cmd.append('--fix')
        
        if params.file_path:
            cmd.append(params.file_path)
        else:
            cmd.extend(['--ext', '.js,.jsx,.ts,.tsx', '.'])
        
        cmd.append('--format=json')
        
        result = subprocess.run(
            cmd,
            cwd=params.project_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        try:
            lint_results = json.loads(result.stdout) if result.stdout else []
        except:
            lint_results = []
        
        return ToolResult(
            success=result.returncode == 0,
            data={
                "results": lint_results,
                "fixed": params.fix
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def prettier_format(params: PrettierFormatInput) -> ToolResult:
    """Format code with Prettier"""
    try:
        cmd = ['npx', 'prettier']
        
        if params.write:
            cmd.append('--write')
        else:
            cmd.append('--check')
        
        cmd.append(params.file_path)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return ToolResult(
            success=result.returncode == 0,
            data={
                "formatted": params.write,
                "output": result.stdout
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def npm_command(params: NPMCommandInput) -> ToolResult:
    """Execute NPM commands"""
    try:
        cmd = ['npm', params.command]
        
        if params.args:
            cmd.extend(params.args)
        
        result = subprocess.run(
            cmd,
            cwd=params.working_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        return ToolResult(
            success=result.returncode == 0,
            data={
                "output": result.stdout,
                "errors": result.stderr
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def generate_type_definitions(params: GenerateTypeDefinitionsInput) -> ToolResult:
    """Generate TypeScript type definitions from JSON or API response"""
    try:
        # Parse source if it's JSON
        try:
            data = json.loads(params.source)
        except:
            return ToolResult(success=False, error="Invalid JSON source")
        
        def generate_type(obj: Any, name: str) -> str:
            """Recursively generate TypeScript types"""
            if isinstance(obj, dict):
                fields = []
                for key, value in obj.items():
                    ts_type = get_ts_type(value)
                    fields.append(f"  {key}: {ts_type};")
                return f"interface {name} {{\n" + "\n".join(fields) + "\n}"
            elif isinstance(obj, list) and obj:
                item_type = get_ts_type(obj[0])
                return f"type {name} = {item_type}[];"
            else:
                return f"type {name} = {get_ts_type(obj)};"
        
        def get_ts_type(value: Any) -> str:
            """Get TypeScript type for a value"""
            if isinstance(value, bool):
                return "boolean"
            elif isinstance(value, int) or isinstance(value, float):
                return "number"
            elif isinstance(value, str):
                return "string"
            elif isinstance(value, list):
                if value:
                    return f"{get_ts_type(value[0])}[]"
                return "any[]"
            elif isinstance(value, dict):
                return "object"
            elif value is None:
                return "null"
            else:
                return "any"
        
        type_def = generate_type(data, params.type_name)
        
        # Write to file
        output_path = pathlib.Path(params.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"// Auto-generated type definitions\n\n{type_def}\n")
        
        return ToolResult(
            success=True,
            data={
                "type_definition": type_def,
                "output_file": str(output_path)
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))
