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
from services.analysis import run_analysis_pipeline
from services.bright_data import trigger_scrape, trigger_and_poll, normalize_payload
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
    On startup, attempt to fetch live jobs from Bright Data.
    Falls back to seed data only if Bright Data is not configured or fails.
    """
    logger.info("Starting Opportunity Navigator API...")
    logger.info("Environment: %s", settings.environment)
    logger.info("Allowed origins: %s", settings.cors_origins)
    logger.info("Bright Data configured: %s", settings.is_bright_data_configured)
    logger.info("Gemini configured: %s", settings.is_gemini_configured)

    if data_store.job_count == 0:
        # ── 1. Try Bright Data first ──────────────────────────────────
        if settings.is_bright_data_configured:
            logger.info("Attempting to fetch live jobs from Bright Data...")
            try:
                # Try webhook mode first — Bright Data will POST back to /webhook/jobs
                webhook_url = f"{settings.backend_url}/webhook/jobs"
                result = await trigger_scrape(notify_url=webhook_url)
                if result:
                    logger.info(
                        "Bright Data scrape triggered (webhook mode). "
                        "snapshot_id=%s — data will arrive via /webhook/jobs",
                        result.get("snapshot_id"),
                    )
                    # Load seed data temporarily while we wait for the webhook delivery
                    count = data_store.load_seed_data()
                    if count > 0:
                        logger.info(
                            "Loaded %d seed jobs as interim data while waiting for Bright Data",
                            count,
                        )
                        asyncio.create_task(run_analysis_pipeline(limit=50))
                else:
                    # Webhook trigger failed — try full polling workflow in background
                    logger.warning(
                        "Webhook trigger failed. Falling back to polling workflow..."
                    )
                    asyncio.create_task(_startup_poll_workflow())
                    # Load seed data while polling runs
                    count = data_store.load_seed_data()
                    if count > 0:
                        logger.info(
                            "Loaded %d seed jobs as interim data while polling runs",
                            count,
                        )
                        asyncio.create_task(run_analysis_pipeline(limit=50))
            except Exception as exc:
                logger.error("Bright Data startup fetch failed: %s", exc)
                _load_seed_fallback()
        else:
            # ── 2. Bright Data not configured — use seed data ─────────
            logger.warning("Bright Data not configured — loading seed data as fallback")
            _load_seed_fallback()


def _load_seed_fallback():
    """Load seed data and kick off analysis."""
    count = data_store.load_seed_data()
    if count > 0:
        logger.info("Loaded %d seed jobs as fallback", count)
        asyncio.create_task(run_analysis_pipeline(limit=50))
    else:
        logger.warning("No seed data available — job store is empty")


async def _startup_poll_workflow():
    """Background task: poll Bright Data for results and replace the store."""
    try:
        raw_jobs = await trigger_and_poll()
        if raw_jobs:
            normalized = normalize_payload(raw_jobs)
            data_store.replace_all(normalized)
            logger.info(
                "Startup poll workflow complete — %d live jobs loaded, replacing seed data",
                len(normalized),
            )
            # Run Gemini analysis on the fresh live data
            await run_analysis_pipeline(limit=50)
        else:
            logger.warning("Startup poll workflow returned no jobs — keeping seed data")
    except Exception as exc:
        logger.error("Startup poll workflow failed: %s — keeping seed data", exc)


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
