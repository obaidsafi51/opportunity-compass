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
    """Load seed data on startup if no live data is available."""
    logger.info("Starting Opportunity Navigator API...")
    logger.info("Environment: %s", settings.environment)
    logger.info("Allowed origins: %s", settings.cors_origins)
    logger.info("Bright Data configured: %s", settings.is_bright_data_configured)
    logger.info("Gemini configured: %s", settings.is_gemini_configured)

    # Load seed data as fallback
    if data_store.job_count == 0:
        count = data_store.load_seed_data()
        if count > 0:
            logger.info("Loaded %d seed jobs as fallback", count)
            # Kick off async analysis pipeline directly
            logger.info("Triggering background analysis pipeline for seed data fallback")
            asyncio.create_task(run_analysis_pipeline(limit=50))
        else:
            logger.warning("No seed data available — job store is empty")


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
