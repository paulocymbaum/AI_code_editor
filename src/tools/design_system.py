"""
Design System Generator Tool
Generates professional design systems with Tailwind config, global CSS, and component patterns
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from ..tool_schemas import ToolResult
from .design_tokens import DesignTokens


# ============================================================================
# Input Schemas
# ============================================================================

class GenerateDesignSystemInput(BaseModel):
    """Input for generating a complete design system"""
    project_path: str = Field(..., description="Root path of the project")
    framework: str = Field(
        default="nextjs",
        description="Framework: nextjs, react, vite"
    )
    include_dark_mode: bool = Field(
        default=True,
        description="Include dark mode support"
    )
    include_component_patterns: bool = Field(
        default=True,
        description="Generate component pattern CSS"
    )
    include_docs: bool = Field(
        default=True,
        description="Generate documentation"
    )
    include_layout: bool = Field(
        default=True,
        description="Generate Next.js layout file (for Next.js projects)"
    )
    css_output_path: Optional[str] = Field(
        default=None,
        description="Custom CSS output path (default: src/app/globals.css for Next.js)"
    )
    tailwind_config_path: Optional[str] = Field(
        default=None,
        description="Custom Tailwind config path (default: ./tailwind.config.js)"
    )


# ============================================================================
# Design System Generator
# ============================================================================

class DesignSystemGenerator:
    """Generates complete design system files"""
    
    def __init__(self, tokens: DesignTokens):
        self.tokens = tokens
    
    def generate_tailwind_config(self, include_dark_mode: bool = True) -> str:
        """Generate Tailwind configuration"""
        
        # Build color palette
        colors = self.tokens.COLORS
        
        config = {
            "content": [
                "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
                "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
                "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
            ],
            "darkMode": "class" if include_dark_mode else False,
            "theme": {
                "extend": {
                    "colors": {
                        "primary": colors["primary"],
                        "neutral": colors["neutral"],
                        "success": colors["success"],
                        "warning": colors["warning"],
                        "error": colors["error"],
                        "info": colors["info"],
                    },
                    "fontFamily": {
                        "sans": self.tokens.TYPOGRAPHY["font_families"]["sans"],
                        "serif": self.tokens.TYPOGRAPHY["font_families"]["serif"],
                        "mono": self.tokens.TYPOGRAPHY["font_families"]["mono"],
                    },
                    "fontSize": self.tokens.TYPOGRAPHY["font_sizes"],
                    "fontWeight": self.tokens.TYPOGRAPHY["font_weights"],
                    "lineHeight": self.tokens.TYPOGRAPHY["line_heights"],
                    "letterSpacing": self.tokens.TYPOGRAPHY["letter_spacing"],
                    "spacing": self.tokens.SPACING,
                    "borderRadius": self.tokens.BORDERS["radius"],
                    "borderWidth": self.tokens.BORDERS["width"],
                    "boxShadow": self.tokens.SHADOWS,
                    "screens": self.tokens.BREAKPOINTS,
                    "zIndex": self.tokens.Z_INDEX,
                    "transitionDuration": self.tokens.ANIMATIONS["durations"],
                    "transitionTimingFunction": self.tokens.ANIMATIONS["timing_functions"],
                }
            },
            "plugins": [],
        }
        
        # Format as JavaScript module
        config_str = json.dumps(config, indent=2)
        
        js_config = f"""/** @type {{import('tailwindcss').Config}} */
module.exports = {config_str}
"""
        return js_config
    
    def generate_global_css(self, include_dark_mode: bool = True, 
                          include_components: bool = True) -> str:
        """Generate global CSS with CSS variables and component patterns"""
        
        colors = self.tokens.COLORS
        typography = self.tokens.TYPOGRAPHY
        spacing = self.tokens.SPACING
        shadows = self.tokens.SHADOWS
        animations = self.tokens.ANIMATIONS
        
        css_parts = []
        
        # Tailwind directives
        css_parts.append("""@tailwind base;
@tailwind components;
@tailwind utilities;
""")
        
        # Base layer with CSS custom properties
        css_parts.append("""
