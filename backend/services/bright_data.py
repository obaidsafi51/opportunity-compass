"""
Bright Data Web Scraper API client.

Implements two delivery strategies from the PRD:
  1. **Webhook** (primary) — trigger scrape with `notify` URL → Bright Data
     POSTs the completed payload to our `/webhook/jobs` endpoint.
  2. **Polling** (fallback) — trigger scrape → poll snapshot status →
     download completed snapshot JSON.

Also handles normalization of raw Bright Data payloads into the internal
NormalizedJob schema.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from config import settings
from models.schemas import NormalizedJob

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bright Data API endpoints
# ---------------------------------------------------------------------------
BASE_URL = "https://api.brightdata.com/datasets/v3"
TRIGGER_URL = f"{BASE_URL}/trigger"
SNAPSHOT_URL = f"{BASE_URL}/snapshot"       # GET /snapshot/<snapshot_id>
PROGRESS_URL = f"{BASE_URL}/progress"      # GET /progress/<snapshot_id>

# Polling configuration
POLL_INTERVAL_SECONDS = 10
POLL_MAX_ATTEMPTS = 60  # 60 × 10s = 10 minutes max wait


def _auth_headers() -> dict[str, str]:
    """Return authorization headers for Bright Data API."""
    return {
        "Authorization": f"Bearer {settings.bright_data_api_key}",
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# Trigger
# ---------------------------------------------------------------------------

async def trigger_scrape(
    notify_url: str | None = None,
    location: str = "Montgomery, AL",
    days_posted: int = 30,
) -> dict[str, Any] | None:
    """
    Trigger an async scrape job on Bright Data.

    Args:
        notify_url: If provided, Bright Data will POST the completed payload
                    to this URL (webhook mode). If None, use polling mode.
        location:   Geographic filter for job postings.
        days_posted: Only include postings from the last N days.

    Returns:
        API response dict containing `snapshot_id` (and other metadata),
        or None on failure.
    """
    if not settings.is_bright_data_configured:
        logger.warning("Bright Data not configured — skipping scrape trigger")
        return None

    body: dict[str, Any] = {
        "dataset_id": settings.bright_data_dataset_id,
        "format": "json",
        "filters": {
            "location": location,
            "days_posted": days_posted,
        },
    }
    if notify_url:
        body["notify"] = notify_url

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(TRIGGER_URL, headers=_auth_headers(), json=body)
            resp.raise_for_status()
            data = resp.json()
            logger.info("Bright Data scrape triggered: %s", data)
            return data
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Bright Data trigger HTTP error %s: %s",
            exc.response.status_code,
            exc.response.text[:500],
        )
        return None
    except httpx.HTTPError as exc:
        logger.error("Failed to trigger Bright Data scrape: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Polling — check snapshot status
# ---------------------------------------------------------------------------

async def get_snapshot_status(snapshot_id: str) -> dict[str, Any] | None:
    """
    Poll the progress of a snapshot.

    Returns:
        Dict with at minimum a `status` key. Possible statuses include:
        "running", "ready", "failed".
        Returns None on request failure.
    """
    if not settings.is_bright_data_configured:
        return None

    url = f"{PROGRESS_URL}/{snapshot_id}"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=_auth_headers())
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as exc:
        logger.error("Failed to poll snapshot %s: %s", snapshot_id, exc)
        return None


async def download_snapshot(snapshot_id: str) -> list[dict[str, Any]] | None:
    """
    Download the completed snapshot data.

    Returns:
        List of raw job dicts, or None on failure.
    """
    if not settings.is_bright_data_configured:
        return None

    url = f"{SNAPSHOT_URL}/{snapshot_id}"
    params = {"format": "json"}
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(url, headers=_auth_headers(), params=params)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return data.get("data", data.get("results", []))
            return []
    except httpx.HTTPError as exc:
        logger.error("Failed to download snapshot %s: %s", snapshot_id, exc)
        return None


# ---------------------------------------------------------------------------
# Full polling workflow: trigger → poll → download
# ---------------------------------------------------------------------------

async def trigger_and_poll(
    location: str = "Montgomery, AL",
    days_posted: int = 30,
) -> list[dict[str, Any]] | None:
    """
    Complete polling workflow:
      1. Trigger a scrape (no webhook)
      2. Poll until status is 'ready'
      3. Download the snapshot data

    Returns:
        List of raw job dicts, or None if any step fails.
    """
    # Step 1: Trigger
    result = await trigger_scrape(notify_url=None, location=location, days_posted=days_posted)
    if not result:
        logger.error("Polling workflow aborted — trigger failed")
        return None

    snapshot_id = result.get("snapshot_id")
    if not snapshot_id:
        logger.error("No snapshot_id in trigger response: %s", result)
        return None

    logger.info("Polling workflow started — snapshot_id: %s", snapshot_id)

    # Step 2: Poll for completion
    for attempt in range(1, POLL_MAX_ATTEMPTS + 1):
        await asyncio.sleep(POLL_INTERVAL_SECONDS)

        status_data = await get_snapshot_status(snapshot_id)
        if status_data is None:
            logger.warning("Poll attempt %d/%d — no response", attempt, POLL_MAX_ATTEMPTS)
            continue

        status = status_data.get("status", "unknown")
        logger.info(
            "Poll attempt %d/%d — status: %s",
            attempt, POLL_MAX_ATTEMPTS, status,
        )

        if status == "ready":
            break
        elif status == "failed":
            logger.error("Snapshot %s failed: %s", snapshot_id, status_data)
            return None
    else:
        logger.error("Polling timed out after %d attempts for snapshot %s", POLL_MAX_ATTEMPTS, snapshot_id)
        return None

    # Step 3: Download
    raw_jobs = await download_snapshot(snapshot_id)
    if raw_jobs is None:
        logger.error("Failed to download snapshot %s", snapshot_id)
        return None

    logger.info("Polling workflow complete — downloaded %d raw jobs", len(raw_jobs))
    return raw_jobs


# ---------------------------------------------------------------------------
# Normalization — raw Bright Data payload → internal schema
# ---------------------------------------------------------------------------

def normalize_job(raw: dict[str, Any]) -> NormalizedJob:
    """
    Normalize a single raw Bright Data job payload into our internal schema.

    Handles common field name variations across different Bright Data
    dataset schemas (indeed, linkedin, glassdoor, etc.).
    """
    return NormalizedJob(
        job_title=_first(raw, "job_title", "title", "position", default="Unknown"),
        company_name=_first(raw, "company_name", "company", "employer", default=""),
        job_location=_first(raw, "job_location", "location", "city", default=""),
        description=_first(raw, "description", "job_description", "full_description", default=""),
        timestamp=_first(raw, "timestamp", "date_posted", "posted_at", "date", default=""),
        salary=raw.get("salary") or raw.get("salary_range") or raw.get("compensation"),
        job_type=_first(raw, "job_type", "employment_type", "type", default=""),
        url=_first(raw, "url", "job_url", "apply_url", "link", default=""),
    )


def normalize_payload(raw_jobs: list[dict[str, Any]]) -> list[NormalizedJob]:
    """Normalize an entire Bright Data payload into internal job objects."""
    normalized = []
    for raw in raw_jobs:
        try:
            normalized.append(normalize_job(raw))
        except Exception as exc:
            logger.warning("Skipping malformed job entry: %s", exc)
    logger.info("Normalized %d / %d raw jobs", len(normalized), len(raw_jobs))
    return normalized


def _first(d: dict, *keys: str, default: Any = "") -> Any:
    """Return the first non-None value from a dict for the given keys."""
    for key in keys:
        val = d.get(key)
        if val is not None:
            return val
    return default
