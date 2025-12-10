"""
Redux Tools - Generate Redux store setup, slices, and mock data
"""
import json
import pathlib
import re
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from ..tool_schemas import ToolResult, ComponentSchema, GenerateReduxSetupInput


# ============================================================================
# Input Schemas - Now imported from tool_schemas.py
# ============================================================================

# Schema definitions moved to tool_schemas.py to avoid circular imports


def _generate_mock_data(prop_type: str, prop_name: str) -> Any:
    """Generate realistic mock data based on prop type"""
    
    # Handle array types
    if prop_type.startswith("Array<") or prop_type.endswith("[]"):
        # Extract inner type
        inner_type = prop_type.replace("Array<", "").replace(">", "").replace("[]", "").strip()
        
        # Generate array of 3-5 items
        count = 4
        items = []
        
        if "{" in inner_type:  # Object type
            # Parse object structure: {title: string; description: string}
            obj_match = re.findall(r'(\w+):\s*(\w+)', inner_type)
            for i in range(count):
                obj = {}
                for field_name, field_type in obj_match:
                    obj[field_name] = _generate_mock_data(field_type, field_name)
                items.append(obj)
        else:
            # Simple array type
            for i in range(count):
                items.append(_generate_mock_data(inner_type, prop_name))
        
        return items
    
    # Handle primitive types
    if prop_type == "string":
        # Generate contextual strings based on prop name
        if "title" in prop_name.lower():
            return f"Sample Title {prop_name}"
        elif "description" in prop_name.lower():
            return f"This is a sample description for {prop_name}"
        elif "name" in prop_name.lower():
            return f"Sample Name"
        elif "email" in prop_name.lower():
            return "user@example.com"
        elif "url" in prop_name.lower() or "link" in prop_name.lower():
            return "https://example.com"
        elif "message" in prop_name.lower() or "text" in prop_name.lower():
            return "Sample message text"
        else:
            return f"Sample {prop_name}"
    
    elif prop_type == "number":
        return 42
    
    elif prop_type == "boolean":
        return True
    
    else:
        # Default to string
        return f"Sample {prop_name}"


def _extract_props_interface(component_content: str) -> Dict[str, str]:
    """Extract props interface from component code"""
    props_dict = {}
    
    # Find interface definition
    interface_match = re.search(
        r'interface\s+\w+Props\s*\{([^}]+)\}',
        component_content,
        re.MULTILINE | re.DOTALL
    )
    
    if interface_match:
        interface_body = interface_match.group(1)
        
        # Extract each prop: name: type;
        prop_matches = re.findall(
            r'(\w+):\s*([^;]+);',
            interface_body
        )
        
        for prop_name, prop_type in prop_matches:
            props_dict[prop_name] = prop_type.strip()
    
    return props_dict


def _generate_slice_file(component_schema: ComponentSchema, output_dir: pathlib.Path) -> str:
    """Generate a Redux slice file with mock data"""
    
    slice_name = component_schema.name.replace('Component', '').lower()
    
    # Generate initial state with mock data
    initial_state = {}
    for prop_name, prop_type in component_schema.props.items():
        initial_state[prop_name] = _generate_mock_data(prop_type, prop_name)
    
    # Format initial state as JSON-like JavaScript object
    state_str = json.dumps(initial_state, indent=2)
    
    # Generate slice code
    slice_code = f"""import {{ createSlice, PayloadAction }} from '@reduxjs/toolkit';

interface {component_schema.name}State {{
"""
    
    # Add state interface props
    for prop_name, prop_type in component_schema.props.items():
        slice_code += f"  {prop_name}: {prop_type};\n"
    
    slice_code += f"""}}

const initialState: {component_schema.name}State = {state_str};

const {slice_name}Slice = createSlice({{
  name: '{slice_name}',
  initialState,
  reducers: {{
    // Add reducers here as needed
  }},
}});

export const {{ }} = {slice_name}Slice.actions;
export default {slice_name}Slice.reducer;
"""
    
    # Write slice file
    slice_file = output_dir / f"{slice_name}Slice.ts"
    slice_file.write_text(slice_code, encoding='utf-8')
    
    return str(slice_file)


def _generate_store_file(component_schemas: List[ComponentSchema], output_dir: pathlib.Path) -> str:
    """Generate Redux store configuration"""
    
    # Generate imports
    imports = ["import { configureStore } from '@reduxjs/toolkit';"]
    
    reducers = []
    for schema in component_schemas:
        slice_name = schema.name.replace('Component', '').lower()
        imports.append(f"import {slice_name}Reducer from './{slice_name}Slice';")
        reducers.append(f"    {slice_name}: {slice_name}Reducer,")
    
    # Generate store code
    store_code = '\n'.join(imports) + '\n\n'
    store_code += """export const store = configureStore({
  reducer: {
"""
    store_code += '\n'.join(reducers) + '\n'
    store_code += """  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
"""
    
    # Write store file
    store_file = output_dir / "store.ts"
    store_file.write_text(store_code, encoding='utf-8')
    
    return str(store_file)


def _generate_hooks_file(output_dir: pathlib.Path) -> str:
    """Generate typed Redux hooks"""
    
    hooks_code = """import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from './store';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
"""
    
    # Write hooks file
    hooks_file = output_dir / "hooks.ts"
    hooks_file.write_text(hooks_code, encoding='utf-8')
    
    return str(hooks_file)


async def generate_redux_setup(params: GenerateReduxSetupInput) -> ToolResult:
    """Generate complete Redux store setup with slices and mock data"""
    try:
        output_dir = pathlib.Path(params.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        
        # Generate slice for each component
        for component_schema in params.components:
            if component_schema.props:  # Only create slice if component has props
                slice_file = _generate_slice_file(component_schema, output_dir)
                created_files.append(slice_file)
                print(f"✅ Generated Redux slice: {slice_file}")
        
        # Generate store configuration
        if params.components:
            store_file = _generate_store_file(params.components, output_dir)
            created_files.append(store_file)
            print(f"✅ Generated Redux store: {store_file}")
            
            # Generate typed hooks
            hooks_file = _generate_hooks_file(output_dir)
            created_files.append(hooks_file)
            print(f"✅ Generated Redux hooks: {hooks_file}")
        
        return ToolResult(
            success=True,
            data={
                "store_dir": str(output_dir),
                "files_created": created_files,
                "slices_count": len([f for f in created_files if 'Slice' in f])
            }
        )
    
    except Exception as e:
        return ToolResult(success=False, error=str(e))


# Export for agent
__all__ = ['generate_redux_setup', 'GenerateReduxSetupInput', 'ComponentSchema']
