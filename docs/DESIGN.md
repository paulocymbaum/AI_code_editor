# Design Documentation - AI Code Editor

## Design System Overview

The AI Code Editor uses a comprehensive design token system to ensure visual consistency across all generated components. Every design decision is driven by configurable tokens that can be customized per project.

## Design Tokens

### Color Palette

#### Vibrant Theme (Default)
```json
{
  "colors": {
    "primary": {
      "50": "#f5f3ff",
      "100": "#ede9fe",
      "200": "#ddd6fe",
      "300": "#c4b5fd",
      "400": "#a78bfa",
      "500": "#8b5cf6",  // Primary brand color
      "600": "#7c3aed",
      "700": "#6d28d9",
      "800": "#5b21b6",
      "900": "#4c1d95"
    },
    "secondary": {
      "500": "#14b8a6",  // Teal accent
      "600": "#0d9488"
    },
    "accent": {
      "500": "#f97316",  // Orange highlight
      "600": "#ea580c"
    },
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",
    "background": {
      "primary": "#ffffff",
      "secondary": "#f9fafb",
      "tertiary": "#f3f4f6"
    },
    "text": {
      "primary": "#111827",
      "secondary": "#6b7280",
      "tertiary": "#9ca3af",
      "inverse": "#ffffff"
    },
    "border": {
      "light": "#e5e7eb",
      "default": "#d1d5db",
      "dark": "#9ca3af"
    }
  }
}
```

#### Dark Mode Support
```json
{
  "colors": {
    "background": {
      "primary": "#0f172a",
      "secondary": "#1e293b",
      "tertiary": "#334155"
    },
    "text": {
      "primary": "#f1f5f9",
      "secondary": "#cbd5e1",
      "tertiary": "#94a3b8"
    }
  }
}
```

### Typography

#### Font Families
```json
{
  "typography": {
    "fontFamily": {
      "sans": ["Inter", "system-ui", "sans-serif"],
      "serif": ["Merriweather", "Georgia", "serif"],
      "mono": ["Fira Code", "Courier New", "monospace"]
    }
  }
}
```

#### Font Sizes (Modular Scale 1.250)
```json
{
  "typography": {
    "fontSize": {
      "xs": "0.75rem",    // 12px
      "sm": "0.875rem",   // 14px
      "base": "1rem",     // 16px
      "lg": "1.125rem",   // 18px
      "xl": "1.25rem",    // 20px
      "2xl": "1.5rem",    // 24px
      "3xl": "1.875rem",  // 30px
      "4xl": "2.25rem",   // 36px
      "5xl": "3rem",      // 48px
      "6xl": "3.75rem"    // 60px
    },
    "fontWeight": {
      "light": 300,
      "normal": 400,
      "medium": 500,
      "semibold": 600,
      "bold": 700,
      "extrabold": 800
    },
    "lineHeight": {
      "none": 1,
      "tight": 1.25,
      "snug": 1.375,
      "normal": 1.5,
      "relaxed": 1.625,
      "loose": 2
    }
  }
}
```

### Spacing System (4px Base Unit)
```json
{
  "spacing": {
    "0": "0",
    "1": "0.25rem",  // 4px
    "2": "0.5rem",   // 8px
    "3": "0.75rem",  // 12px
    "4": "1rem",     // 16px
    "5": "1.25rem",  // 20px
    "6": "1.5rem",   // 24px
    "8": "2rem",     // 32px
    "10": "2.5rem",  // 40px
    "12": "3rem",    // 48px
    "16": "4rem",    // 64px
    "20": "5rem",    // 80px
    "24": "6rem"     // 96px
  }
}
```

### Border Radius
```json
{
  "borderRadius": {
    "none": "0",
    "sm": "0.125rem",   // 2px
    "base": "0.25rem",  // 4px
    "md": "0.375rem",   // 6px
    "lg": "0.5rem",     // 8px
    "xl": "0.75rem",    // 12px
    "2xl": "1rem",      // 16px
    "3xl": "1.5rem",    // 24px
    "full": "9999px"
  }
}
```

