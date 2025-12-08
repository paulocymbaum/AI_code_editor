# React/TypeScript Code Generation Guide

## Overview

This AI coding agent is specifically designed to generate **React**, **TypeScript**, **JavaScript**, and **Next.js** code. It provides intelligent code generation, refactoring, and project scaffolding capabilities.

## Key Features for React Development

### 1. React Component Generation

Generate functional or class components with:
- TypeScript support
- Props interfaces
- React hooks (useState, useEffect, useContext, etc.)
- Multiple styling options (CSS Modules, Styled Components, Tailwind)
- Proper file structure

**Example:**
```python
result = await agent.execute(
    """
    Create a React TypeScript component called 'ProductCard' that:
    - Takes props: product (object with name, price, image, description)
    - Uses useState for managing quantity
    - Has an 'Add to Cart' button
    - Uses Tailwind CSS for styling
    """
)
```

### 2. Next.js Application Development

Build complete Next.js applications with:
- App Router (Next.js 13+) or Pages Router
- Server-side rendering (SSR)
- Static site generation (SSG)
- Incremental static regeneration (ISR)
- API routes
- Layouts and templates
- Middleware

**Example:**
```python
result = await agent.execute(
    """
    Create a Next.js 14 e-commerce site with:
    - Home page with product grid (SSG)
    - Product detail pages with dynamic routes
    - Shopping cart with Zustand
    - Checkout page
    - Admin dashboard
    - API routes for products and orders
    """
)
```

### 3. API Route Generation

Create backend API routes for:
- Next.js App Router
- Next.js Pages Router
- Express.js
- Fastify

**Example:**
```python
result = await agent.execute(
    """
    Create REST API for user management:
    - POST /api/users - Create user
    - GET /api/users - List users
    - GET /api/users/[id] - Get user
    - PUT /api/users/[id] - Update user
    - DELETE /api/users/[id] - Delete user
    
    Include validation, error handling, and TypeScript types
    """
)
```

### 4. TypeScript Type Generation

Automatically generate TypeScript types from:
- API responses
- JSON data
- Database schemas
- GraphQL schemas

**Example:**
```python
result = await agent.execute(
    """
    Generate TypeScript types for this API response:
    {
      "user": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "posts": [
          {"id": 1, "title": "Hello", "published": true}
        ]
      }
    }
    """
)
```

### 5. Custom Hooks Creation

Generate reusable custom React hooks:
- Data fetching hooks
- Form handling hooks
- State management hooks
- Utility hooks

**Example:**
```python
result = await agent.execute(
    """
    Create a custom hook 'useApi' that:
    - Accepts a URL and options
    - Manages loading, error, and data states
    - Supports automatic retries
    - Includes TypeScript generics for type safety
    - Has abort controller for cleanup
    """
)
```

### 6. State Management Setup

Set up state management with:
- Zustand
- Redux Toolkit
- Jotai
- React Context

**Example:**
```python
result = await agent.execute(
    """
    Set up Zustand store for authentication:
    - User state (user object, isAuthenticated)
    - Actions: login, logout, updateProfile
    - Persist to localStorage
    - TypeScript interfaces
    - Middleware for logging
    """
)
```

### 7. Form Components with Validation

Create forms with:
- React Hook Form
- Zod validation
- Error handling
- Accessibility features

**Example:**
```python
result = await agent.execute(
    """
    Create a contact form with:
    - Fields: name, email, subject, message
    - Zod schema validation
    - React Hook Form
    - Show inline errors
    - Submit to API endpoint
    - Loading and success states
    """
)
```

### 8. Testing

Generate tests with:
- Jest
- React Testing Library
- Vitest
- Playwright (E2E)

**Example:**
```python
result = await agent.execute(
    """
    Generate comprehensive tests for LoginForm component:
    - Test form rendering
    - Test validation errors
    - Test successful submission
    - Test API error handling
    - Test accessibility
    """
)
```

## Common Use Cases

### Use Case 1: Create a New Feature

```python
result = await agent.execute(
    """
    Create a blog feature with:
    1. BlogList component showing all posts
    2. BlogPost component for single post
    3. BlogEditor component for creating/editing
    4. API routes for CRUD operations
    5. Zustand store for blog state
    6. TypeScript types for all entities
    7. Tests for components
    """
)
```

### Use Case 2: Refactor to TypeScript

```python
result = await agent.execute(
    """
    Refactor the entire src/components folder to TypeScript:
    1. Rename all .jsx files to .tsx
    2. Add proper type definitions
    3. Fix any type errors
    4. Run TypeScript compiler to verify
    5. Update imports if needed
    """
)
```

### Use Case 3: Add Authentication

```python
result = await agent.execute(
    """
    Add authentication to the app:
    1. Create auth context with login/logout
    2. Protected route wrapper component
    3. Login and signup forms
    4. API routes for auth
    5. JWT token management
    6. Persist auth state
    7. Redirect logic
    """
)
```

### Use Case 4: Build a Dashboard

```python
result = await agent.execute(
    """
    Create an admin dashboard with:
    1. Sidebar navigation
    2. Stats cards with metrics
    3. Charts using Recharts
    4. Data tables with sorting/filtering
    5. Dark mode toggle
    6. Responsive design
    7. API integration
    """
)
```

### Use Case 5: Optimize Performance

