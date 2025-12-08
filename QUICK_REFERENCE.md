# Quick Reference - React/TypeScript Code Generation

## Common Commands

### Create React Component
```python
agent.execute("Create a Button component with TypeScript, variants (primary/secondary), and Tailwind CSS")
```

### Create Next.js Page
```python
agent.execute("Create a Next.js about page with SSG and TypeScript")
```

### Generate API Route
```python
agent.execute("Create a POST /api/users API route with validation using Zod")
```

### Setup Project
```python
agent.execute("Initialize a Next.js 14 project with TypeScript, Tailwind, and ESLint")
```

### Add Feature
```python
agent.execute("Add authentication with login/signup forms, JWT, and protected routes")
```

### Generate Tests
```python
agent.execute("Generate Jest tests for the UserCard component")
```

### Refactor Code
```python
agent.execute("Refactor all components in src/components to use TypeScript")
```

### Fix Issues
```python
agent.execute("Fix all TypeScript errors in the project")
```

## Component Patterns

### Functional Component with Props
```
Create a {ComponentName} component with:
- TypeScript interface for props
- Props: {list props and types}
- {Describe functionality}
- Use {styling approach}
```

### Component with Hooks
```
Create a {ComponentName} component using:
- useState for {state description}
- useEffect for {effect description}
- {Other hooks}
- TypeScript throughout
```

### Form Component
```
Create a {FormName} form with:
- Fields: {list fields}
- React Hook Form
- Zod validation
- Error handling
- Submit to {endpoint}
```

### Custom Hook
```
Create a custom hook 'use{HookName}' that:
- {Describe functionality}
- Returns {what it returns}
- TypeScript generics
- Proper cleanup
```

## Next.js Patterns

### Page with SSR
```
Create a {PageName} page with:
- Server-side rendering
- Fetch data from {source}
- TypeScript
- SEO metadata
```

### Page with SSG
```
Create a {PageName} page with:
- Static generation
- getStaticProps
- Revalidate every {time}
- TypeScript
```

### Dynamic Route
```
Create a dynamic route /blog/[slug] with:
- getStaticPaths
- getStaticProps
- Fetch from {source}
- TypeScript
```

### API Route
```
Create {METHOD} /api/{route} that:
- {Describe functionality}
- Validate input with Zod
- Error handling
- TypeScript
```

## State Management

### Zustand Store
```
Create a Zustand store for {feature}:
- State: {list state}
- Actions: {list actions}
- Persist to localStorage
- TypeScript interfaces
```

### Context Provider
```
Create a {Context}Provider with:
- State: {list state}
- Actions: {list actions}
- TypeScript
- Custom hook for consumption
```

## Styling Approaches

### Tailwind CSS
```
Create a {Component} using Tailwind CSS with:
- {Describe styling}
- Responsive design
- Dark mode support
```

### CSS Modules
```
Create a {Component} with CSS Modules:
- {Describe styling}
- Scoped styles
- TypeScript
```

### Styled Components
```
Create a {Component} using Styled Components:
- {Describe styling}
- Theme support
- TypeScript
```

## Testing Patterns

### Component Tests
```
Generate tests for {Component}:
- Test rendering
- Test user interactions
- Test props
- Test edge cases
- Use React Testing Library
```

### Hook Tests
```
Generate tests for use{Hook}:
- Test initial state
- Test state updates
- Test side effects
- Use @testing-library/react-hooks
```

### API Tests
```
Generate tests for /api/{route}:
- Test successful requests
- Test validation errors
- Test error handling
- Use supertest
```

## Project Setup

### New Next.js Project
```
Set up a new Next.js 14 project with:
- TypeScript
- App Router
- Tailwind CSS
- ESLint + Prettier
- Folder structure
- Path aliases
```

### Add Dependencies
```
Install and configure:
- {library1}
- {library2}
- {library3}
Update package.json and configs
```

### Setup Linting
```
Configure ESLint and Prettier with:
- TypeScript support
- React rules
- Import sorting
- Tailwind plugin
```

## Code Quality

### Type Check
```
Run TypeScript type checking on the entire project and fix any errors
```

### Lint and Fix
```
Run ESLint on all files and auto-fix issues
```

### Format Code
```
Format all files with Prettier
```

## Common Requests

### Authentication
```
Add authentication with:
- Login/signup forms
- JWT tokens
- Protected routes
- Auth context
- API routes
```

### CRUD Operations
```
Create CRUD for {entity}:
- List view
- Detail view
- Create form
- Edit form
- Delete confirmation
- API routes
- State management
```

### Dashboard
```
Create a dashboard with:
- Layout (sidebar, header)
- Stats cards
- Charts
- Data tables
- Responsive design
```

### Search Feature
```
Add search functionality:
- Search input with debounce
- Filter results
- Display results
- API integration
```

### Pagination
```
Add pagination to {component}:
- Page controls
- Items per page
- API integration
- Loading states
```

## Tips for Better Results

1. **Be Specific**: Mention exact libraries, patterns, and requirements
2. **Include Types**: Always request TypeScript with proper types
3. **Specify Styling**: Mention Tailwind, CSS Modules, or Styled Components
4. **Request Tests**: Ask for tests alongside components
5. **Mention Framework**: Specify Next.js version and router type
6. **Add Context**: Explain how the code fits into your app
7. **List Dependencies**: Mention libraries you want to use
8. **Request Validation**: Ask for Zod or other validation
9. **Include Error Handling**: Request proper error handling
10. **Ask for Accessibility**: Mention a11y requirements

## Example: Complete Feature Request

```python
result = await agent.execute(
    """
    Create a blog feature with:
    
    Components:
    - BlogList: Display posts in a grid, pagination, search
    - BlogPost: Single post view with comments
    - BlogEditor: Create/edit posts with rich text editor
    - CommentSection: Display and add comments
    
    Pages (Next.js App Router):
    - /blog - List all posts (SSG with ISR)
    - /blog/[slug] - Single post (SSG)
    - /blog/new - Create post (protected)
    - /blog/edit/[id] - Edit post (protected)
    
    API Routes:
    - GET /api/posts - List posts
    - GET /api/posts/[id] - Get post
    - POST /api/posts - Create post
    - PUT /api/posts/[id] - Update post
    - DELETE /api/posts/[id] - Delete post
    - POST /api/posts/[id]/comments - Add comment
    
    State Management:
    - Zustand store for blog state
    - Actions for CRUD operations
    
    Features:
    - TypeScript throughout
    - Zod validation
    - Error handling
    - Loading states
    - Tailwind CSS
    - Responsive design
    - SEO optimization
    - Tests for components
    
    Authentication:
    - Protected routes for create/edit
    - User context
    """
)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Type errors | `agent.execute("Run TypeScript check and fix all errors")` |
| Lint errors | `agent.execute("Run ESLint with auto-fix")` |
| Missing deps | `agent.execute("Install {package} and configure")` |
| Styling issues | Be more specific about styling approach |
| Wrong pattern | Provide example or reference |
| Incomplete code | Ask for specific missing parts |

## Resources

- **REACT_GUIDE.md** - Comprehensive React/TS guide
- **examples/react_examples.py** - Working examples
- **tools/javascript_tools.py** - Tool implementations
- **SYSTEM_DESIGN.md** - Architecture details
