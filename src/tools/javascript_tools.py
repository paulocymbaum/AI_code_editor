"""
JavaScript/TypeScript/React Tools
Specialized tools for JS/TS code generation and analysis
"""

import subprocess
import json
import pathlib
from typing import Optional, List, Dict, Any
from functools import lru_cache
from ..tool_schemas import (
    ToolResult,
    GenerateReactComponentInput,
    GenerateNextJSPageInput,
    GenerateAPIRouteInput,
    TypeScriptCheckInput,
    ESLintCheckInput,
    PrettierFormatInput,
    NpmCommandInput,
    GenerateTypeDefinitionsInput
)
from pydantic import BaseModel, Field
from .design_tokens import DesignTokens
from ..utils.path_utils import PathUtils


# ============================================================================
# NOTE: All input schemas are now centralized in src/tool_schemas.py
# This eliminates duplication and ensures consistency across the codebase.
# ============================================================================
# Pattern Loading
# ============================================================================
# Helper Functions for Design System Integration
# ============================================================================

def _get_component_pattern_code(
    component_name: str, 
    pattern: Optional[str], 
    variant: str = "primary",
    use_typescript: bool = True
) -> Dict[str, str]:
    """Generate component code with design system patterns"""
    
    patterns = {
        "button": {
            "jsx": f'''    <button className="btn-{variant}">
      {component_name}
    </button>''',
            "props": [
                {"name": "onClick", "type": "() => void"},
                {"name": "disabled", "type": "boolean"},
                {"name": "children", "type": "React.ReactNode"}
            ]
        },
        "card": {
            "jsx": f'''    <div className="card-interactive">
      <h3 className="text-2xl font-semibold mb-4">{component_name}</h3>
      <p className="text-neutral-600 dark:text-neutral-400 mb-6">
        {{/* Add your card content here */}}
      </p>
      <button className="btn-{variant}">
        Learn More
      </button>
    </div>''',
            "props": [
                {"name": "title", "type": "string"},
                {"name": "description", "type": "string"},
                {"name": "children", "type": "React.ReactNode"}
            ]
        },
        "form": {
            "jsx": '''    <form className="space-y-6">
      <div>
        <label className="label">Email Address</label>
        <input 
          type="email" 
          className="input" 
          placeholder="you@example.com"
        />
        <p className="helper-text">We'll never share your email</p>
      </div>
      
      <div>
        <label className="label">Password</label>
        <input 
          type="password" 
          className="input"
        />
      </div>
      
      <button type="submit" className="btn-primary w-full">
        Submit
      </button>
    </form>''',
            "props": [
                {"name": "onSubmit", "type": "(e: React.FormEvent) => void"}
            ]
        },
        "modal": {
            "jsx": f'''    <div className="modal-overlay">
      <div className="modal-content">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold">{component_name}</h2>
          <button 
            className="btn-ghost btn-sm"
            aria-label="Close"
          >
            ✕
          </button>
        </div>
        
        <div className="mb-6">
          {{/* Modal content */}}
        </div>
        
        <div className="flex gap-3 justify-end">
          <button className="btn-secondary">Cancel</button>
          <button className="btn-{variant}">Confirm</button>
        </div>
      </div>
    </div>''',
            "props": [
                {"name": "isOpen", "type": "boolean"},
                {"name": "onClose", "type": "() => void"},
                {"name": "children", "type": "React.ReactNode"}
            ]
        },
        "list": {
            "jsx": '''    <div className="space-y-3">
      {props.items.map((item, index) => (
        <div 
          key={index}
          className="card-hover flex items-center gap-4"
        >
          <div className="flex-shrink-0 w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center">
            <span className="text-primary-600 dark:text-primary-400 text-xl">
              {index + 1}
            </span>
          </div>
          <div className="flex-1">
            <h4 className="font-semibold">{item.title}</h4>
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              {item.description}
            </p>
          </div>
        </div>
      ))}
    </div>''',
            "props": [
                {"name": "items", "type": "Array<{title: string; description: string}>"}
            ]
        },
        "hero": {
            "jsx": f'''    <section className="section">
      <div className="container-narrow text-center">
        <h1 className="section-title text-gradient">
          {component_name}
        </h1>
        <p className="section-subtitle max-w-2xl mx-auto">
          Create stunning user interfaces with our professional design system
        </p>
        <div className="flex gap-4 justify-center mt-8">
          <button className="btn-{variant} btn-lg">
            Get Started
          </button>
          <button className="btn-outline btn-lg">
            Learn More
          </button>
        </div>
      </div>
    </section>''',
            "props": [
                {"name": "title", "type": "string"},
                {"name": "subtitle", "type": "string"}
            ]
        },
        "feature": {
            "jsx": '''    <div className="card">
      <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-xl flex items-center justify-center mb-4">
        <svg className="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <h3 className="text-xl font-semibold mb-2">Feature Title</h3>
      <p className="text-neutral-600 dark:text-neutral-400">
        Feature description goes here. Explain the benefit and value.
      </p>
    </div>''',
            "props": [
                {"name": "icon", "type": "React.ReactNode"},
                {"name": "title", "type": "string"},
                {"name": "description", "type": "string"}
            ]
        },
        "pricing": {
            "jsx": f'''    <div className="card text-center">
      <div className="inline-flex items-center gap-2 px-4 py-1 bg-primary-100 dark:bg-primary-900 rounded-full mb-4">
        <span className="text-sm font-medium text-primary-700 dark:text-primary-300">
          Popular
        </span>
      </div>
      
      <h3 className="text-2xl font-bold mb-2">Professional</h3>
      
      <div className="mb-6">
        <span className="text-5xl font-bold">$29</span>
        <span className="text-neutral-600 dark:text-neutral-400">/month</span>
      </div>
      
      <ul className="space-y-3 mb-8 text-left">
        <li className="flex items-center gap-2">
          <span className="text-success-600">✓</span>
          <span>Unlimited projects</span>
        </li>
        <li className="flex items-center gap-2">
          <span className="text-success-600">✓</span>
          <span>Priority support</span>
        </li>
        <li className="flex items-center gap-2">
          <span className="text-success-600">✓</span>
          <span>Advanced analytics</span>
        </li>
      </ul>
      
      <button className="btn-{variant} w-full">
        Get Started
      </button>
    </div>''',
            "props": [
                {"name": "title", "type": "string"},
                {"name": "price", "type": "number"},
                {"name": "features", "type": "string[]"},
                {"name": "isPopular", "type": "boolean"}
            ]
        },
        "sidebar": {
            "jsx": '''    <div className="flex flex-col h-full bg-white dark:bg-neutral-900 p-4">
      {/* Sidebar Header */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-neutral-900 dark:text-neutral-100">
          Navigation
        </h2>
      </div>
      
      {/* Navigation Items */}
      <nav className="flex-1 space-y-2">
        <a href="#" className="flex items-center gap-3 px-4 py-3 rounded-lg bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-primary-900/30 transition-colors">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <span className="font-medium">Dashboard</span>
        </a>
        
        <a href="#" className="flex items-center gap-3 px-4 py-3 rounded-lg text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <span className="font-medium">Messages</span>
        </a>
        
        <a href="#" className="flex items-center gap-3 px-4 py-3 rounded-lg text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span className="font-medium">Settings</span>
        </a>
      </nav>
      
      {/* Sidebar Footer */}
      <div className="pt-4 border-t border-neutral-200 dark:border-neutral-700">
        <div className="flex items-center gap-3 px-4 py-3">
          <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center text-white font-semibold">
            U
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100 truncate">
              User Name
            </p>
            <p className="text-xs text-neutral-500 dark:text-neutral-400 truncate">
              user@example.com
            </p>
          </div>
        </div>
      </div>
    </div>''',
            "props": [
                {"name": "items", "type": "Array<{label: string; href: string; icon?: React.ReactNode}>"},
                {"name": "userInfo", "type": "{name: string; email: string; avatar?: string}"}
            ]
        },
        "header": {
            "jsx": '''    <header className="flex items-center justify-between px-4 py-3 bg-white dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800">
      {/* Left: Logo/Brand */}
      <div className="flex items-center gap-4">
        <button 
          className="md:hidden p-2 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
          aria-label="Toggle menu"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        
        <h1 className="text-xl font-bold text-neutral-900 dark:text-neutral-100">
          App Name
        </h1>
      </div>
      
      {/* Center: Search (hidden on mobile) */}
      <div className="hidden md:flex flex-1 max-w-xl mx-8">
        <div className="relative w-full">
          <input 
            type="search"
            placeholder="Search..."
            className="w-full px-4 py-2 pl-10 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-lg focus:ring-2 focus:ring-primary-500 text-neutral-900 dark:text-neutral-100"
          />
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>
      
      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        <button className="p-2 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors relative">
          <svg className="w-6 h-6 text-neutral-700 dark:text-neutral-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <span className="absolute top-1 right-1 w-2 h-2 bg-error-500 rounded-full"></span>
        </button>
        
        <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center text-white font-semibold cursor-pointer hover:bg-primary-700 transition-colors">
          U
        </div>
      </div>
    </header>''',
            "props": [
                {"name": "title", "type": "string"},
                {"name": "onMenuClick", "type": "() => void"},
                {"name": "userAvatar", "type": "string"}
            ]
        },
        "footer": {
            "jsx": '''    <footer className="bg-neutral-100 dark:bg-neutral-900 border-t border-neutral-200 dark:border-neutral-800 px-4 py-3">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-neutral-600 dark:text-neutral-400">
        {/* Left: Copyright */}
        <div className="flex items-center gap-2">
          <span>© 2024 Company Name</span>
          <span className="hidden sm:inline">•</span>
          <span className="hidden sm:inline">All rights reserved</span>
        </div>
        
        {/* Right: Links */}
        <div className="flex items-center gap-4">
          <a href="#" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
            Privacy
          </a>
          <a href="#" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
            Terms
          </a>
          <a href="#" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
            Help
          </a>
        </div>
      </div>
    </footer>''',
            "props": [
                {"name": "copyright", "type": "string"},
                {"name": "links", "type": "Array<{label: string; href: string}>"}
            ]
        },
        "messages": {
            "jsx": '''    <div className="space-y-4">
      {/* Message from other user */}
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-neutral-300 dark:bg-neutral-700 flex-shrink-0"></div>
        <div className="flex-1">
          <div className="flex items-baseline gap-2 mb-1">
            <span className="font-semibold text-sm text-neutral-900 dark:text-neutral-100">
              User Name
            </span>
            <span className="text-xs text-neutral-500 dark:text-neutral-400">
              2:30 PM
            </span>
          </div>
          <div className="bg-neutral-100 dark:bg-neutral-800 rounded-2xl rounded-tl-none px-4 py-2.5 inline-block max-w-lg">
            <p className="text-neutral-900 dark:text-neutral-100">
              Hey! How are you doing today?
            </p>
          </div>
        </div>
      </div>
      
      {/* Message from current user */}
      <div className="flex items-start gap-3 flex-row-reverse">
        <div className="w-10 h-10 rounded-full bg-primary-600 flex-shrink-0"></div>
        <div className="flex-1 flex flex-col items-end">
          <div className="flex items-baseline gap-2 mb-1">
            <span className="text-xs text-neutral-500 dark:text-neutral-400">
              2:31 PM
            </span>
            <span className="font-semibold text-sm text-neutral-900 dark:text-neutral-100">
              You
            </span>
          </div>
          <div className="bg-primary-600 rounded-2xl rounded-tr-none px-4 py-2.5 inline-block max-w-lg">
            <p className="text-white">
              I'm doing great! Thanks for asking. How about you?
            </p>
          </div>
        </div>
      </div>
      
      {/* System message */}
      <div className="flex justify-center">
        <span className="text-xs text-neutral-500 dark:text-neutral-400 px-3 py-1 bg-neutral-100 dark:bg-neutral-800 rounded-full">
          Today
        </span>
      </div>
    </div>''',
            "props": [
                {"name": "messages", "type": "Array<{id: string; text: string; sender: string; timestamp: string; isCurrentUser: boolean}>"}
            ]
        },
        "input": {
            "jsx": '''    <div className="flex items-end gap-2 p-4 bg-white dark:bg-neutral-900 border-t border-neutral-200 dark:border-neutral-800">
      {/* Attachment button */}
      <button 
        className="p-2.5 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors flex-shrink-0"
        aria-label="Attach file"
      >
        <svg className="w-5 h-5 text-neutral-600 dark:text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
        </svg>
      </button>
      
      {/* Input field */}
      <div className="flex-1 relative">
        <textarea 
          placeholder="Type a message..."
          rows={1}
          className="w-full px-4 py-2.5 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl focus:ring-2 focus:ring-primary-500 text-neutral-900 dark:text-neutral-100 resize-none max-h-32"
        />
      </div>
      
      {/* Emoji button */}
      <button 
        className="p-2.5 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors flex-shrink-0"
        aria-label="Add emoji"
      >
        <svg className="w-5 h-5 text-neutral-600 dark:text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>
      
      {/* Send button */}
      <button 
        className="p-2.5 bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors flex-shrink-0"
        aria-label="Send message"
      >
        <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
        </svg>
      </button>
    </div>''',
            "props": [
                {"name": "value", "type": "string"},
                {"name": "onChange", "type": "(value: string) => void"},
                {"name": "onSubmit", "type": "() => void"},
                {"name": "placeholder", "type": "string"}
            ]
        }
    }
    
    # Return pattern or default
    if pattern and pattern in patterns:
        return patterns[pattern]
    
    # Default custom pattern
    return {
        "jsx": f'''    <div className="card">
      <h2 className="text-2xl font-semibold mb-4">{component_name}</h2>
      <p className="text-neutral-600 dark:text-neutral-400">
        {{/* Add your component logic here */}}
      </p>
    </div>''',
        "props": [{"name": "children", "type": "React.ReactNode"}]
    }