@layer base {
  :root {
    /* Colors - Primary */""")
        
        for shade, value in colors["primary"].items():
            css_parts.append(f"    --color-primary-{shade}: {value};")
        
        css_parts.append("""
    /* Colors - Neutral */""")
        for shade, value in colors["neutral"].items():
            css_parts.append(f"    --color-neutral-{shade}: {value};")
        
        css_parts.append("""
    /* Colors - Semantic */""")
        for name, value in colors["semantic"].items():
            css_parts.append(f"    --color-{name}: {value};")
        
        css_parts.append("""
    /* Typography */""")
        css_parts.append(f"    --font-sans: {', '.join(typography['font_families']['sans'])};")
        css_parts.append(f"    --font-serif: {', '.join(typography['font_families']['serif'])};")
        css_parts.append(f"    --font-mono: {', '.join(typography['font_families']['mono'])};")
        
        css_parts.append("""
    /* Spacing */""")
        css_parts.append(f"    --spacing-base: {spacing['4']};")
        css_parts.append(f"    --spacing-section: {spacing['24']};")
        
        css_parts.append("""
    /* Shadows */""")
        css_parts.append(f"    --shadow-sm: {shadows['sm']};")
        css_parts.append(f"    --shadow-md: {shadows['md']};")
        css_parts.append(f"    --shadow-lg: {shadows['lg']};")
        css_parts.append(f"    --shadow-xl: {shadows['xl']};")
        
        css_parts.append("""
    /* Animations */""")
        css_parts.append(f"    --duration-fast: {animations['durations']['150']};")
        css_parts.append(f"    --duration-base: {animations['durations']['200']};")
        css_parts.append(f"    --duration-slow: {animations['durations']['300']};")
        css_parts.append(f"    --ease-default: {animations['timing_functions']['ease']};")
        css_parts.append(f"    --ease-in-out: {animations['timing_functions']['ease-in-out']};")
        
        css_parts.append("""
    /* Border Radius */""")
        css_parts.append(f"    --radius-sm: {self.tokens.BORDERS['radius']['sm']};")
        css_parts.append(f"    --radius-md: {self.tokens.BORDERS['radius']['md']};")
        css_parts.append(f"    --radius-lg: {self.tokens.BORDERS['radius']['lg']};")
        css_parts.append(f"    --radius-xl: {self.tokens.BORDERS['radius']['xl']};")
        
        css_parts.append("""  }
""")
        
        # Dark mode variables
        if include_dark_mode:
            css_parts.append("""
  .dark {
    /* Dark mode color overrides */
    --color-background: #0f172a;
    --color-surface: #1e293b;
    --color-text-primary: #f1f5f9;
    --color-text-secondary: #cbd5e1;
    --color-text-tertiary: #94a3b8;
    --color-border: #334155;
    --color-border-hover: #475569;
    
    /* Adjust shadows for dark mode */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.5);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -1px rgba(0, 0, 0, 0.3);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.3);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.3);
  }
""")
        
        # Base element styles
        css_parts.append("""
  * {
    @apply border-neutral-200 dark:border-neutral-700;
  }

  html {
    @apply scroll-smooth;
  }

  body {
    @apply bg-neutral-50 text-neutral-900 dark:bg-neutral-900 dark:text-neutral-100;
    @apply antialiased;
    font-family: var(--font-sans);
  }

  h1, h2, h3, h4, h5, h6 {
    @apply font-semibold tracking-tight;
  }

  h1 {
    @apply text-5xl;
  }

  h2 {
    @apply text-4xl;
  }

  h3 {
    @apply text-3xl;
  }

  h4 {
    @apply text-2xl;
  }

  h5 {
    @apply text-xl;
  }

  h6 {
    @apply text-lg;
  }

  a {
    @apply text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300;
    @apply transition-colors duration-200;
  }

  code {
    @apply font-mono text-sm;
    @apply bg-neutral-100 dark:bg-neutral-800;
    @apply px-1.5 py-0.5 rounded;
  }

  pre {
    @apply font-mono text-sm;
    @apply bg-neutral-100 dark:bg-neutral-800;
    @apply p-4 rounded-lg overflow-x-auto;
  }

  pre code {
    @apply bg-transparent p-0;
  }
}
""")
        
        # Component patterns
        if include_components:
            css_parts.append(self._generate_component_patterns())
        
        # Utility classes
        css_parts.append("""
