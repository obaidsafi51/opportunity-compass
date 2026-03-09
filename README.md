# Workforce Pulse: Opportunity Navigator

> **WORLD WIDE VIBES 2026** — "Workforce, Business & Economic Growth" Track  
> **Team:** Obaid (Full-Stack Developer) · Suyen (UX/Graphic Designer) · Paul (Workforce Planning Lead)

A dual-panel web dashboard that transforms abstract labor statistics into actionable, individualized career pathways for vulnerable populations in **Montgomery, Alabama**. It combines civic open data, real-time Indeed job scraping (Bright Data), and AI-powered cognitive matching (Google Gemini 2.5 Flash) to surface reachable opportunities filtered by persona — General, Long-Term Unemployed, and NEET Youth.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6?logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-AI-4285F4?logo=google&logoColor=white)

---

## The Problem

| Signal | Data Point | The Hidden Story |
|---|---|---|
| Low unemployment | 2.7% | Looks healthy on paper |
| High poverty rate | 19.7% | Many are trapped in low-wage, cyclical work |
| Median household income | $57,300 | Masks acute struggles of specific subgroups |

Traditional dashboards serve policymakers with aggregated numbers. They **completely fail** at the individual level — they don't help a long-term unemployed adult or a NEET youth identify accessible career pathways. Standard metrics actively mask their struggles.

**Our solution:** An active intervention engine that makes systemic barriers visible and maps reachable opportunities to funded local training programs.

---

## Key Features

- **Municipal Overview Strip** — Population, unemployment rate, open jobs, median income, poverty rate
- **Skills Heatmap** — Top 8-10 in-demand skills with posting counts, trend velocity, and "Rising Skill" badges
- **Training Deficit Panel** — Occupational gaps classified as Acute / Emerging / Balanced
- **Persona-Based Opportunity Navigator** — Tri-state toggle refilters all data through persona constraints
- **AI-Powered Role Cards** — Gemini analyzes job descriptions for barrier flags, wage estimates, and persona-specific fit reasons
- **Interactive Barrier Filters** — Toggle "No Degree," "No Car," "No Experience" to grey out ineligible roles
- **Local Program Recommendations** — Maps roles to specific Montgomery training programs (YouthBuild, Trenholm State, TechMGM, etc.)
- **$15/hr Living-Wage Floor** — Jobs below the floor are automatically filtered out

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, TypeScript, Vite 5, Tailwind CSS, shadcn/ui (Radix), TanStack Query, Recharts, Framer Motion |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, httpx, Uvicorn |
| **AI Engine** | Google Gemini 2.5 Flash (structured JSON output) |
| **Data Scraping** | Bright Data Web Scraper API (Indeed jobs) |
| **Civic Data** | City of Montgomery Open Data Portal (ArcGIS) |

---

## Quick Start

### Prerequisites

| Requirement | Version |
|---|---|
| **Python** | 3.11+ |
| **Node.js** | 18+ |
| **Bun** (recommended) or npm | latest |

### 1. Clone the Repository

```bash
git clone <repo-url>
cd opportunity-compass
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

Create a `.env.development` file in `backend/`:

```dotenv
ENVIRONMENT=development
FRONTEND_ORIGIN=http://localhost:8080,http://localhost:5173,http://localhost:3000
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# AI Analysis (optional — enables Gemini-powered job analysis)
GEMINI_API_KEY=your_gemini_api_key_here

# Live Scraping (optional — enables real-time Indeed job scraping)
BRIGHT_DATA_API_KEY=your_bright_data_api_key_here
BRIGHT_DATA_DATASET_ID=your_dataset_id_here
```

> **Works without API keys!** The app loads seed data from `data/seed-jobs.json` so the dashboard is never empty.

Start the backend:

```bash
uvicorn main:app --reload --port 8000
```

Backend is now running at **http://localhost:8000** (interactive docs at `/docs`).

### 3. Frontend Setup

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
bun install          # or: npm install

# Start dev server
bun run dev          # or: npm run dev
```

Frontend is now running at **http://localhost:8080**.

> Vite automatically proxies `/api` and `/webhook` requests to the backend at `:8000` — no extra configuration needed.

### 4. Open the App

Navigate to **http://localhost:8080** in your browser. You'll see the onboarding modal — pick a persona and optional barriers, then explore the dashboard.

---

## Project Structure