### Shadows
```json
{
  "shadows": {
    "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "base": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
    "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
    "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
    "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
    "inner": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)"
  }
}
```

## Component Patterns

### Pattern Catalog (13 Patterns)

#### 1. Card Pattern
**Use Case**: Content containers, product displays, info panels  
**HTML Structure**: `<div>` with shadow and rounded corners  
**Props**: title, content, footer  
**Responsive**: Stacks on mobile, grid on desktop

```tsx
<div className="bg-white rounded-lg shadow-md p-6">
  <h3 className="text-xl font-semibold mb-4">{title}</h3>
  <p className="text-gray-600">{content}</p>
  <div className="mt-4 pt-4 border-t">{footer}</div>
</div>
```

#### 2. Button Pattern
**Use Case**: CTAs, form submissions, navigation triggers  
**HTML Structure**: `<button>` with variants  
**Props**: label, variant (primary/secondary/outline), size  
**States**: hover, active, disabled, loading

```tsx
<button className="px-4 py-2 rounded-lg bg-primary-500 text-white hover:bg-primary-600">
  {label}
</button>
```

#### 3. Form Pattern
**Use Case**: User input, data collection, settings  
**HTML Structure**: `<form>` with labeled inputs  
**Props**: fields (array), onSubmit, validation  
**Accessibility**: Labels, error messages, ARIA attributes

```tsx
<form onSubmit={handleSubmit} className="space-y-4">
  <label className="block">
    <span className="text-gray-700">Email</span>
    <input type="email" className="mt-1 block w-full rounded-lg border-gray-300" />
  </label>
  <button type="submit" className="btn-primary">Submit</button>
</form>
```

#### 4. Modal Pattern
**Use Case**: Dialogs, confirmations, overlay content  
**HTML Structure**: `<div>` with backdrop overlay  
**Props**: isOpen, onClose, title, children  
**Behavior**: Focus trap, ESC to close, backdrop click closes

```tsx
<div className="fixed inset-0 bg-black/50 flex items-center justify-center">
  <div className="bg-white rounded-xl p-6 max-w-md w-full">
    <h2 className="text-2xl font-bold mb-4">{title}</h2>
    {children}
    <button onClick={onClose}>Close</button>
  </div>
</div>
```

#### 5. List Pattern
**Use Case**: Data tables, item lists, navigation menus  
**HTML Structure**: `<ul>` with styled `<li>` items  
**Props**: items (array), itemRenderer  
**Features**: Hover states, dividers, icons

```tsx
<ul className="divide-y divide-gray-200">
  {items.map(item => (
    <li key={item.id} className="px-4 py-3 hover:bg-gray-50">
      {item.label}
    </li>
  ))}
</ul>
```

#### 6. Hero Pattern
**Use Case**: Landing page headers, product intros  
**HTML Structure**: `<section>` with centered content  
**Props**: headline, subheadline, cta, image  
**Layout**: Full-width, centered, responsive image

```tsx
<section className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white py-20">
  <div className="container mx-auto px-4 text-center">
    <h1 className="text-5xl font-bold mb-4">{headline}</h1>
    <p className="text-xl mb-8">{subheadline}</p>
    <button className="btn-lg btn-white">{cta}</button>
  </div>
</section>
```

#### 7. Feature Pattern
**Use Case**: Product features, service highlights  
**HTML Structure**: Grid of feature cards with icons  
**Props**: features (array with icon, title, description)  
**Layout**: 1 col mobile, 2-3 cols desktop

```tsx
<div className="grid grid-cols-1 md:grid-cols-3 gap-8">
  {features.map(feature => (
    <div key={feature.id} className="text-center">
      <div className="text-4xl mb-4">{feature.icon}</div>
      <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
      <p className="text-gray-600">{feature.description}</p>
    </div>
  ))}
</div>
```

#### 8. Pricing Pattern
**Use Case**: Subscription plans, product tiers  
**HTML Structure**: Card-based pricing table  
**Props**: plans (array with name, price, features, cta)  
**Highlights**: Recommended plan with accent border