def _generate_enhanced_css_module(component_name: str, pattern: Optional[str]) -> str:
    """Generate enhanced CSS module with design system tokens"""
    
    if pattern == "button":
        return """.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-lg);
  font-weight: 500;
  transition: all var(--duration-base) var(--ease-default);
  cursor: pointer;
  border: none;
}

.primary {
  background-color: var(--color-primary-600);
  color: white;
}

.primary:hover {
  background-color: var(--color-primary-700);
  box-shadow: var(--shadow-md);
}

.primary:active {
  background-color: var(--color-primary-800);
}

.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
"""
    
    elif pattern == "card":
        return """.card {
  background-color: white;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-xl);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  transition: all var(--duration-base) var(--ease-default);
}

.card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-300);
  transform: translateY(-2px);
}

.title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--color-neutral-900);
}

.description {
  color: var(--color-neutral-600);
  line-height: 1.6;
}

@media (prefers-color-scheme: dark) {
  .card {
    background-color: var(--color-neutral-800);
    border-color: var(--color-neutral-700);
  }
  
  .title {
    color: var(--color-neutral-100);
  }
  
  .description {
    color: var(--color-neutral-400);
  }
}
"""
    
    # Default CSS module
    return f""".container {{
  padding: var(--spacing-base);
}}

.{component_name.lower()} {{
  display: flex;
  flex-direction: column;
  gap: 1rem;
}}

.title {{
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-neutral-900);
}}

@media (prefers-color-scheme: dark) {{
  .title {{
    color: var(--color-neutral-100);
  }}
}}
"""