```python
result = await agent.execute(
    """
    Optimize the app for performance:
    1. Add React.memo to expensive components
    2. Implement code splitting with dynamic imports
    3. Add image optimization with next/image
    4. Implement virtual scrolling for long lists
    5. Add loading skeletons
    6. Optimize bundle size
    """
)
```

## Tool Reference

### React Component Tools

#### `generate_react_component`
Generates React components with full TypeScript support.

**Parameters:**
- `component_name`: Component name (PascalCase)
- `component_type`: "functional" or "class"
- `use_typescript`: true/false
- `props`: Array of prop definitions
- `hooks`: Array of React hooks to use
- `styling`: "css-modules", "styled-components", or "tailwind"
- `output_dir`: Output directory path

#### `generate_nextjs_page`
Creates Next.js pages with data fetching.

**Parameters:**
- `page_name`: Page name (kebab-case)
- `route`: Route path
- `use_typescript`: true/false
- `data_fetching`: "SSR", "SSG", "ISR", or "CSR"
- `layout`: Layout component to use
- `output_dir`: Output directory

#### `generate_api_route`
Creates API route handlers.

**Parameters:**
- `route_name`: API route name
- `method`: HTTP method (GET, POST, PUT, DELETE)
- `use_typescript`: true/false
- `framework`: "nextjs", "express", or "fastify"
- `output_dir`: Output directory

### Code Quality Tools

#### `typescript_check`
Runs TypeScript type checking.

**Parameters:**
- `file_path`: Specific file or null for all
- `project_root`: Project root directory
- `strict`: Enable strict mode

#### `eslint_check`
Runs ESLint with optional auto-fix.

**Parameters:**
- `file_path`: Specific file or null for all
- `fix`: Auto-fix issues
- `project_root`: Project root directory

#### `prettier_format`
Formats code with Prettier.

**Parameters:**
- `file_path`: File to format
- `write`: Write changes to file

### Package Management

#### `npm_command`
Executes NPM commands.

**Parameters:**
- `command`: NPM command (install, run, test, build)
- `args`: Additional arguments
- `working_dir`: Working directory

### Type Generation

#### `generate_type_definitions`
Generates TypeScript types from JSON.

**Parameters:**
- `source`: JSON source data
- `type_name`: Name for the type/interface
- `output_file`: Output file path

## Best Practices

### 1. Always Use TypeScript
```python
# Good
result = await agent.execute(
    "Create a UserProfile component with TypeScript"
)

# Better - Be specific about types
result = await agent.execute(
    """
    Create a UserProfile component with:
    - TypeScript interface for User type
    - Props: user (User), onEdit (function)
    - Proper return type annotations
    """
)
```

### 2. Specify Styling Approach
```python
result = await agent.execute(
    """
    Create a Button component using Tailwind CSS with:
    - Variants: primary, secondary, danger
    - Sizes: sm, md, lg
    - Loading state
    - Disabled state
    """
)
```

### 3. Include Error Handling
```python
result = await agent.execute(
    """
    Create an API route with:
    - Try-catch error handling
    - Proper HTTP status codes
    - Error response format
    - Input validation
    """
)
```

### 4. Request Tests
```python
result = await agent.execute(
    """
    Create a SearchBar component and include:
    - Component implementation
    - Jest + RTL tests
    - Test user interactions
    - Test debouncing
    """
)
```

### 5. Be Specific About Data Fetching
```python
result = await agent.execute(
    """
    Create a ProductsPage with:
    - Server-side rendering (SSR)
    - Fetch products from API
    - Loading state
    - Error boundary
    - SEO metadata
    """
)
```

## Project Setup

### Initialize a New Project

```python
result = await agent.execute(
    """
    Set up a new Next.js 14 project:
    1. Initialize with create-next-app (TypeScript, App Router, Tailwind)
    2. Install: zustand, react-hook-form, zod, axios, lucide-react
    3. Configure ESLint and Prettier
    4. Set up folder structure:
       - app/ (routes)
       - components/ (reusable components)
       - lib/ (utilities)
       - hooks/ (custom hooks)
       - types/ (TypeScript types)
       - stores/ (Zustand stores)
    5. Create tsconfig paths
    6. Add .env.example
    7. Set up global styles
    """
)
```

## Tips for Better Results

1. **Be Specific**: The more details you provide, the better the generated code
2. **Mention Dependencies**: Specify libraries you want to use (e.g., "using Zod for validation")
3. **Request TypeScript**: Always specify TypeScript for type safety
4. **Include Context**: Mention the broader application context
5. **Ask for Tests**: Request tests alongside component generation
6. **Specify Patterns**: Mention design patterns (e.g., "using compound component pattern")

## Troubleshooting

### Issue: Generated code has type errors
**Solution:** Run `typescript_check` tool and ask agent to fix errors

### Issue: Code doesn't follow project conventions
**Solution:** Provide more context about your project structure and conventions

### Issue: Missing dependencies
**Solution:** Use `npm_command` tool to install required packages

### Issue: Styling not working
**Solution:** Specify the exact styling approach (Tailwind, CSS Modules, etc.)

## Next Steps

1. Try the examples in `examples/react_examples.py`
2. Read the main `README.md` for setup instructions
3. Check `SYSTEM_DESIGN.md` for architecture details
4. Explore the tool implementations in `tools/javascript_tools.py`

## Support

For issues or questions about React/TypeScript code generation, refer to:
- Tool documentation in `tools/javascript_tools.py`
- Example usage in `examples/react_examples.py`
- System design in `SYSTEM_DESIGN.md`