```tsx
<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
  {plans.map(plan => (
    <div className={`rounded-lg p-6 ${plan.featured ? 'border-4 border-primary-500' : 'border border-gray-200'}`}>
      <h3 className="text-2xl font-bold">{plan.name}</h3>
      <div className="text-4xl font-bold my-4">${plan.price}<span className="text-lg">/mo</span></div>
      <ul className="space-y-2 mb-6">
        {plan.features.map(feature => <li>✓ {feature}</li>)}
      </ul>
      <button className="btn-primary w-full">{plan.cta}</button>
    </div>
  ))}
</div>
```

#### 9. Sidebar Pattern ⭐ NEW
**Use Case**: Navigation panels, menu lists, user profiles  
**HTML Structure**: `<aside>` full-height with flex column  
**Props**: items (array), userInfo (object)  
**Responsive**: Hidden on mobile (toggle), visible on desktop

```tsx
<aside className="h-full bg-gray-900 text-white flex flex-col">
  <div className="p-4 border-b border-gray-800">
    <h2 className="text-xl font-bold">App Name</h2>
  </div>
  <nav className="flex-1 overflow-y-auto">
    {items.map(item => (
      <a href={item.href} className="flex items-center px-4 py-3 hover:bg-gray-800">
        <span className="mr-3">{item.icon}</span>
        <span>{item.label}</span>
      </a>
    ))}
  </nav>
  <div className="p-4 border-t border-gray-800">
    <div className="flex items-center">
      <img src={userInfo.avatar} className="w-10 h-10 rounded-full" />
      <div className="ml-3">
        <p className="font-medium">{userInfo.name}</p>
        <p className="text-sm text-gray-400">{userInfo.email}</p>
      </div>
    </div>
  </div>
</aside>
```

#### 10. Header Pattern ⭐ NEW
**Use Case**: Top navigation bars, app headers  
**HTML Structure**: `<header>` with flex layout  
**Props**: title, onMenuClick, search, notifications, userAvatar  
**Responsive**: Mobile menu toggle, hidden search on mobile

```tsx
<header className="bg-white border-b border-gray-200 px-4 py-3">
  <div className="flex items-center justify-between">
    <div className="flex items-center">
      <button onClick={onMenuClick} className="md:hidden mr-4">☰</button>
      <h1 className="text-xl font-bold">{title}</h1>
    </div>
    <div className="flex items-center gap-4">
      <input type="search" placeholder="Search..." className="hidden md:block px-4 py-2 rounded-lg border" />
      <button className="relative">
        <span>🔔</span>
        <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-4 h-4">3</span>
      </button>
      <img src={userAvatar} className="w-8 h-8 rounded-full" />
    </div>
  </div>
</header>
```

#### 11. Footer Pattern ⭐ NEW
**Use Case**: Bottom navigation, copyright, links  
**HTML Structure**: `<footer>` with responsive flex layout  
**Props**: links (array), copyright  
**Responsive**: Stacks on mobile, inline on desktop

```tsx
<footer className="bg-gray-900 text-white px-4 py-6">
  <div className="container mx-auto flex flex-col md:flex-row justify-between items-center">
    <p className="mb-4 md:mb-0">&copy; {year} {appName}</p>
    <nav className="flex gap-6">
      {links.map(link => (
        <a key={link.id} href={link.href} className="hover:text-primary-300">{link.label}</a>
      ))}
    </nav>
  </div>
</footer>
```

#### 12. Messages Pattern ⭐ NEW
**Use Case**: Chat interfaces, comment threads  
**HTML Structure**: `<div>` with flex column, messages alternate left/right  
**Props**: messages (array with sender, content, timestamp, isOwn)  
**Layout**: Own messages right-aligned, others left-aligned

