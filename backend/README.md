# Workforce Pulse: Opportunity Navigator — Backend

> FastAPI backend powering the Opportunity Navigator dashboard for Montgomery, Alabama. Provides real-time labor market data, AI-powered job analysis, and persona-based opportunity matching.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running the Server](#running-the-server)
- [API Reference](#api-reference)
  - [Health Check](#health-check)
  - [Summary](#get-apisummary)
  - [Skills Heatmap](#get-apiskills)
  - [Training Gaps](#get-apigaps)
  - [Opportunities](#get-apiopportunities)
  - [Programs](#get-apiprograms)
  - [Growth Signals](#get-apigrowth-signals)
  - [Scrape Trigger](#post-apiscrapetrigger)
  - [Scrape Status](#get-apiscrapestatus)
  - [Webhook](#post-webhookjobs)
- [Project Structure](#project-structure)
- [Data Pipeline](#data-pipeline)
- [AI / Gemini Integration](#ai--gemini-integration)
- [Deployment](#deployment)
- [License](#license)

---

## Overview

The backend serves as the data engine for the **Workforce Pulse: Opportunity Navigator** — a hackathon project for **WORLD WIDE VIBES 2026** ("Workforce, Business & Economic Growth" track). It synthesizes:

- **Civic open data** from the City of Montgomery Open Data Portal (ArcGIS)
- **Real-time job postings** scraped via the Bright Data Web Scraper API (Indeed)
- **AI-powered cognitive matching** via Google Gemini 2.5 Flash

All endpoints return a standardized response envelope:

```json
{
  "data": "<T | null>",
  "error": "<string | null>",
  "source": "live | cached"
}
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | **FastAPI** 0.115 |
| Runtime | **Python 3.11+** |
| ASGI Server | **Uvicorn** 0.34 |
| Validation | **Pydantic** v2 + **pydantic-settings** |
| HTTP Client | **httpx** (async) |
| AI Engine | **Google GenAI SDK** (`google-genai`) — Gemini 2.5 Flash |
| Scraping | **Bright Data** Web Scraper API |
| Env Management | **python-dotenv** |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI App                          │
│                                                             │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ api.py   │  │  scrape.py   │  │   webhook.py       │    │
│  │ /api/*   │  │ /api/scrape/*│  │   /webhook/jobs    │    │
│  └────┬─────┘  └──────┬───────┘  └─────────┬──────────┘    │
│       │               │                    │                │
│  ┌────▼───────────────▼────────────────────▼──────────┐    │
│  │                  Services Layer                     │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────────┐  │    │
│  │  │ data_store │ │  gemini    │ │  bright_data   │  │    │
│  │  │ (in-mem)   │ │  (AI)      │ │  (scraping)    │  │    │
│  │  └────────────┘ └────────────┘ └────────────────┘  │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────────┐  │    │
│  │  │ civic_data │ │ gaps_anal. │ │  programs_db   │  │    │
│  │  │ (ArcGIS)   │ │ (heatmap)  │ │  (training)    │  │    │
│  │  └────────────┘ └────────────┘ └────────────────┘  │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │                  Models Layer                       │    │
│  │  schemas.py — Pydantic models for all I/O          │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **pip** (or your preferred package manager)
- (Optional) **Bright Data** API key + dataset ID for live scraping
- (Optional) **Google Gemini** API key for AI analysis

### Installation

```bash
# Clone the repo and navigate to the backend
cd opportunity-compass/backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env.development` file (or `.env`) in the `backend/` directory:

```dotenv
# Required
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

> **Note:** The app works without any API keys — it loads seed data from `data/seed-jobs.json` as a fallback so the dashboard is never empty.

### Running the Server

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at **http://localhost:8000**. Interactive docs at **http://localhost:8000/docs**.

---

## API Reference

All data endpoints return the `ResponseEnvelope` wrapper:

```json
{ "data": ..., "error": null, "source": "live" }
```

### Health Check

```
GET /
```

Returns service status, version, job count, and data source (`seed` / `live`).

---

### `GET /api/summary`

Municipal overview stats for the header strip.

**Response** (`SummaryResponse`):

| Field | Type | Description |
|---|---|---|
| `population` | `int` | Total population (200,603) |
| `unemployment_rate` | `float` | Unemployment rate as % |
| `total_open_jobs` | `int` | Total active job postings |
| `median_income` | `int` | Median household income (USD) |
| `poverty_rate` | `float` | Poverty rate as % |

---

### `GET /api/skills`

Top 8–10 in-demand skills by posting volume for the Skills Heatmap.

**Response** (`list[SkillRow]`):

| Field | Type | Description |
|---|---|---|
| `skill` | `str` | Skill name |
| `count` | `int` | Number of active postings |
| `pct_change` | `float` | % change vs. prior period |
| `is_rising` | `bool` | `true` if ≥25% surge |

---

### `GET /api/gaps`

Training deficit analysis — occupations with severity labels.

**Response** (`list[GapRow]`):

| Field | Type | Description |
|---|---|---|
| `occupation` | `str` | Occupation title |
| `severity` | `enum` | `balanced` / `emerging` / `acute` |
| `aligned_programs` | `list` | Matched training programs (`name`, `provider`) |

---

### `GET /api/opportunities`

Persona-filtered reachable role cards for the Opportunity Navigator.

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `persona` | `enum` | `general` | `general` / `long_term_unemployed` / `neet_youth` |

**Response** (`list[OpportunityCard]`):

| Field | Type | Description |
|---|---|---|
| `job_title` | `str` | Role title |
| `fit_reason` | `str` | AI-generated persona-specific explanation |
| `wage_range` | `str` | Estimated wage range |
| `training_weeks` | `int` | Weeks of training needed |
| `demand_count` | `int` | Number of active postings |
| `barriers` | `object` | Boolean barrier flags (degree, vehicle, experience, etc.) |
| `programs` | `list` | Aligned local training programs |

---

### `GET /api/programs`

All local training programs (Montgomery, AL).

**Response** (`list[ProgramCard]`):

| Field | Type | Description |
|---|---|---|
| `name` | `str` | Program name |
| `provider` | `str` | Institution |
| `benefit` | `str` | Key benefit |
| `eligibility` | `str` | Eligibility criteria |
| `sectors` | `list[str]` | Relevant sectors |

---

### `GET /api/growth-signals`

New business licenses & permits by sector — leading economic indicators.

**Response** (`list[GrowthSignal]`):

| Field | Type | Description |
|---|---|---|
| `sector` | `str` | Sector name |
| `new_licenses` | `int` | New business licenses |
| `permits` | `int` | Construction permits |
| `trend` | `str` | `rising` / `stable` / `declining` |

---

### `POST /api/scrape/trigger`

Trigger a new Bright Data scrape for Montgomery, AL jobs.

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `mode` | `str` | `direct` | `direct` (sync) / `poll` (background) / `webhook` (async callback) |

---

### `GET /api/scrape/status`

Check data store stats and source info.

---

### `POST /webhook/jobs`

Bright Data webhook receiver. Accepts completed scrape payloads, normalizes job data, stores it, and triggers Gemini analysis in the background.

---

## Project Structure

```
backend/
├── main.py                 # FastAPI app entry point & startup logic
├── config.py               # pydantic-settings configuration
├── requirements.txt        # Python dependencies
├── Procfile                # Deployment (Heroku/Render style)
├── .env.development        # Environment variables (dev)
├── data/
│   └── seed-jobs.json      # Seed job data fallback
├── models/
│   └── schemas.py          # Pydantic request/response models
├── routers/
│   ├── api.py              # Primary REST endpoints (/api/*)
│   ├── scrape.py           # Scrape management (/api/scrape/*)
│   └── webhook.py          # Bright Data webhook (/webhook/jobs)
└── services/
    ├── analysis.py         # Gemini analysis pipeline orchestrator
    ├── bright_data.py      # Bright Data Web Scraper API client
    ├── civic_data.py       # Montgomery Open Data Portal client (ArcGIS)
    ├── data_store.py       # In-memory job data store (singleton)
    ├── gaps_analysis.py    # Skills heatmap & training gap aggregation
    ├── gemini.py           # Google Gemini API client (job analysis)
    ├── programs_db.py      # Local training programs database
    └── wage_utils.py       # Wage parsing & $15/hr floor logic
```

---

## Data Pipeline

```
Startup
  │
  ├── Load seed-jobs.json → DataStore (immediate)
  │
  └── Background task (if Bright Data configured):
        │
        ├── Trigger Indeed scrape via Bright Data API
        │     ├── Inline response → normalize → store
        │     └── Snapshot ID → poll until ready → download → normalize → store
        │
        └── Run Gemini Analysis Pipeline
              ├── Batch unanalyzed jobs (5 at a time)
              ├── Extract: barriers, skills, wages, persona reachability
              └── Update jobs in-place in DataStore
```

The **$15/hr living-wage floor** is enforced at query time — jobs below the floor are filtered out of opportunity results, with relaxation if fewer than 3 results remain.

---

## AI / Gemini Integration

The Gemini 2.5 Flash model analyzes each job description and returns structured JSON with:

- **Barrier flags**: `requires_degree`, `requires_vehicle`, `requires_experience_1yr`, `requires_recent_certification`, `requires_continuous_work_history`
- **Wage estimate**: Extracted or market-estimated for Montgomery, AL
- **Training duration**: Weeks to become job-ready
- **Skills extraction**: Top 3-5 required skills
- **Persona reachability**: `neet_reachable`, `ltu_reachable` booleans
- **Fit reasons**: Empathetic, persona-specific explanations (8th-grade reading level, dignity-preserving language)
- **Occupational category**: e.g., Healthcare, Construction, Customer Service

The system prompt enforces strict tone guidelines:
- **LTU**: Language conveys dignity, agency, fresh starts. Never uses "upskill" or "pivot."
- **NEET Youth**: Energetic, forward-looking. Never uses "at-risk youth."
- General: Active voice, short sentences, no jargon. Says "entry-level" not "low-skilled."

---

## Deployment

The backend includes a `Procfile` for deployment to platforms like Heroku or Render:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

Ensure the following environment variables are set in your deployment environment:

- `ENVIRONMENT=production`
- `FRONTEND_ORIGIN=https://your-frontend-domain.com`
- `GEMINI_API_KEY` (optional)
- `BRIGHT_DATA_API_KEY` + `BRIGHT_DATA_DATASET_ID` (optional)

---

## License

Built for the **WORLD WIDE VIBES 2026** Hackathon — "Workforce, Business & Economic Growth" Track.

**Team:** Obaid (Full-Stack Developer), Suyen (UX/Graphic Designer), Paul (Workforce Planning Lead)