@layer utilities {
  /* Focus visible styles for accessibility */
  .focus-visible-ring {
    @apply focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2;
  }

  /* Smooth transitions */
  .transition-smooth {
    transition: all var(--duration-base) var(--ease-default);
  }

  /* Text gradients */
  .text-gradient {
    @apply bg-clip-text text-transparent;
    background-image: linear-gradient(135deg, var(--color-primary-600), var(--color-primary-400));
  }

  /* Glassmorphism effect */
  .glass {
    @apply bg-white/70 dark:bg-neutral-900/70;
    @apply backdrop-blur-lg;
    @apply border border-neutral-200/50 dark:border-neutral-700/50;
  }

  /* Animated gradient background */
  .gradient-animated {
    background: linear-gradient(
      -45deg,
      var(--color-primary-400),
      var(--color-primary-600),
      var(--color-primary-700),
      var(--color-primary-500)
    );
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
  }

  /* Hide scrollbar but keep functionality */
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }

  /* Custom scrollbar */
  .scrollbar-custom {
    scrollbar-width: thin;
    scrollbar-color: var(--color-primary-500) transparent;
  }
  
  .scrollbar-custom::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  .scrollbar-custom::-webkit-scrollbar-track {
    background: transparent;
  }
  
  .scrollbar-custom::-webkit-scrollbar-thumb {
    background-color: var(--color-primary-500);
    border-radius: 4px;
  }
  
  .scrollbar-custom::-webkit-scrollbar-thumb:hover {
    background-color: var(--color-primary-600);
  }

  /* Reduced motion support */
  @media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
}
""")
        
        # Keyframe animations
        css_parts.append("""
