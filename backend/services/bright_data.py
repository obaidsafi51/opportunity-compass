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
import json
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
SCRAPE_URL = f"{BASE_URL}/scraper"          # synchronous — returns data inline
SNAPSHOT_URL = f"{BASE_URL}/snapshot"       # GET /snapshot/<snapshot_id>
PROGRESS_URL = f"{BASE_URL}/progress"      # GET /progress/<snapshot_id>

# Polling configuration
POLL_INTERVAL_SECONDS = 10
POLL_MAX_ATTEMPTS = 60  # 60 × 10s = 10 minutes max wait


def _parse_ndjson(text: str) -> list[dict[str, Any]]:
    """Parse newline-delimited JSON (NDJSON) text into a list of dicts."""
    results = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line:
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                logger.warning("Skipping malformed NDJSON line: %s", line[:100])
    return results


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
    keyword_search: str = "Jobs",
    location: str = "Montgomery, AL",
    date_posted: str = "Last 14 days",
    posted_by: str = "Employer",
) -> dict[str, Any] | None:
    """
    Trigger an async scrape job on Bright Data (Indeed Jobs dataset).

    Args:
        notify_url:      If provided, Bright Data will POST the completed payload
                         to this URL (webhook mode). If None, use polling mode.
        keyword_search:  Search keyword for Indeed (e.g., "jobs", "nursing", "warehouse").
        location:        Geographic filter for job postings.
        date_posted:     Indeed date filter (e.g., "Last 14 days", "Last 7 days").
        posted_by:       Filter by poster type (e.g., "Employer").

    Returns:
        API response dict containing `snapshot_id` (and other metadata),
        or None on failure.
    """
    if not settings.is_bright_data_configured:
        logger.warning("Bright Data not configured — skipping scrape trigger")
        return None

    # Build the input row matching the Indeed scraper configuration
    input_row: dict[str, Any] = {
        "country": "US",
        "domain": "indeed.com",
        "keyword_search": keyword_search,
        "location": location,
        "location_radius": "",
    }
    if date_posted:
        input_row["date_posted"] = date_posted
    if posted_by:
        input_row["posted_by"] = posted_by

    body: dict[str, Any] = {
        "input": [input_row],
    }

    # Query parameters — dataset_id and options go here, not in the body
    params: dict[str, str] = {
        "dataset_id": settings.bright_data_dataset_id,
        "include_errors": "true",
        "type": "discover_new",
        "discover_by": "keyword",
        "limit_per_input": "100",
    }
    if notify_url:
        params["notify"] = notify_url
    else:
        params["notify"] = "false"

    # Build the full URL with query params (matching the Bright Data docs exactly)
    url = f"{SCRAPE_URL}?" + "&".join(f"{k}={v}" for k, v in params.items())
    headers = {
        "Authorization": f"Bearer {settings.bright_data_api_key}",
        "Content-Type": "application/json",
    }

    logger.info("Bright Data request URL: %s", url)
    logger.info("Bright Data request body: %s", json.dumps(body))

    # /scraper endpoint is synchronous — blocks until data is ready (can take minutes)
    timeout = 300 if not notify_url else 60

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, headers=headers, content=json.dumps(body))
            logger.info("Bright Data response status: %s", resp.status_code)
            logger.info("Bright Data response body (first 500 chars): %s", resp.text[:500])
            resp.raise_for_status()

            # Try parsing as standard JSON first (webhook mode returns {"snapshot_id": "..."})
            try:
                data = resp.json()
                # If it's a dict with snapshot_id, it's an async trigger response
                if isinstance(data, dict) and "snapshot_id" in data:
                    logger.info("Bright Data scrape triggered (async): %s", data)
                    return data
                # If it's a list, it's inline data
                if isinstance(data, list):
                    logger.info("Bright Data returned %d jobs inline (JSON array)", len(data))
                    return {"_inline_data": data}
                # Single dict that's a job record
                if isinstance(data, dict) and ("job_title" in data or "company_name" in data):
                    logger.info("Bright Data returned 1 job inline")
                    return {"_inline_data": [data]}
                # Unknown format, return as-is
                return data
            except json.JSONDecodeError:
                # NDJSON format — Bright Data returns one JSON object per line
                jobs = _parse_ndjson(resp.text)
                if jobs:
                    logger.info("Bright Data returned %d jobs inline (NDJSON)", len(jobs))
                    return {"_inline_data": jobs}
                logger.warning("Failed to parse Bright Data response as JSON or NDJSON")
                return None

    except httpx.HTTPStatusError as exc:
        logger.error(
            "Bright Data trigger HTTP error %s: %s",
            exc.response.status_code,
            exc.response.text[:500],
        )
        return None
    except Exception as exc:
        logger.error(
            "Failed to trigger Bright Data scrape: [%s] %s",
            type(exc).__name__,
            exc,
        )
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
            try:
                data = resp.json()
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("data", data.get("results", []))
                return []
            except json.JSONDecodeError:
                # NDJSON format
                jobs = _parse_ndjson(resp.text)
                logger.info("Downloaded %d jobs from snapshot (NDJSON)", len(jobs))
                return jobs if jobs else []
    except httpx.HTTPError as exc:
        logger.error("Failed to download snapshot %s: %s", snapshot_id, exc)
        return None


# ---------------------------------------------------------------------------
# Full polling workflow: trigger → poll → download
# ---------------------------------------------------------------------------

async def trigger_and_poll(
    keyword_search: str = "Jobs",
    location: str = "Montgomery, AL",
    date_posted: str = "Last 14 days",
    posted_by: str = "Employer",
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
    result = await trigger_scrape(
        notify_url=None,
        keyword_search=keyword_search,
        location=location,
        date_posted=date_posted,
        posted_by=posted_by,
    )
    if not result:
        logger.error("Polling workflow aborted — trigger failed")
        return None

    # Check if Bright Data returned data inline (notify=false can do this)
    if "_inline_data" in result:
        raw_jobs = result["_inline_data"]
        logger.info("Polling workflow skipped — got %d jobs inline from trigger", len(raw_jobs))
        return raw_jobs

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