```
opportunity-compass/
├── README.md                    ← You are here
│
├── backend/                     # Python FastAPI server
│   ├── main.py                  #   App entry point & startup
│   ├── config.py                #   Environment config (pydantic-settings)
│   ├── requirements.txt         #   Python dependencies
│   ├── Procfile                 #   Deployment manifest
│   ├── data/seed-jobs.json      #   Seed job data fallback
│   ├── models/schemas.py        #   Pydantic request/response models
│   ├── routers/                 #   API route handlers
│   │   ├── api.py               #     /api/* endpoints
│   │   ├── scrape.py            #     /api/scrape/* endpoints
│   │   └── webhook.py           #     /webhook/jobs receiver
│   └── services/                #   Business logic
│       ├── analysis.py          #     Gemini analysis orchestrator
│       ├── bright_data.py       #     Bright Data scraper client
│       ├── civic_data.py        #     Montgomery Open Data client
│       ├── data_store.py        #     In-memory job store
│       ├── gaps_analysis.py     #     Skills & training gap aggregation
│       ├── gemini.py            #     Gemini API client
│       ├── programs_db.py       #     Local training programs DB
│       └── wage_utils.py        #     Wage parsing & $15 floor
│
└── frontend/                    # React + TypeScript SPA
    ├── src/
    │   ├── App.tsx              #   Root component (routing)
    │   ├── pages/
    │   │   ├── Home.tsx         #   Landing page (persona heroes)
    │   │   └── Index.tsx        #   Main dashboard
    │   ├── components/
    │   │   ├── OnboardingModal  #   First-visit persona selector
    │   │   ├── SkillsHeatmap   #   Skills demand visualization
    │   │   ├── TrainingGapPanel #   Training deficit analysis
    │   │   ├── PersonaCards     #   Role cards + programs
    │   │   └── ui/              #   40+ shadcn/ui primitives
    │   ├── data/                #   Static/fallback datasets
    │   └── lib/utils.ts         #   API_BASE + utilities
    ├── package.json
    └── vite.config.ts           #   Dev proxy + chunk splitting
```

---

## API Endpoints

All data endpoints return a standard envelope: `{ data, error, source }`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check (status, version, job count) |
| `GET` | `/api/summary` | Municipal overview — population, unemployment, jobs, income, poverty |
| `GET` | `/api/skills` | Top 8-10 in-demand skills for the heatmap |
| `GET` | `/api/gaps` | Training deficit analysis with severity labels |
| `GET` | `/api/opportunities?persona=<type>` | Persona-filtered role cards (`general` / `long_term_unemployed` / `neet_youth`) |
| `GET` | `/api/programs` | Local training programs (Montgomery) |
| `GET` | `/api/growth-signals` | Business licenses & permits by sector |
| `POST` | `/api/scrape/trigger?mode=<mode>` | Trigger Bright Data scrape (`direct` / `poll` / `webhook`) |
| `GET` | `/api/scrape/status` | Data store stats |
| `POST` | `/webhook/jobs` | Bright Data webhook receiver |

Full API docs are auto-generated at **http://localhost:8000/docs** (Swagger UI).

---

## Environment Variables Reference

### Backend (`backend/.env.development`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `ENVIRONMENT` | No | `development` | `development` or `production` |
| `FRONTEND_ORIGIN` | No | `http://localhost:8080,...` | Comma-separated CORS origins |
| `BACKEND_HOST` | No | `0.0.0.0` | Server bind host |
| `BACKEND_PORT` | No | `8000` | Server bind port |
| `GEMINI_API_KEY` | No | — | Google Gemini API key (enables AI analysis) |
| `BRIGHT_DATA_API_KEY` | No | — | Bright Data API key (enables live scraping) |
| `BRIGHT_DATA_DATASET_ID` | No | — | Bright Data dataset ID |

### Frontend (`frontend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `VITE_API_URL` | No | `""` (uses Vite proxy) | Backend API URL for production builds |

---

## How It Works

```
┌──────────────────────────────────────────────────────────────┐
│                        Frontend (:8080)                       │
│  Landing Page → Onboarding Modal → Dashboard                 │
│  Persona Toggle + Barrier Filters → Live-updating panels     │
└────────────────────────┬─────────────────────────────────────┘
                         │ /api/* (Vite proxy in dev)
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                        Backend (:8000)                        │
│                                                              │
│  Startup:                                                    │
│    1. Load seed-jobs.json (instant data)                     │
│    2. Trigger Bright Data scrape (background)                │
│    3. Run Gemini analysis on fetched jobs                    │
│                                                              │
│  Data Sources:                                               │
│    ├── Montgomery Open Data Portal (demographics)            │
│    ├── Bright Data (real-time Indeed scraping)                │
│    └── Google Gemini 2.5 Flash (job analysis)                │
│                                                              │
│  AI Pipeline:                                                │
│    Job description → Gemini → barrier flags, wages, skills,  │
│    persona reachability, fit reasons, category                │
│                                                              │
│  Output: Persona-filtered, wage-floored role cards           │
│          with matched local training programs                │
└──────────────────────────────────────────────────────────────┘
```

---

## Deployment

### Backend

Includes a `Procfile` for Heroku/Render-style platforms:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

Set production env vars (`ENVIRONMENT=production`, `FRONTEND_ORIGIN`, API keys).

### Frontend

Builds to a static `dist/` folder:

```bash
cd frontend && bun run build
```

Deploy to **Vercel**, **Netlify**, or any static host. Set `VITE_API_URL` to your deployed backend URL.

---

## License

Built for the **WORLD WIDE VIBES 2026** Hackathon — "Workforce, Business & Economic Growth" Track.

**Team:** Obaid (Full-Stack Developer) · Suyen (UX/Graphic Designer) · Paul (Workforce Planning Lead)
