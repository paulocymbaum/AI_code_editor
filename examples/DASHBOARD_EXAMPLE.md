# Complex Dashboard Example with Redux State Management

This example demonstrates how to use the AI Code Editor agent to create a sophisticated admin dashboard with Redux state management, animations, and complex UI interactions.

## 🎯 Overview

The dashboard example generates a complete, production-ready admin interface with:

- **Redux State Management**: Centralized state for UI and data
- **Animated Sidebar**: Smooth collapse/expand transitions
- **Tab Navigation**: Multiple views with state persistence
- **Responsive Design**: Mobile-first with breakpoint adaptations
- **TypeScript**: Full type safety throughout
- **Accessibility**: ARIA labels and keyboard navigation
- **Dark Mode Ready**: Theme switching capability

## 📦 What Gets Generated

### Redux Store Structure

```
demo/src/
├── store/
│   ├── store.ts              # Redux store configuration
│   └── slices/
│       ├── uiSlice.ts        # UI state (menu, tabs, theme)
│       └── dashboardSlice.ts # Dashboard data
```

**uiSlice.ts** manages:
- `menuCollapsed: boolean` - Sidebar collapsed state
- `activeTab: string` - Current active tab
- `theme: 'light' | 'dark'` - Theme preference

**dashboardSlice.ts** manages:
- `stats` - Dashboard statistics
- `recentActivity` - Activity feed data

### React Components

```
demo/src/components/
├── DashboardLayout.tsx   # Main layout wrapper
├── Sidebar.tsx           # Animated collapsible sidebar
├── TopBar.tsx           # Header with controls
├── TabNavigation.tsx    # Tab switching UI
├── TabContent.tsx       # Dynamic content renderer
└── StatsCard.tsx        # Reusable stat display
```

### Page

```
demo/src/app/dashboard/page.tsx  # Dashboard page entry point
```

## 🚀 Quick Start

### Step 1: Set up environment

```bash
# Ensure GROQ_API_KEY is set
export GROQ_API_KEY='your-groq-api-key-here'
```

### Step 2: Run the example

```bash
# From project root
cd /path/to/AI_code_editor

# Run the dashboard generator
python examples/dashboard_example.py
```

### Step 3: Choose generation mode

```
1. Full Dashboard with Redux (Complex - Recommended)
   → Generates complete dashboard with full Redux setup
   
2. Simple Dashboard Demo (Quick test without Redux)
   → Simpler version using React useState
   
3. Add Advanced Features to Existing Dashboard
   → Enhances existing dashboard with search, notifications, etc.
```

### Step 4: Install dependencies

```bash
cd demo

# Install required packages
npm install @reduxjs/toolkit react-redux lucide-react

# If using animations
npm install framer-motion  # Optional
```

### Step 5: Run the development server

```bash
npm run dev

# Open browser
open http://localhost:3000/dashboard
```

## 🎨 Features Walkthrough

### 1. Collapsible Sidebar

**State Management:**
```typescript
// uiSlice.ts
const uiSlice = createSlice({
  name: 'ui',
  initialState: { menuCollapsed: false },
  reducers: {
    toggleMenu: (state) => {
      state.menuCollapsed = !state.menuCollapsed;
    }
  }
});
```

**Component:**
```typescript
// Sidebar.tsx
const Sidebar: React.FC = () => {
  const menuCollapsed = useSelector((state: RootState) => state.ui.menuCollapsed);
  const dispatch = useDispatch();
  
  return (
    <aside className={`
      transition-all duration-300 ease-in-out
      ${menuCollapsed ? 'w-16' : 'w-60'}
    `}>
      {/* Menu items */}
    </aside>
  );
};
```

**Animations:**
- Width transition: `240px → 64px`
- Label fade: opacity animation
- Icon rotation: subtle hover effects
- Duration: `300ms` with `ease-in-out`

### 2. Tab Navigation

**State Management:**
```typescript
// uiSlice.ts
const uiSlice = createSlice({
  name: 'ui',
  initialState: { activeTab: 'overview' },
  reducers: {
    setActiveTab: (state, action) => {
      state.activeTab = action.payload;
    }
  }
});
```

**Component:**
```typescript
// TabNavigation.tsx
const TabNavigation: React.FC = () => {
  const activeTab = useSelector((state: RootState) => state.ui.activeTab);
  const dispatch = useDispatch();
  
  const tabs = ['overview', 'analytics', 'settings', 'users'];
  
  return (
    <nav>
      {tabs.map(tab => (
        <button
          key={tab}
          onClick={() => dispatch(setActiveTab(tab))}
          className={activeTab === tab ? 'active' : ''}
        >
          {tab}
        </button>
      ))}
    </nav>
  );
};
```

**Animations:**
- Active indicator slide: smooth underline transition
- Content fade: fade out → fade in on tab change
- Hover effects: background color fade

### 3. Dynamic Content Rendering

```typescript
// TabContent.tsx
const TabContent: React.FC = () => {
  const activeTab = useSelector((state: RootState) => state.ui.activeTab);
  const stats = useSelector((state: RootState) => state.dashboard.stats);
  
  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewTab stats={stats} />;
      case 'analytics':
        return <AnalyticsTab />;
      case 'settings':
        return <SettingsTab />;
      case 'users':
        return <UsersTab />;
      default:
        return null;
    }
  };
  
  return (
    <div className="animate-fade-in">
      {renderContent()}
    </div>
  );
};
```

## 🎭 Animation Specifications

