"""
Webhook router — receives async payloads from Bright Data.

POST /webhook/jobs is called by Bright Data when a scrape job completes.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import JSONResponse

from services.bright_data import normalize_payload
from services.data_store import data_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/jobs")
async def receive_jobs(request: Request, background_tasks: BackgroundTasks):
    """
    Bright Data webhook receiver.

    Accepts the completed scrape payload, normalizes the job data,
    and stores it in the in-memory data store.
    """
    try:
        body = await request.json()

        # Bright Data may send data as a top-level list or nested in a 'data' key
        if isinstance(body, list):
            raw_jobs = body
        elif isinstance(body, dict):
            raw_jobs = body.get("data", body.get("results", []))
        else:
            logger.warning("Unexpected webhook payload type: %s", type(body))
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid payload format"},
            )

        # Normalize and store — but never wipe the store with an empty payload
        normalized = normalize_payload(raw_jobs)

        if not normalized:
            logger.warning(
                "Webhook received %d raw jobs but 0 normalized — ignoring to preserve existing %d jobs",
                len(raw_jobs),
                data_store.job_count,
            )
            return {"status": "ignored", "reason": "empty payload", "jobs_received": 0}

        data_store.replace_all(normalized)

        logger.info(
            "Webhook processed: %d raw jobs → %d normalized",
            len(raw_jobs),
            len(normalized),
        )

        return {"status": "ok", "jobs_received": len(normalized)}

    except Exception as exc:
        logger.error("Webhook processing failed: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"error": f"Processing failed: {str(exc)}"},
        )