```tsx
<div className="space-y-4">
  {messages.map(message => (
    <div key={message.id} className={`flex ${message.isOwn ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex gap-3 max-w-[70%] ${message.isOwn ? 'flex-row-reverse' : ''}`}>
        <img src={message.avatar} className="w-8 h-8 rounded-full" />
        <div>
          <div className={`rounded-lg px-4 py-2 ${message.isOwn ? 'bg-primary-500 text-white' : 'bg-gray-200'}`}>
            {message.content}
          </div>
          <p className="text-xs text-gray-500 mt-1">{message.timestamp}</p>
        </div>
      </div>
    </div>
  ))}
</div>
```

#### 13. Input Pattern ⭐ NEW
**Use Case**: Message inputs, comment forms, search bars  
**HTML Structure**: `<div>` with input field and action buttons  
**Props**: value, onChange, onSubmit, placeholder  
**Features**: Attachment button, emoji picker, send button

```tsx
<div className="border-t border-gray-200 px-4 py-3">
  <div className="flex items-center gap-2">
    <button className="text-gray-500 hover:text-gray-700">📎</button>
    <textarea
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className="flex-1 resize-none border-0 focus:ring-0"
      rows={1}
    />
    <button className="text-gray-500 hover:text-gray-700">😊</button>
    <button onClick={onSubmit} className="btn-primary">Send</button>
  </div>
</div>
```

## Responsive Layouts

### Layout Types (5)

#### 1. Grid Layout
**Use Case**: Product catalogs, image galleries, card grids  
**Breakpoints**:
- Mobile: 1 column
- Tablet: 2 columns
- Desktop: 3-4 columns

```tsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>
```

#### 2. Chat Layout
**Use Case**: Messaging apps, customer support interfaces  
**Structure**: Sidebar + Header + Messages + Input + Footer  
**Breakpoints**:
- Mobile: Stacked, collapsible sidebar
- Desktop: Fixed sidebar (250px), flex content area

```tsx
<div className="flex h-screen">
  <aside className="hidden md:flex md:w-64">{/* Sidebar */}</aside>
  <div className="flex-1 flex flex-col">
    <header>{/* ChatHeader */}</header>
    <main className="flex-1 overflow-y-auto">{/* ChatMessageList */}</main>
    <div>{/* ChatInput */}</div>
    <footer>{/* ChatFooter */}</footer>
  </div>
</div>
```

#### 3. Dashboard Layout
**Use Case**: Admin panels, analytics dashboards  
**Structure**: Sidebar + Header + Grid of cards/charts  
**Breakpoints**:
- Mobile: Single column, hamburger menu
- Desktop: Fixed sidebar, 2-3 column grid

```tsx
<div className="flex">
  <aside className="w-64">{/* DashboardSidebar */}</aside>
  <div className="flex-1">
    <header>{/* DashboardHeader */}</header>
    <main className="p-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {widgets.map(widget => <Card key={widget.id} {...widget} />)}
      </div>
    </main>
  </div>
</div>
```

#### 4. Landing Layout
**Use Case**: Marketing websites, product pages  
**Structure**: Hero + Features + Pricing + Footer  
**Breakpoints**: Fully responsive, stacks on mobile

```tsx
<div>
  <HeroSection />
  <FeatureSection />
  <PricingSection />
  <FooterSection />
</div>
```

#### 5. App Layout
**Use Case**: Complex applications, multi-view apps  
**Structure**: Flexible, customizable component arrangement  
**Breakpoints**: Configurable per project needs

## Responsive Design Principles

### Mobile-First Approach
All patterns default to mobile layout, then progressively enhance for larger screens using Tailwind breakpoints.

### Breakpoint Strategy
```css
/* Tailwind breakpoints */
sm: 640px   /* Tablet portrait */
md: 768px   /* Tablet landscape */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
2xl: 1536px /* Extra large */
```

### Touch Targets
- Minimum 44x44px for buttons/links (mobile)
- 16px minimum font size (prevent zoom on iOS)
- Adequate spacing between interactive elements

### Performance
- Mobile images: Optimize for <200KB
- Desktop images: Optimize for <500KB
- Use `loading="lazy"` for below-the-fold content
- Serve responsive images with `srcset`

## Pattern Selection Guidelines

### When to Use Each Pattern

| Pattern | Best For | NOT For |
|---------|----------|---------|
| Card | Content blocks, product displays | Full-page layouts |
| Button | Actions, CTAs | Navigation links (use <a>) |
| Form | User input, data collection | Display-only content |
| Modal | Confirmations, temporary dialogs | Permanent content |
| List | Repeating items, navigation | Single items |
| Hero | Landing page headers | Internal pages |
| Feature | Product highlights | Detailed documentation |
| Pricing | Subscription tiers | Single products |
| Sidebar | Navigation panels | Temporary menus |
| Header | Top bars, app navigation | Section headers |
| Footer | Bottom navigation, copyright | Content footers |
| Messages | Chat bubbles, comments | Single messages |
| Input | Message entry, inline forms | Long forms |

### Common Mistakes ❌

1. **Using Card for Sidebar** ❌ → Use Sidebar pattern ✅
2. **Using Modal for Header** ❌ → Use Header pattern ✅
3. **Using List for Chat Messages** ❌ → Use Messages pattern ✅
4. **Using Form for Message Input** ❌ → Use Input pattern ✅
5. **Defaulting to Card when pattern is missing** ❌ → Pattern is REQUIRED ✅

## Accessibility Guidelines

### WCAG 2.1 AA Compliance

#### Color Contrast
- Normal text: 4.5:1 minimum
- Large text (18px+): 3:1 minimum
- Interactive elements: Clear focus indicators

#### Keyboard Navigation
- All interactive elements reachable via Tab
- Modal focus trap (Tab stays in modal)
- ESC to close modals/dropdowns
- Enter/Space to activate buttons

#### Screen Readers
- Semantic HTML (`<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>`)
- ARIA labels for icon buttons
- Alt text for images
- Form labels for inputs

#### Focus Management
```tsx
// Modal focus trap
useEffect(() => {
  if (isOpen) {
    const firstFocusable = modalRef.current.querySelector('button, [href], input');
    firstFocusable?.focus();
  }
}, [isOpen]);
```

## Design System Configuration

### JSON Configuration Example
```json
{
  "name": "MyAppDesignSystem",
  "theme": "vibrant",
  "tokens": {
    "colors": { /* color palette */ },
    "typography": { /* font settings */ },
    "spacing": { /* spacing scale */ }
  },
  "components": {
    "card": {
      "defaultShadow": "md",
      "defaultRadius": "lg"
    },
    "button": {
      "defaultSize": "md",
      "defaultVariant": "primary"
    }
  }
}
```

### Customization Workflow
1. Create `design-system.json` in project root
2. Override default tokens as needed
3. Run `generate_design_system` tool
4. Tailwind config auto-generated
5. All components inherit new tokens

## CSS Architecture

### Tailwind CSS Integration
All generated components use Tailwind utility classes for:
- Rapid iteration
- Consistent spacing/colors
- Responsive modifiers
- Dark mode support

### Custom CSS (When Needed)
```css
/* globals.css */
@layer components {
  .btn-primary {
    @apply px-4 py-2 rounded-lg bg-primary-500 text-white hover:bg-primary-600;
  }
}
```

### CSS Modules (Optional)
```tsx
import styles from './Card.module.css';

<div className={styles.container}>
  {/* Component content */}
</div>
```

## Design System Status

### Completed ✅
- ✅ Design token system (colors, typography, spacing, shadows)
- ✅ 13 component patterns with responsive templates
- ✅ 5 layout types with mobile-first approach
- ✅ Tailwind CSS integration
- ✅ Pattern selection guidelines
- ✅ Semantic HTML enforcement

### In Progress 🚧
- 🚧 Dark mode theme variants
- 🚧 Animation system (transitions, keyframes)
- 🚧 Accessibility testing automation
- 🚧 Icon library integration

### Planned 📋
- 📋 Design system documentation site
- 📋 Figma plugin for token sync
- 📋 Component playground/sandbox
- 📋 Visual regression testing

## Conclusion

The AI Code Editor design system enforces consistent, accessible, and responsive UI patterns across all generated code. The **pattern system overhaul** ensures components are semantic and appropriate (sidebar for navigation, header for top bars, messages for chat, etc.) instead of defaulting to generic cards.

**Key Achievement**: Made `pattern` field REQUIRED to prevent generic defaults and enforce semantic HTML.

---

**Last Updated**: January 2025  
**Document Owner**: Design Team  
**Review Cycle**: Quarterly
