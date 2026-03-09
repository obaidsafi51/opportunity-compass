# Workforce Pulse: Opportunity Navigator — Frontend

> React + TypeScript single-page application powering the Opportunity Navigator dashboard. Visualizes real-time labor market data for Montgomery, Alabama and provides persona-based career pathway matching for vulnerable populations.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Development Server](#development-server)
  - [Building for Production](#building-for-production)
- [Project Structure](#project-structure)
- [Pages & Routing](#pages--routing)
- [Key Components](#key-components)
- [Data Flow](#data-flow)
- [API Integration](#api-integration)
- [Design System](#design-system)
- [Testing](#testing)
- [Deployment](#deployment)
- [License](#license)

---

## Overview

The frontend is a **dual-panel dashboard** built for the **WORLD WIDE VIBES 2026** Hackathon ("Workforce, Business & Economic Growth" track). It transforms abstract labor statistics into actionable, individualized career pathways for Montgomery, Alabama.

**Key Features:**
- **Landing Page** — Persona-driven hero sections with animated transitions (Framer Motion)
- **Skills Heatmap** — Top 8-10 in-demand skills with posting counts, trend indicators, and "Rising Skill" badges
- **Training Deficit Panel** — Occupational gaps classified as Acute / Emerging / Balanced with aligned program recommendations
- **Persona-Based Opportunity Navigator** — Tri-state toggle (General / Long-Term Unemployed / NEET Youth) refilters all data
- **Barrier Filters** — Interactive boolean checkboxes that visually grey out ineligible roles
- **Onboarding Modal** — First-visit guided persona and barrier selection
- **Local Program Recommendations** — Maps roles to funded Montgomery training programs

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | **React 18** with **TypeScript** |
| Build Tool | **Vite 5** (SWC plugin) |
| Styling | **Tailwind CSS 3** + **tailwindcss-animate** |
| UI Components | **shadcn/ui** (Radix UI primitives) |
| State / Data | **TanStack React Query** v5 |
| Routing | **React Router DOM** v6 |
| Charts | **Recharts** |
| Animations | **Framer Motion** |
| Forms | **React Hook Form** + **Zod** validation |
| Icons | **Lucide React** |
| Package Manager | **Bun** (also compatible with npm/yarn/pnpm) |

---

## Getting Started

### Prerequisites

- **Node.js 18+**
- **Bun** (recommended) or npm/yarn/pnpm
- Backend server running on `http://localhost:8000` (see [backend README](../backend/README.md))

### Installation

```bash
# Navigate to the frontend directory
cd opportunity-compass/frontend

# Install dependencies
bun install
# or: npm install
```

### Environment Variables

Create a `.env` or `.env.local` file in the `frontend/` directory:

```dotenv
# API base URL — leave empty to use Vite proxy (recommended for dev)
VITE_API_URL=

# For production builds pointing to a deployed backend:
# VITE_API_URL=https://your-backend-api.com
```

> **Note:** In development, Vite proxies `/api` and `/webhook` requests to `http://localhost:8000` automatically (configured in `vite.config.ts`). No `VITE_API_URL` is needed.

### Development Server

```bash
bun run dev
# or: npm run dev
```

The app will be available at **http://localhost:8080**.

### Building for Production

```bash
bun run build
# or: npm run build

# Preview the production build locally
bun run preview
```

---

## Project Structure

```
frontend/
├── index.html                # HTML entry point
├── package.json              # Dependencies & scripts
├── vite.config.ts            # Vite config (proxy, aliases, chunk splitting)
├── tailwind.config.ts        # Tailwind CSS configuration
├── tsconfig.json             # TypeScript root config
├── vitest.config.ts          # Test configuration
├── components.json           # shadcn/ui component config
│
├── public/
│   └── robots.txt
│
└── src/
    ├── main.tsx              # React entry point
    ├── App.tsx               # Root component — routing & providers
    ├── index.css             # Global styles & Tailwind directives
    ├── vite-env.d.ts         # Vite type declarations
    │
    ├── pages/
    │   ├── Home.tsx          # Landing page with persona hero sections
    │   ├── Index.tsx         # Main dashboard (dual-panel layout)
    │   └── NotFound.tsx      # 404 page
    │
    ├── components/
    │   ├── TopNav.tsx        # Navigation bar with profile reset
    │   ├── OnboardingModal.tsx  # First-visit persona + barrier selector
    │   ├── SkillsHeatmap.tsx    # Skills demand visualization
    │   ├── SkillsChart.tsx      # Recharts-based skill chart
    │   ├── TrainingGapPanel.tsx # Training deficit analysis
    │   ├── PersonaCards.tsx     # Opportunity role cards + programs
    │   ├── Footer.tsx           # Page footer
    │   ├── NavLink.tsx          # Navigation link component
    │   └── ui/                  # shadcn/ui components (40+ primitives)
    │       ├── button.tsx
    │       ├── card.tsx
    │       ├── dialog.tsx
    │       ├── checkbox.tsx
    │       ├── scroll-area.tsx
    │       ├── tabs.tsx
    │       ├── toast.tsx
    │       ├── tooltip.tsx
    │       └── ... (accordion, badge, dropdown, etc.)
    │
    ├── data/                 # Static/fallback datasets
    │   ├── barriers.ts       # Barrier filter definitions
    │   ├── cityStats.ts      # Montgomery demographic constants
    │   ├── gaps.ts           # Fallback training gap data
    │   ├── programmes.ts     # Local training program data
    │   ├── rolesReachable.ts # Persona definitions & role mappings
    │   ├── skillRoleMap.ts   # Skill-to-role mapping table
    │   └── skills.ts         # Fallback skills heatmap data
    │
    ├── hooks/
    │   ├── use-mobile.tsx    # Mobile breakpoint detection hook
    │   └── use-toast.ts      # Toast notification hook
    │
    ├── lib/
    │   └── utils.ts          # cn() utility + API_BASE constant
    │
    ├── assets/               # Static images (hero photos, etc.)
    │
    └── test/
        ├── setup.ts          # Test setup (jsdom)
        └── example.test.ts   # Example test
```

---

## Pages & Routing

| Path | Component | Description |
|---|---|---|
| `/` | `Home` | Persona-driven landing page with animated hero sections |
| `/dashboard` | `Index` | Main dual-panel dashboard |
| `*` | `NotFound` | 404 catch-all |

---

## Key Components

### `OnboardingModal`
First-visit onboarding flow — a two-step modal:
1. **Persona selection** — Recruiters, Long-Term Unemployed, NEET Youth
2. **Barrier selection** — No Degree, No Car, No Experience

Stores the user's profile in `localStorage` (`pulse_profile`). Profile can be reset from the top nav.

### `SkillsHeatmap`
Fetches `/api/skills` and renders a ranked list of in-demand skills with:
- Posting count badges
- Percentage change indicators (trending up/down)
- "Rising Skill" labels for skills with ≥25% surge
- Color-coded demand levels (High Demand / Moderate Growth / Saturating)

### `TrainingGapPanel`
Fetches `/api/gaps` and groups occupations by severity:
- **Acute Shortage** (red) — critical training deficits
- **Emerging Shortage** (amber) — growing gaps
- **Balanced** (green) — adequate training pipeline

### `PersonaCards`
Fetches `/api/opportunities?persona=<type>` and renders role cards showing:
- Job title, wage range, training duration
- AI-generated fit reasons (persona-specific)
- Barrier requirement badges
- Matched local training programs with support flags (childcare, transit, etc.)

Roles are visually greyed out when they conflict with active barrier filters.

---

## Data Flow

```
┌────────────────────────────────────────────────────┐
│                  React App                         │
│                                                    │
│  ┌──────────────┐   ┌─────────────────────────┐   │
│  │ OnboardingModal│  │  Persona Toggle + Barrier│  │
│  │  (first visit) │  │    Filters (Index.tsx)   │  │
│  └──────┬─────────┘  └──────────┬──────────────┘  │
│         │ localStorage           │ state            │
│         ▼                        ▼                  │
│  ┌──────────────────────────────────────────────┐  │
│  │            TanStack React Query              │  │
│  │  useQuery("skills")  → GET /api/skills       │  │
│  │  useQuery("gaps")    → GET /api/gaps         │  │
│  │  useQuery("opps")    → GET /api/opportunities│  │
│  └──────────────────────────────────────────────┘  │
│         │                                           │
│         ▼                                           │
│  ┌──────────────────────────────────────────────┐  │
│  │  SkillsHeatmap │ TrainingGapPanel │ Persona  │  │
│  │                │                  │  Cards    │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
         │  Vite Dev Proxy (/api → :8000)
         ▼
   FastAPI Backend
```

---

## API Integration

All API calls go through `API_BASE` (from `src/lib/utils.ts`):

```typescript
export const API_BASE = (import.meta.env.VITE_API_URL || "").replace(/\/+$/, "");
```

In development, Vite proxies `/api` and `/webhook` to the backend at `http://localhost:8000`:

```typescript
// vite.config.ts
proxy: {
  "/api": { target: "http://localhost:8000", changeOrigin: true },
  "/webhook": { target: "http://localhost:8000", changeOrigin: true },
}
```

Data fetching uses **TanStack React Query** for caching, background refetching, and loading states.

---

## Design System

- **Color Palette**: Dark theme centered on `hsl(270, *)` purple accent
- **Typography**: System font stack with tracking-tight headings
- **Component Library**: 40+ shadcn/ui primitives (Radix UI based)
- **Responsive**: Mobile-first with `use-mobile.tsx` breakpoint hook
- **Animations**: Framer Motion for page transitions and scroll-triggered reveals
- **Accessibility**: Radix UI handles focus management, keyboard navigation, and ARIA attributes

Key design tokens:

| Token | Value | Usage |
|---|---|---|
| Primary accent | `hsl(270, 80%, 55%)` | Buttons, active states, badges |
| Rising skill | `hsl(152, 60%, 45%)` | Positive trend indicators |
| Warning | `hsl(38, 92%, 55%)` | Emerging shortage labels |
| Danger | `hsl(0, 72%, 55%)` | Acute shortage, negative trends |
| Background | `hsl(270, 40%, 8%)` | Dark base background |

---

## Testing

```bash
# Run tests once
bun run test

# Run tests in watch mode
bun run test:watch
```

Tests use **Vitest** + **@testing-library/react** with **jsdom** environment.

---

## Scripts

| Script | Command | Description |
|---|---|---|
| `dev` | `bun run dev` | Start Vite dev server (port 8080) |
| `build` | `bun run build` | Production build |
| `build:dev` | `bun run build:dev` | Development build |
| `preview` | `bun run preview` | Preview production build |
| `lint` | `bun run lint` | ESLint check |
| `test` | `bun run test` | Run Vitest tests |
| `test:watch` | `bun run test:watch` | Vitest in watch mode |

---

## Deployment

The frontend builds to a static `dist/` folder suitable for any static hosting:

- **Vercel** — Auto-detects Vite, zero-config deployment
- **Netlify** — Build command: `bun run build`, publish: `dist`
- **GitHub Pages** — Deploy `dist/` folder

Set `VITE_API_URL` to your deployed backend URL in your hosting platform's environment variables:

```
VITE_API_URL=https://your-backend-api.com
```

### Chunk Splitting

The production build uses manual chunk splitting for optimal loading:

| Chunk | Libraries |
|---|---|
| `vendor` | react, react-dom, react-router-dom |
| `ui` | Radix UI components |
| `charts` | Recharts |
| `motion` | Framer Motion |

---

## License

Built for the **WORLD WIDE VIBES 2026** Hackathon — "Workforce, Business & Economic Growth" Track.

**Team:** Obaid (Full-Stack Developer), Suyen (UX/Graphic Designer), Paul (Workforce Planning Lead)
