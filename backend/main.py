"""
Workforce Pulse: Opportunity Navigator — FastAPI Backend

Entry point for the Python backend server.
Run with: uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import api_router, scrape_router, webhook_router
from services.bright_data import trigger_scrape, normalize_payload
from services.data_store import data_store

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Workforce Pulse: Opportunity Navigator API",
    description=(
        "Backend API for the Opportunity Navigator dashboard. "
        "Serves municipal labor market data, AI-powered opportunity matching, "
        "and training program recommendations for Montgomery, Alabama."
    ),
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS — allow the React frontend origin
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Include routers
# ---------------------------------------------------------------------------
app.include_router(api_router)
app.include_router(scrape_router)
app.include_router(webhook_router)


# ---------------------------------------------------------------------------
# Startup / Shutdown events
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def on_startup():
    """
    On startup, load seed data immediately so the server binds the port fast,
    then trigger Bright Data in the background to replace seed with live data.
    """
    logger.info("Starting Opportunity Navigator API...")
    logger.info("Environment: %s", settings.environment)
    logger.info("Allowed origins: %s", settings.cors_origins)
    logger.info("Bright Data configured: %s", settings.is_bright_data_configured)
    logger.info("Gemini configured: %s", settings.is_gemini_configured)

    # ── Always load seed data first so the server starts immediately ──
    if data_store.job_count == 0:
        count = data_store.load_seed_data()
        if count > 0:
            logger.info("Loaded %d seed jobs for immediate serving", count)
        else:
            logger.warning("No seed data available — job store is empty")

    # ── Then kick off Bright Data fetch in background (non-blocking) ──
    if settings.is_bright_data_configured:
        logger.info("Scheduling background Bright Data fetch...")
        asyncio.create_task(_fetch_bright_data_background())
    else:
        logger.warning("Bright Data not configured — serving seed data only")


async def _fetch_bright_data_background():
    """
    Background task: call Bright Data directly (notify=false) to get live jobs.
    Replaces seed data once results arrive.
    """
    await asyncio.sleep(3)

    try:
        logger.info("Fetching live jobs from Bright Data (direct mode)...")
        result = await trigger_scrape(notify_url=None)
        if not result:
            logger.warning("Bright Data returned nothing — keeping seed data")
            return

        # Direct mode returns inline data
        if "_inline_data" in result:
            raw_jobs = result["_inline_data"]
            normalized = normalize_payload(raw_jobs)
            if normalized:
                data_store.replace_all(normalized)
                logger.info("Live data loaded — %d jobs, replaced seed data", len(normalized))
            else:
                logger.warning("Got %d raw jobs but 0 normalized — keeping seed data", len(raw_jobs))
        else:
            logger.warning("Unexpected Bright Data response (no inline data): %s", result)
    except Exception as exc:
        logger.error("Background Bright Data fetch failed: %s — keeping seed data", exc)


@app.get("/", tags=["health"])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "Opportunity Navigator API",
        "version": "0.1.0",
        "jobs_loaded": data_store.job_count,
        "data_source": "seed" if data_store.is_using_seed_data else "live",
    }
