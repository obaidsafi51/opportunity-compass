"""
In-memory data store for jobs and cached analysis results.

This module acts as the central data repository during the MVP.
In production, this would be replaced by a proper database.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from models.schemas import NormalizedJob

logger = logging.getLogger(__name__)

# Path to seed data file (relative to backend root)
SEED_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "seed-jobs.json"


class DataStore:
    """Thread-safe in-memory store for normalized job data."""

    def __init__(self) -> None:
        self._jobs: list[NormalizedJob] = []
        self._using_seed: bool = False

    @property
    def job_count(self) -> int:
        return len(self._jobs)

    @property
    def is_using_seed_data(self) -> bool:
        return self._using_seed

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    def get_all_jobs(self) -> list[NormalizedJob]:
        """Return all stored jobs."""
        return list(self._jobs)

    def add_jobs(self, jobs: list[NormalizedJob]) -> int:
        """Add normalized jobs to the store. Returns count added."""
        self._jobs.extend(jobs)
        logger.info("Added %d jobs to store (total: %d)", len(jobs), self.job_count)
        return len(jobs)

    def replace_all(self, jobs: list[NormalizedJob]) -> None:
        """Replace the entire job store (used on webhook delivery)."""
        self._jobs = list(jobs)
        self._using_seed = False
        logger.info("Replaced job store with %d jobs", self.job_count)

    def clear(self) -> None:
        """Clear all stored jobs."""
        self._jobs.clear()
        self._using_seed = False

    # ------------------------------------------------------------------
    # Seed data fallback
    # ------------------------------------------------------------------

    def load_seed_data(self, path: Optional[Path] = None) -> int:
        """
        Load jobs from the seed JSON file as a fallback.
        Returns the number of jobs loaded.
        """
        seed_path = path or SEED_DATA_PATH
        if not seed_path.exists():
            logger.warning("Seed data file not found at %s", seed_path)
            return 0

        try:
            raw = json.loads(seed_path.read_text(encoding="utf-8"))
            jobs = [NormalizedJob(**item) for item in raw]
            self._jobs = jobs
            self._using_seed = True
            logger.info("Loaded %d jobs from seed data", len(jobs))
            return len(jobs)
        except Exception as exc:
            logger.error("Failed to load seed data: %s", exc)
            return 0


# ---------------------------------------------------------------------------
# Singleton instance
# ---------------------------------------------------------------------------
data_store = DataStore()
