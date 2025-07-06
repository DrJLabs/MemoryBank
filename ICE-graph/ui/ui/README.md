# 🎨 OpenMemory UI Dashboard

**Modern Next.js 15 + React 19 + TypeScript Dashboard for Memory Management**

[![Next.js](https://img.shields.io/badge/Next.js-15.2.4-black.svg)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-19.0-blue.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://typescriptlang.org)
[![Tailwind](https://img.shields.io/badge/Tailwind-3.4.17-38B2AC.svg)](https://tailwindcss.com)

## 🎯 Overview

The OpenMemory UI Dashboard is a modern, responsive web interface for managing memory data, built with cutting-edge technologies. It provides real-time monitoring, memory management, and analytics capabilities through a beautiful, accessible user interface.

## 🚀 Quick Start

### Prerequisites
- **Node.js**: v18.17.0+ (managed via Volta)
- **Package Manager**: pnpm 10.5.2+ (specified in packageManager field)
- **Environment**: Linux/macOS/Windows with modern browser support

### Installation & Development
```bash
# Navigate to UI directory
cd mem0/openmemory/ui

# Install dependencies (MUST use pnpm, not npm)
pnpm install

# Start development server
pnpm run dev --port 3010

# Build for production
pnpm run build

# Start production server
pnpm start
```

### Important Notes
- **Always use `pnpm`** - This project is configured for pnpm package manager
- **Directory Context**: Run commands from `mem0/openmemory/ui` directory
- **Development Port**: Default port 3010 to avoid conflicts

## 🏗️ Technology Stack

### **Core Framework**
| Technology | Version | Purpose | Why Chosen |
|------------|---------|---------|------------|
| **Next.js** | 15.2.4 | React Framework | Latest features, excellent developer experience, production-ready |
| **React** | 19.0.0 | UI Library | Cutting-edge concurrent features, server components |
| **TypeScript** | 5.0+ | Type Safety | Enhanced developer experience, catch errors at compile-time |

### **UI & Styling (27 packages)**
| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **Tailwind CSS** | 3.4.17 | Utility-first CSS | [Tailwind Docs](https://tailwindcss.com/docs) |
| **Radix UI** | ^1.1+ | Accessible Components | 25 component packages for comprehensive UI |
| **Lucide React** | ^0.454.0 | Icon System | [Lucide Icons](https://lucide.dev) |
| **shadcn/ui** | Latest | Component System | [shadcn/ui Docs](https://ui.shadcn.com) |

#### **Radix UI Components Used:**
```typescript
// Form & Input Components
@radix-ui/react-checkbox, react-radio-group, react-select, react-slider, react-switch
@radix-ui/react-label, input-otp, react-hook-form, @hookform/resolvers

// Layout & Navigation
@radix-ui/react-accordion, react-collapsible, react-navigation-menu, react-tabs
@radix-ui/react-scroll-area, react-resizable-panels, @radix-ui/react-separator

// Overlay & Feedback
@radix-ui/react-dialog, react-popover, react-tooltip, react-hover-card
@radix-ui/react-alert-dialog, react-toast, sonner

// Interactive Elements
@radix-ui/react-dropdown-menu, react-context-menu, react-menubar
@radix-ui/react-toggle, react-toggle-group, react-progress
```

### **Data & State Management (5 packages)**
| Technology | Version | Purpose | Integration |
|------------|---------|---------|-------------|
| **Redux Toolkit** | ^2.7.0 | Global State | Modern Redux with excellent DevTools |
| **React Redux** | ^9.2.0 | React Integration | Official React bindings for Redux |
| **Axios** | ^1.8.4 | HTTP Client | Promise-based HTTP requests with interceptors |
| **Zod** | ^3.24.1 | Schema Validation | TypeScript-first validation with inference |
| **React Hook Form** | ^7.54.1 | Form Management | Performant forms with minimal re-renders |

### **Charts & Visualization (3 packages)**
| Technology | Version | Purpose | Features |
|------------|---------|---------|----------|
| **Recharts** | 2.15.0 | Chart Library | React-based charts, highly customizable |
| **Date-fns** | 4.1.0 | Date Utilities | Modern date manipulation, tree-shakeable |
| **React Day Picker** | 8.10.1 | Date Selection | Accessible date picker component |

### **Developer Experience (8 packages)**
| Technology | Version | Purpose | Benefits |
|------------|---------|---------|----------|
| **TypeScript** | ^5.0 | Type Checking | Compile-time error detection |
| **@types/*** | Latest | Type Definitions | Full TypeScript support for all libraries |
| **PostCSS** | ^8.0 | CSS Processing | Tailwind CSS compilation |
| **Autoprefixer** | ^10.4.20 | CSS Vendor Prefixes | Cross-browser CSS compatibility |

## 📁 Project Structure

```
mem0/openmemory/ui/
├── 📄 Configuration
│   ├── package.json              # Dependencies & scripts
│   ├── tsconfig.json             # TypeScript configuration
│   ├── tailwind.config.ts        # Tailwind CSS configuration
│   ├── postcss.config.mjs        # PostCSS processing
│   ├── components.json           # shadcn/ui configuration
│   └── next.config.mjs           # Next.js configuration
├── 🎨 Frontend Structure
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx            # Root layout with providers
│   │   ├── page.tsx              # Dashboard main page
│   │   └── globals.css           # Global styles with Tailwind
│   ├── components/               # Reusable UI components
│   │   ├── ui/                   # shadcn/ui components
│   │   └── dashboard/            # Dashboard-specific components
│   ├── hooks/                    # Custom React hooks
│   ├── lib/                      # Utility functions
│   └── store/                    # Redux store configuration
├── 🎨 Assets
│   ├── public/                   # Static assets (logo, icons)
│   └── styles/                   # Additional stylesheets
├── 🐳 Deployment
│   ├── Dockerfile                # Multi-stage Docker build
│   ├── .dockerignore             # Docker ignore patterns
│   └── entrypoint.sh             # Docker startup script
└── 🔧 Development
    ├── .env.example              # Environment variables template
    └── pnpm-lock.yaml            # Locked dependency versions
```

## 🎨 Component Architecture

### **shadcn/ui Integration**
This project uses [shadcn/ui](https://ui.shadcn.com) - a collection of copy-paste components built on top of Radix UI and Tailwind CSS.

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui"
  },
  "iconLibrary": "lucide"
}
```

### **Key Design Principles**
- **Accessibility First**: All components use Radix UI primitives for WCAG compliance
- **Type Safety**: Full TypeScript coverage with strict type checking
- **Performance**: Optimized with React 19 concurrent features
- **Responsive Design**: Mobile-first approach with Tailwind responsive utilities
- **Dark Theme**: Built-in dark mode support with next-themes

## 🔧 Development Workflow

### **Available Scripts**
```bash
pnpm run dev      # Start development server (port 3010)
pnpm run build    # Build for production
pnpm run start    # Start production server
pnpm run lint     # Run ESLint for code quality
```

### **Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Configure variables
API_URL=http://localhost:8765          # OpenMemory API endpoint
NEXT_PUBLIC_APP_URL=http://localhost:3010  # App URL for client-side
```

### **Code Quality Tools**
- **ESLint**: Configured with Next.js recommended rules
- **TypeScript**: Strict mode enabled for maximum type safety
- **Prettier**: Automatic code formatting (if configured)

## 🐳 Docker Deployment

### **Multi-stage Dockerfile**
```dockerfile
# Development: Local development with hot reload
# Production: Optimized build with minimal runtime
# Base: Node 18 Alpine for security and size
```

### **Docker Commands**
```bash
# Build image
docker build -t openmemory-ui .

# Run container
docker run -p 3010:3000 openmemory-ui

# Development with volume mount
docker run -v $(pwd):/app -p 3010:3000 openmemory-ui
```

## 📚 Dependency Documentation

### **Why These Dependencies?**

**Next.js 15.2.4**: 
- Latest stable version with server components
- Excellent performance with automatic optimization
- Built-in TypeScript support

**React 19**:
- Cutting-edge features like concurrent rendering
- Improved developer experience
- Better performance optimizations

**Radix UI Components**:
- Industry-leading accessibility (WCAG 2.1 AA compliant)
- Unstyled primitives perfect for Tailwind CSS
- Comprehensive component coverage

**Redux Toolkit**:
- Modern Redux with less boilerplate
- Built-in immutability with Immer
- Excellent DevTools integration

**TypeScript 5**:
- Enhanced type inference
- Better error messages
- Modern JavaScript features

### **Dependency Update Strategy**
- **Major Updates**: Review breaking changes, test thoroughly
- **Minor Updates**: Generally safe, review changelogs
- **Patch Updates**: Auto-update for security fixes
- **Lock File**: Always commit pnpm-lock.yaml for reproducible builds

## 🔒 Security Considerations

### **Dependency Security**
- Regular dependency audits with `pnpm audit`
- Automated vulnerability scanning
- Minimal dependency tree to reduce attack surface

### **Runtime Security**
- CSP headers configured in Next.js
- No inline scripts or dangerous HTML
- Sanitized user inputs with Zod validation

## 🚀 Performance Optimizations

### **Build Optimizations**
- **Tree Shaking**: Automatic unused code elimination
- **Code Splitting**: Route-based and dynamic imports
- **Image Optimization**: Next.js Image component with WebP
- **CSS Optimization**: Tailwind CSS purging and minification

### **Runtime Performance**
- **React 19 Features**: Concurrent rendering and automatic batching
- **Memoization**: Strategic use of useMemo and useCallback
- **Bundle Analysis**: Regular bundle size monitoring

## 🛠️ Troubleshooting

### **Common Issues**

**"next: not found" Error**:
- **Cause**: Running npm instead of pnpm, or wrong directory
- **Solution**: Use `pnpm run dev` from `mem0/openmemory/ui` directory

**Port 3010 in Use**:
- **Check**: `lsof -i :3010`
- **Solution**: Kill process or use different port with `--port`

**TypeScript Errors**:
- **Solution**: Ensure all @types packages are installed
- **Check**: `pnpm install` and restart TypeScript server

**Styling Issues**:
- **Cause**: Missing Tailwind CSS classes or configuration
- **Solution**: Check `tailwind.config.ts` and rebuild CSS

### **Getting Help**
1. Check this README for common solutions
2. Review Next.js documentation for framework issues
3. Check component documentation for Radix UI issues
4. Review TypeScript errors for type issues

## 📈 Future Enhancements

### **Planned Features**
- **Testing**: Jest + Testing Library setup
- **Storybook**: Component documentation and testing
- **E2E Testing**: Playwright integration
- **Bundle Analysis**: Automated bundle size tracking
- **Performance Monitoring**: Real User Monitoring (RUM)

### **Potential Upgrades**
- **React Server Components**: Migrate to server components where beneficial
- **Streaming**: Implement streaming for better perceived performance
- **Progressive Web App**: Add PWA capabilities for offline usage

---

## 📞 Support & Contributing

### **Development Support**
- **Documentation**: This README covers all essential information
- **Code Style**: Follow existing patterns and TypeScript best practices
- **Component Guidelines**: Use Radix UI primitives with Tailwind styling

### **Contributing Guidelines**
1. Follow the established TypeScript and React patterns
2. Ensure accessibility compliance with Radix UI components
3. Add proper TypeScript types for all new functionality
4. Test responsive design across multiple screen sizes
5. Update this README when adding new dependencies

---

**🎨 Built with modern web technologies for exceptional developer experience and user satisfaction**

*Last Updated: 2025-06-28 | Status: Production Ready | Dependencies: 54 packages documented* 