### Sidebar Collapse/Expand
```css
transition: width 300ms ease-in-out;

/* Expanded */
width: 240px;

/* Collapsed */
width: 64px;
```

### Tab Indicator Slide
```css
transition: transform 300ms ease-in-out;
transform: translateX(var(--tab-offset));
```

### Content Fade
```css
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

animation: fadeIn 300ms ease-out;
```

### Hover Effects
```css
/* Menu items */
transition: background-color 200ms ease;

/* Stats cards */
transition: transform 200ms ease, box-shadow 200ms ease;
transform: translateY(-4px);
box-shadow: 0 8px 16px rgba(0,0,0,0.1);
```

## 📱 Responsive Behavior

### Breakpoints

```typescript
// Tailwind breakpoints
sm: '640px'   // Phone landscape
md: '768px'   // Tablet
lg: '1024px'  // Desktop
xl: '1280px'  // Large desktop
```

### Responsive Rules

**Mobile (< 768px):**
- Sidebar auto-collapsed
- Overlay menu (absolute positioning)
- Tab navigation scrollable
- Single column layout

**Tablet (768px - 1024px):**
- Sidebar collapsible
- Two column layout
- Tab navigation full width

**Desktop (> 1024px):**
- Sidebar expanded by default
- Three column layout
- All features visible

## 🔧 Customization

### Changing Colors

Edit `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        500: '#3b82f6', // Change to your brand color
        600: '#2563eb',
      }
    }
  }
}
```

### Adding New Tabs

1. Update `uiSlice.ts`:
```typescript
type TabType = 'overview' | 'analytics' | 'settings' | 'users' | 'reports'; // Add 'reports'
```

2. Update `TabNavigation.tsx`:
```typescript
const tabs = ['overview', 'analytics', 'settings', 'users', 'reports'];
```

3. Update `TabContent.tsx`:
```typescript
case 'reports':
  return <ReportsTab />;
```

### Modifying Animations

Adjust duration in Tailwind classes:

```typescript
// Slower transition
className="transition-all duration-500 ease-in-out"

// Faster transition
className="transition-all duration-150 ease-in-out"
```

## 🧪 Testing Redux State

### Using Redux DevTools

1. Install browser extension:
   - [Chrome](https://chrome.google.com/webstore/detail/redux-devtools/)
   - [Firefox](https://addons.mozilla.org/en-US/firefox/addon/reduxdevtools/)

2. Open DevTools in browser
3. Navigate to Redux tab
4. Monitor state changes in real-time

### Manual Testing

```typescript
// In browser console
// Access store (if exposed)
window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__

// Dispatch actions
store.dispatch({ type: 'ui/toggleMenu' })
store.dispatch({ type: 'ui/setActiveTab', payload: 'analytics' })
```

## 📊 Performance Optimization

### Memoization

```typescript
import { memo } from 'react';

// Memoize expensive components
export const StatsCard = memo(({ title, value, change }: Props) => {
  // Component logic
});
```

### Selector Optimization

```typescript
import { createSelector } from '@reduxjs/toolkit';

// Memoized selector
const selectActiveTabData = createSelector(
  [(state: RootState) => state.ui.activeTab,
   (state: RootState) => state.dashboard.stats],
  (activeTab, stats) => {
    // Compute derived data
    return { activeTab, stats };
  }
);
```

## 🐛 Troubleshooting

### Common Issues

**1. Redux store not found**
```
Error: could not find react-redux context value
```
Solution: Ensure Provider wraps the app in `app/layout.tsx`:
```typescript
import { Provider } from 'react-redux';
import { store } from '@/store/store';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <Provider store={store}>
          {children}
        </Provider>
      </body>
    </html>
  );
}
```

**2. Animations not smooth**
```
Sidebar transition is janky
```
Solution: Ensure GPU acceleration:
```css
transform: translateZ(0);
will-change: width;
```

**3. TypeScript errors**
```
Property 'ui' does not exist on type 'RootState'
```
Solution: Export RootState type:
```typescript
// store/store.ts
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

## 🔍 Code Examples

### Complete Redux Setup

```typescript
// store/store.ts
import { configureStore } from '@reduxjs/toolkit';
import uiReducer from './slices/uiSlice';
import dashboardReducer from './slices/dashboardSlice';

export const store = configureStore({
  reducer: {
    ui: uiReducer,
    dashboard: dashboardReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

### Custom Hooks

```typescript
// hooks/redux.ts
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from '@/store/store';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
```

## 🎓 Learning Resources

- [Redux Toolkit Docs](https://redux-toolkit.js.org/)
- [React-Redux Hooks](https://react-redux.js.org/api/hooks)
- [Tailwind CSS Animations](https://tailwindcss.com/docs/animation)
- [TypeScript with Redux](https://redux.js.org/usage/usage-with-typescript)

## 📝 Next Steps

After generating the dashboard, consider adding:

1. **Authentication**
   - Login/logout functionality
   - Protected routes
   - User session management

2. **Data Fetching**
   - API integration
   - Loading states
   - Error handling

3. **Advanced Features**
   - Search functionality
   - Notifications system
   - Keyboard shortcuts
   - Export/import data

4. **Testing**
   - Unit tests for Redux slices
   - Component tests with React Testing Library
   - E2E tests with Playwright

## 🤝 Contributing

To extend this example:

1. Fork the repository
2. Create your feature branch
3. Add new dashboard features
4. Submit a pull request

## 📄 License

MIT License - See main project LICENSE file

---

**Created with AI Code Editor Agent** 🤖  
**Last Updated:** December 2025  
**Version:** 1.0