/* Keyframe Animations */
@keyframes gradient {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

@keyframes slideInUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes slideInDown {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes slideInLeft {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes scaleIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
""")
        
        return "\n".join(css_parts)
    
    def _generate_component_patterns(self) -> str:
        """Generate component pattern CSS"""
        return """
@layer components {
  /* Button Patterns */
  .btn {
    @apply inline-flex items-center justify-center gap-2;
    @apply px-6 py-3 rounded-lg;
    @apply font-medium text-base;
    @apply transition-all duration-200;
    @apply focus-visible-ring;
    @apply disabled:opacity-50 disabled:cursor-not-allowed;
  }

  .btn-primary {
    @apply btn;
    @apply bg-primary-600 text-white;
    @apply hover:bg-primary-700 active:bg-primary-800;
    @apply shadow-sm hover:shadow-md;
  }

  .btn-secondary {
    @apply btn;
    @apply bg-neutral-200 text-neutral-900;
    @apply hover:bg-neutral-300 active:bg-neutral-400;
    @apply dark:bg-neutral-700 dark:text-neutral-100;
    @apply dark:hover:bg-neutral-600 dark:active:bg-neutral-500;
  }

  .btn-outline {
    @apply btn;
    @apply bg-transparent border-2 border-primary-600 text-primary-600;
    @apply hover:bg-primary-50 active:bg-primary-100;
    @apply dark:hover:bg-primary-950 dark:active:bg-primary-900;
  }

  .btn-ghost {
    @apply btn;
    @apply bg-transparent text-neutral-700;
    @apply hover:bg-neutral-100 active:bg-neutral-200;
    @apply dark:text-neutral-300;
    @apply dark:hover:bg-neutral-800 dark:active:bg-neutral-700;
  }

  .btn-sm {
    @apply px-4 py-2 text-sm;
  }

  .btn-lg {
    @apply px-8 py-4 text-lg;
  }

  /* Card Patterns */
  .card {
    @apply bg-white dark:bg-neutral-800;
    @apply border border-neutral-200 dark:border-neutral-700;
    @apply rounded-xl shadow-sm;
    @apply p-6;
    @apply transition-shadow duration-200;
  }

  .card-hover {
    @apply card;
    @apply hover:shadow-md cursor-pointer;
  }

  .card-interactive {
    @apply card-hover;
    @apply hover:border-primary-300 dark:hover:border-primary-700;
    @apply hover:-translate-y-1;
    @apply transition-all duration-200;
  }

  /* Input Patterns */
  .input {
    @apply w-full px-4 py-2.5;
    @apply bg-white dark:bg-neutral-800;
    @apply border border-neutral-300 dark:border-neutral-600;
    @apply rounded-lg;
    @apply text-neutral-900 dark:text-neutral-100;
    @apply placeholder:text-neutral-400 dark:placeholder:text-neutral-500;
    @apply focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent;
    @apply disabled:opacity-50 disabled:cursor-not-allowed;
    @apply transition-all duration-200;
  }

  .input-error {
    @apply input;
    @apply border-error-500 focus:ring-error-500;
  }

  .input-success {
    @apply input;
    @apply border-success-500 focus:ring-success-500;
  }

  .label {
    @apply block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1.5;
  }

  .helper-text {
    @apply text-sm text-neutral-500 dark:text-neutral-400 mt-1;
  }

  .error-text {
    @apply text-sm text-error-600 dark:text-error-400 mt-1;
  }

  /* Badge Patterns */
  .badge {
    @apply inline-flex items-center gap-1;
    @apply px-2.5 py-0.5 rounded-full;
    @apply text-xs font-medium;
  }

  .badge-primary {
    @apply badge;
    @apply bg-primary-100 text-primary-800;
    @apply dark:bg-primary-900 dark:text-primary-200;
  }

  .badge-success {
    @apply badge;
    @apply bg-success-100 text-success-800;
    @apply dark:bg-success-900 dark:text-success-200;
  }

  .badge-warning {
    @apply badge;
    @apply bg-warning-100 text-warning-800;
    @apply dark:bg-warning-900 dark:text-warning-200;
  }

  .badge-error {
    @apply badge;
    @apply bg-error-100 text-error-800;
    @apply dark:bg-error-900 dark:text-error-200;
  }

  /* Alert Patterns */
  .alert {
    @apply p-4 rounded-lg;
    @apply border-l-4;
  }

  .alert-info {
    @apply alert;
    @apply bg-info-50 border-info-500 text-info-900;
    @apply dark:bg-info-900 dark:border-info-500 dark:text-info-100;
  }

  .alert-success {
    @apply alert;
    @apply bg-success-50 border-success-500 text-success-900;
    @apply dark:bg-success-900 dark:border-success-500 dark:text-success-100;
  }

  .alert-warning {
    @apply alert;
    @apply bg-warning-50 border-warning-500 text-warning-900;
    @apply dark:bg-warning-900 dark:border-warning-500 dark:text-warning-100;
  }

  .alert-error {
    @apply alert;
    @apply bg-error-50 border-error-500 text-error-900;
    @apply dark:bg-error-900 dark:border-error-500 dark:text-error-100;
  }

  /* Modal/Dialog Patterns */
  .modal-overlay {
    @apply fixed inset-0 bg-black/50 backdrop-blur-sm z-40;
    @apply flex items-center justify-center p-4;
  }

  .modal-content {
    @apply card;
    @apply max-w-lg w-full max-h-[90vh] overflow-y-auto;
    @apply shadow-xl;
    animation: scaleIn 0.2s ease-out;
  }

  /* Dropdown Patterns */
  .dropdown {
    @apply absolute mt-2 w-56;
    @apply bg-white dark:bg-neutral-800;
    @apply border border-neutral-200 dark:border-neutral-700;
    @apply rounded-lg shadow-lg;
    @apply py-1;
    @apply z-50;
    animation: slideInDown 0.15s ease-out;
  }

  .dropdown-item {
    @apply block w-full px-4 py-2.5;
    @apply text-left text-sm text-neutral-700 dark:text-neutral-300;
    @apply hover:bg-neutral-100 dark:hover:bg-neutral-700;
    @apply transition-colors duration-150;
  }

  .dropdown-divider {
    @apply my-1 border-t border-neutral-200 dark:border-neutral-700;
  }

  /* Loading Patterns */
  .spinner {
    @apply inline-block w-5 h-5;
    @apply border-2 border-current border-t-transparent;
    @apply rounded-full;
    animation: spin 0.6s linear infinite;
  }

  .skeleton {
    @apply bg-neutral-200 dark:bg-neutral-700;
    @apply rounded animate-pulse;
  }

  /* Link Patterns */
  .link {
    @apply text-primary-600 dark:text-primary-400;
    @apply hover:text-primary-700 dark:hover:text-primary-300;
    @apply underline-offset-4 hover:underline;
    @apply transition-colors duration-150;
  }

  /* Container Patterns */
  .container-narrow {
    @apply max-w-4xl mx-auto px-4 sm:px-6 lg:px-8;
  }

  .container-wide {
    @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8;
  }

  /* Section Patterns */
  .section {
    @apply py-16 sm:py-20 lg:py-24;
  }

  .section-header {
    @apply text-center mb-12;
  }

  .section-title {
    @apply text-4xl sm:text-5xl font-bold mb-4;
  }

  .section-subtitle {
    @apply text-lg sm:text-xl text-neutral-600 dark:text-neutral-400;
  }
}
"""
    
    def generate_documentation(self) -> str:
        """Generate design system documentation"""
        
        doc = """# Design System Documentation

## Overview

This design system provides a comprehensive set of design tokens, component patterns, and utilities to build consistent, accessible, and beautiful user interfaces.

## Design Tokens

### Colors

#### Primary Colors
Used for primary actions, links, and brand elements.

```css
primary-50   #eff6ff  /* Lightest */
primary-100  #dbeafe
primary-200  #bfdbfe
primary-300  #93c5fd
primary-400  #60a5fa
primary-500  #3b82f6  /* Base */
primary-600  #2563eb
primary-700  #1d4ed8
primary-800  #1e40af
primary-900  #1e3a8a  /* Darkest */
primary-950  #172554
```

#### Neutral Colors
Used for text, backgrounds, and borders.

```css
neutral-50   #fafafa  /* Lightest */
neutral-100  #f5f5f5
neutral-200  #e5e5e5
neutral-300  #d4d4d4
neutral-400  #a3a3a3
neutral-500  #737373  /* Base */
neutral-600  #525252
neutral-700  #404040
neutral-800  #262626
neutral-900  #171717  /* Darkest */
neutral-950  #0a0a0a
```

#### Semantic Colors
- **Success**: Green shades for positive actions and feedback
- **Warning**: Amber shades for warnings and cautions
- **Error**: Red shades for errors and destructive actions
- **Info**: Blue shades for informational messages

### Typography

#### Font Families
- **Sans**: System fonts optimized for readability
- **Serif**: Traditional serif fonts for headings
- **Mono**: Monospace fonts for code

#### Font Sizes
```
xs:   0.75rem   (12px)
sm:   0.875rem  (14px)
base: 1rem      (16px)
lg:   1.125rem  (18px)
xl:   1.25rem   (20px)
2xl:  1.5rem    (24px)
3xl:  1.875rem  (30px)
4xl:  2.25rem   (36px)
5xl:  3rem      (48px)
6xl:  3.75rem   (60px)
7xl:  4.5rem    (72px)
8xl:  6rem      (96px)
9xl:  8rem      (128px)
```

#### Font Weights
```
thin:       100
extralight: 200
light:      300
normal:     400
medium:     500
semibold:   600
bold:       700
extrabold:  800
black:      900
```

### Spacing

Consistent spacing scale from 0px to 384px (96 units):
```
0:  0px      4:  1rem (16px)    8:  2rem (32px)
1:  0.25rem  5:  1.25rem        12: 3rem (48px)
2:  0.5rem   6:  1.5rem         16: 4rem (64px)
3:  0.75rem  7:  1.75rem        24: 6rem (96px)
```

### Shadows

```css
sm:    Small subtle shadow
md:    Medium shadow (default)
lg:    Large prominent shadow
xl:    Extra large shadow
2xl:   Dramatic shadow
inner: Inset shadow
none:  No shadow
```

### Animations

#### Durations
- **fast**: 150ms - Quick transitions
- **base**: 200ms - Default transitions
- **slow**: 300ms - Deliberate transitions
- **slower**: 500ms - Dramatic transitions

#### Timing Functions
- **ease**: Default easing
- **easeIn**: Starts slow
- **easeOut**: Ends slow
- **easeInOut**: Smooth both ways
- **linear**: Constant speed

## Component Patterns

### Buttons

```jsx
// Primary button
<button className="btn-primary">
  Click Me
</button>

// Secondary button
<button className="btn-secondary">
  Secondary
</button>

// Outline button
<button className="btn-outline">
  Outline
</button>

// Ghost button
<button className="btn-ghost">
  Ghost
</button>

// Size variants
<button className="btn-primary btn-sm">Small</button>
<button className="btn-primary">Default</button>
<button className="btn-primary btn-lg">Large</button>
```

### Cards

```jsx
// Basic card
<div className="card">
  <h3>Card Title</h3>
  <p>Card content goes here</p>
</div>

// Hoverable card
<div className="card-hover">
  Content with shadow on hover
</div>

// Interactive card (clickable)
<div className="card-interactive">
  Clickable card with lift effect
</div>
```

### Forms

```jsx
// Input with label
<div>
  <label className="label">Email Address</label>
  <input type="email" className="input" placeholder="you@example.com" />
  <p className="helper-text">We'll never share your email</p>
</div>

// Error state
<div>
  <label className="label">Password</label>
  <input type="password" className="input-error" />
  <p className="error-text">Password is required</p>
</div>

// Success state
<input type="text" className="input-success" />
```

### Badges

```jsx
<span className="badge-primary">Primary</span>
<span className="badge-success">Success</span>
<span className="badge-warning">Warning</span>
<span className="badge-error">Error</span>
```

### Alerts

```jsx
<div className="alert-info">
  Informational message
</div>

<div className="alert-success">
  Success message
</div>

<div className="alert-warning">
  Warning message
</div>

<div className="alert-error">
  Error message
</div>
```

## Dark Mode

Dark mode is enabled by adding the `dark` class to the root element (typically `<html>`):

```jsx
// Toggle dark mode
document.documentElement.classList.toggle('dark');
```

All component patterns automatically adapt to dark mode using Tailwind's `dark:` variant.

## Accessibility

### Focus States
All interactive elements include focus-visible styles for keyboard navigation:
```jsx
<button className="btn-primary focus-visible-ring">
  Accessible Button
</button>
```

### Reduced Motion
The design system respects user's motion preferences:
```css
@media (prefers-reduced-motion: reduce) {
  /* Animations are reduced to minimal duration */
}
```

### Contrast
All color combinations meet WCAG AA contrast requirements for normal text (4.5:1) and large text (3:1).

### Screen Readers
Use semantic HTML and ARIA attributes when needed:
```jsx
<button aria-label="Close dialog" className="btn-ghost">
  <XIcon />
</button>
```

## Utility Classes

### Focus Ring
```jsx
<button className="focus-visible-ring">
  Keyboard accessible
</button>
```

### Smooth Transitions
```jsx
<div className="transition-smooth">
  Smooth transitions for all properties
</div>
```

### Text Gradient
```jsx
<h1 className="text-gradient">
  Gradient Text
</h1>
```

### Glassmorphism
```jsx
<div className="glass">
  Frosted glass effect
</div>
```

### Custom Scrollbar
```jsx
<div className="scrollbar-custom overflow-auto">
  Content with styled scrollbar
</div>
```

## Best Practices

### 1. Consistent Spacing
Use the spacing scale for margins, padding, and gaps:
```jsx
// Good
<div className="p-6 gap-4">

// Avoid
<div style={{padding: "23px", gap: "17px"}}>
```

### 2. Semantic Colors
Use semantic colors for their intended purpose:
```jsx
// Good
<button className="bg-error-600">Delete</button>

// Avoid
<button className="bg-red-600">Delete</button>
```

### 3. Responsive Design
Use breakpoint prefixes for responsive behavior:
```jsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
```

### 4. Accessibility First
Always include proper focus states and ARIA labels:
```jsx
<button 
  className="btn-primary focus-visible-ring"
  aria-label="Submit form"
>
  Submit
</button>
```

### 5. Dark Mode Support
Test all components in both light and dark modes:
```jsx
<div className="bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100">
```

## Support

For questions, issues, or contributions, please refer to the project documentation.
"""
        return doc


# ============================================================================
# Main Tool Function
# ============================================================================

async def generate_design_system(params: GenerateDesignSystemInput) -> ToolResult:
    """Generate a complete design system with Tailwind config, CSS, and documentation"""
    
    try:
        project_path = Path(params.project_path)
        
        if not project_path.exists():
            return ToolResult(
                success=False,
                error=f"Project path does not exist: {params.project_path}"
            )
        
        # Initialize generator with design tokens
        tokens = DesignTokens()
        generator = DesignSystemGenerator(tokens)
        
        generated_files = []
        
        # 1. Generate Tailwind config
        tailwind_path = params.tailwind_config_path or str(project_path / "tailwind.config.js")
        tailwind_config = generator.generate_tailwind_config(params.include_dark_mode)
        
        with open(tailwind_path, 'w') as f:
            f.write(tailwind_config)
        generated_files.append(tailwind_path)
        
        # 2. Generate global CSS
        if params.css_output_path:
            css_path = params.css_output_path
        elif params.framework == "nextjs":
            css_path = str(project_path / "src" / "app" / "globals.css")
        else:
            css_path = str(project_path / "src" / "index.css")
        
        # Ensure directory exists
        css_dir = Path(css_path).parent
        css_dir.mkdir(parents=True, exist_ok=True)
        
        global_css = generator.generate_global_css(
            params.include_dark_mode,
            params.include_component_patterns
        )
        
        with open(css_path, 'w') as f:
            f.write(global_css)
        generated_files.append(css_path)
        
        # 3. Generate layout file (Next.js only)
        if params.include_layout and params.framework == "nextjs":
            layout_path = str(project_path / "src" / "app" / "layout.tsx")
            layout_dir = Path(layout_path).parent
            layout_dir.mkdir(parents=True, exist_ok=True)
            
            # Get relative path to globals.css
            layout_css_import = "./globals.css"
            
            layout_content = f"""import {layout_css_import!r}

export const metadata = {{
  title: 'Application',
  description: 'Built with AI Code Editor Design System'
}}

export default function RootLayout({{
  children,
}}: {{
  children: React.ReactNode
}}) {{
  return (
    <html lang="en">
      <body>{{children}}</body>
    </html>
  )
}}
"""
            
            with open(layout_path, 'w') as f:
                f.write(layout_content)
            generated_files.append(layout_path)
        
        # 4. Generate documentation
        if params.include_docs:
            docs_path = str(project_path / "DESIGN_SYSTEM.md")
            documentation = generator.generate_documentation()
            
            with open(docs_path, 'w') as f:
                f.write(documentation)
            generated_files.append(docs_path)
        
        # Build success message
        token_count = tokens.count_tokens()
        
        return ToolResult(
            success=True,
            data={
                "generated_files": generated_files,
                "token_count": token_count,
                "features": {
                    "dark_mode": params.include_dark_mode,
                    "component_patterns": params.include_component_patterns,
                    "documentation": params.include_docs,
                    "layout": params.include_layout and params.framework == "nextjs"
                },
                "summary": f"Generated professional design system with {token_count} design tokens"
            },
            metadata={
                "framework": params.framework,
                "files_created": len(generated_files)
            }
        )
        
    except Exception as e:
        return ToolResult(
            success=False,
            error=f"Failed to generate design system: {str(e)}"
        )


# ============================================================================
# Export
# ============================================================================

__all__ = [
    "GenerateDesignSystemInput",
    "DesignSystemGenerator",
    "generate_design_system"
]