# ============================================================================
# Tool Implementations
# ============================================================================

async def generate_react_component(params: GenerateReactComponentInput) -> ToolResult:
    """Generate a React component with design system integration"""
    try:
        # Determine file extension
        ext = "tsx" if params.use_typescript else "jsx"
        
        # Get component pattern if specified
        pattern_data = None
        if params.component_pattern:
            pattern_data = _get_component_pattern_code(
                params.component_name,
                params.component_pattern,
                params.variant or "primary",
                params.use_typescript
            )
        
        # Use pattern props or user-provided props
        component_props = params.props if params.props else (pattern_data["props"] if pattern_data else None)
        
        # Build props interface (TypeScript)
        props_interface = ""
        if params.use_typescript and component_props:
            props_interface = f"interface {params.component_name}Props {{\n"
            for prop in component_props:
                props_interface += f"  {prop['name']}: {prop['type']};\n"
            props_interface += "}\n\n"
        
        # Build imports
        imports = ["import React from 'react'"]
        if params.hooks:
            hooks_str = ", ".join(params.hooks)
            imports[0] = f"import React, {{ {hooks_str} }} from 'react'"
        
        # Add Redux imports if needed
        if params.with_redux:
            imports.append("import { useAppSelector } from '../store/hooks'")
        
        # Add styling imports
        if params.styling == "css-modules":
            imports.append(f"import styles from './{params.component_name}.module.css'")
        elif params.styling == "styled-components":
            imports.append("import styled from 'styled-components'")
        
        imports_str = "\n".join(imports) + "\n\n"
        
        # Build component
        if params.component_type == "functional":
            # If using Redux, don't use props parameter
            if params.with_redux:
                props_param = ""
            else:
                props_param = f"props: {params.component_name}Props" if params.use_typescript and component_props else ""
                if not props_param and component_props:
                    props_param = "props"
            
            # Get JSX content
            if pattern_data:
                jsx_content = pattern_data["jsx"]
                # If using Redux, replace props. with direct variable references
                if params.with_redux:
                    jsx_content = jsx_content.replace("props.items", "items")
                    jsx_content = jsx_content.replace("props.title", "title")
                    jsx_content = jsx_content.replace("props.description", "description")
                    jsx_content = jsx_content.replace("props.", "")
            elif params.styling == "tailwind":
                jsx_content = f'''    <div className="card">
      <h2 className="text-2xl font-semibold mb-4">{params.component_name}</h2>
      <p className="text-neutral-600 dark:text-neutral-400">
        {{/* Add your component logic here */}}
      </p>
    </div>'''
            else:
                jsx_content = f'''    <div className={{styles.container}}>
      <h1 className={{styles.title}}>{params.component_name}</h1>
      {{/* Add your component logic here */}}
    </div>'''
            
            # Build component code
            component_code = imports_str + props_interface
            component_code += f"const {params.component_name} = ({props_param}) => {{\n"
            
            # Add Redux selectors if needed
            if params.with_redux and component_props:
                slice_name = params.component_name.replace('Component', '').lower()
                for prop in component_props:
                    # Handle both dict and string formats
                    if isinstance(prop, dict):
                        prop_name = prop.get('name', '')
                    else:
                        prop_name = str(prop)
                    
                    if prop_name:
                        component_code += f"  const {prop_name} = useAppSelector((state) => state.{slice_name}.{prop_name});\n"
                component_code += "\n"
            
            component_code += "  return (\n"
            component_code += jsx_content + "\n"
            component_code += "  );\n"
            component_code += "};\n\n"
            component_code += f"export default {params.component_name};\n"
            
        else:  # class component
            props_generic = f'<{params.component_name}Props>' if params.use_typescript and component_props else ''
            
            # Get JSX content
            if pattern_data:
                jsx_content = pattern_data["jsx"]
            elif params.styling == "tailwind":
                jsx_content = f'''      <div className="card">
        <h2 className="text-2xl font-semibold mb-4">{params.component_name}</h2>
        <p className="text-neutral-600 dark:text-neutral-400">
          {{/* Add your component logic here */}}
        </p>
      </div>'''
            else:
                jsx_content = f'''      <div className={{styles.container}}>
        <h1 className={{styles.title}}>{params.component_name}</h1>
        {{/* Add your component logic here */}}
      </div>'''
            
            component_code = imports_str + props_interface
            component_code += f"class {params.component_name} extends React.Component{props_generic} {{\n"
            component_code += "  render() {\n"
            component_code += "    return (\n"
            component_code += jsx_content + "\n"
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
        
        # Determine output path - prioritize file_path over output_dir
        if params.file_path:
            # Use explicit file_path if provided
            component_file = pathlib.Path(params.file_path)
            output_dir = component_file.parent
        else:
            # Fall back to output_dir + component name
            output_dir = pathlib.Path(params.output_dir)
            component_file = output_dir / f"{params.component_name}.{ext}"
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write component file
        with open(component_file, 'w', encoding='utf-8') as f:
            f.write(component_code)
        
        # Generate CSS module if needed
        if params.styling == "css-modules":
            css_file = output_dir / f"{params.component_name}.module.css"
            css_content = _generate_enhanced_css_module(
                params.component_name, 
                params.component_pattern
            )
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(css_content)
        
        # Extract prop schemas
        prop_schemas = {}
        if component_props:
            for prop in component_props:
                if isinstance(prop, dict):
                    prop_name = prop.get('name', '')
                    prop_type = prop.get('type', 'any')
                    if prop_name:
                        prop_schemas[prop_name] = prop_type
        
        return ToolResult(
            success=True,
            data={
                "component_file": str(component_file),
                "component_name": params.component_name,
                "code": component_code,
                "prop_schemas": prop_schemas
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


async def npm_command(params: NpmCommandInput) -> ToolResult:
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
