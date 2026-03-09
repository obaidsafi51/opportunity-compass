"""
Scrape management router — trigger and manage Bright Data scrape jobs.

Provides endpoints for:
  - POST /api/scrape/trigger  — kick off a new Bright Data scrape
  - GET  /api/scrape/status   — check data store stats and source info
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks

from config import settings
from models.schemas import DataSource, ResponseEnvelope
from services.bright_data import normalize_payload, trigger_and_poll, trigger_scrape
from services.data_store import data_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scrape", tags=["scrape"])


@router.post("/trigger")
async def trigger_bright_data_scrape(
    background_tasks: BackgroundTasks,
    mode: str = "direct",
):
    """
    Trigger a Bright Data scrape for Montgomery, AL jobs.

    Args:
        mode: "direct" (default, synchronous /scraper call — returns data inline),
              "webhook" (async delivery to /webhook/jobs),
              or "poll" (trigger → poll → download).
    """
    if not settings.is_bright_data_configured:
        return ResponseEnvelope(
            error="Bright Data API key and dataset ID are not configured. "
                  "Set BRIGHT_DATA_API_KEY and BRIGHT_DATA_DATASET_ID in .env",
            source=DataSource.CACHED,
        )

    if mode == "direct":
        # Synchronous /scraper endpoint — data comes back inline
        result = await trigger_scrape(notify_url=None)
        if result and "_inline_data" in result:
            raw_jobs = result["_inline_data"]
            normalized = normalize_payload(raw_jobs)
            if normalized:
                data_store.replace_all(normalized)
                logger.info("Direct scrape complete — %d jobs loaded", len(normalized))
                return {
                    "status": "complete",
                    "jobs_loaded": len(normalized),
                    "message": f"Scrape complete. {len(normalized)} jobs loaded into data store.",
                }
            else:
                return ResponseEnvelope(
                    error=f"Got {len(raw_jobs)} raw jobs but normalization produced 0 results.",
                    source=DataSource.CACHED,
                )
        elif result and "snapshot_id" in result:
            # Unexpected for /scraper, but handle gracefully — fall back to polling
            logger.warning("Got snapshot_id from /scraper — falling back to poll mode")
            background_tasks.add_task(_poll_workflow)
            return {
                "status": "polling_started",
                "snapshot_id": result.get("snapshot_id"),
                "message": "Scraper returned async response. Polling for results.",
            }
        else:
            return ResponseEnvelope(
                error="Failed to scrape. Check Bright Data API credentials and connectivity.",
                source=DataSource.CACHED,
            )
    elif mode == "poll":
        # Run the full polling workflow in the background
        background_tasks.add_task(_poll_workflow)
        return {
            "status": "polling_started",
            "message": "Scrape triggered with polling mode. Jobs will be loaded automatically when ready.",
        }
    else:
        # Webhook mode — trigger and let Bright Data call us back
        webhook_url = f"{settings.backend_url}/webhook/jobs"
        result = await trigger_scrape(notify_url=webhook_url)
        if result:
            return {
                "status": "triggered",
                "snapshot_id": result.get("snapshot_id"),
                "message": "Scrape triggered. Bright Data will deliver results via webhook.",
            }
        else:
            return ResponseEnvelope(
                error="Failed to trigger Bright Data scrape. Check API credentials and connectivity.",
                source=DataSource.CACHED,
            )


async def _poll_workflow():
    """Background task: run the full polling workflow and store results."""
    try:
        raw_jobs = await trigger_and_poll()
        if raw_jobs:
            normalized = normalize_payload(raw_jobs)
            data_store.replace_all(normalized)
            logger.info("Poll workflow complete — %d jobs loaded into store", len(normalized))
        else:
            logger.warning("Poll workflow returned no jobs — keeping existing data")
    except Exception as exc:
        logger.error("Poll workflow failed: %s", exc)


@router.get("/status")
async def get_scrape_status():
    """
    Return the current state of the data store.
    Useful for the frontend to show 'Live Data' vs 'Sample Data' indicator.
    """
    return {
        "total_jobs": data_store.job_count,
        "data_source": "seed" if data_store.is_using_seed_data else "live",
        "bright_data_configured": settings.is_bright_data_configured,
        "gemini_configured": settings.is_gemini_configured,
    }
