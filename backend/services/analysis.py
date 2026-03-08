"""
Orchestrates the job analysis pipeline: running Gemini batch processing
on unanalyzed jobs in the data store.
"""

from __future__ import annotations

import asyncio
import logging

from config import settings
from services.data_store import data_store
from services.gemini import analyze_jobs

logger = logging.getLogger(__name__)

async def run_analysis_pipeline(limit: int = 50) -> None:
    """
    Find unanalyzed jobs in the data store and run them through Gemini.
    Updates the jobs in the store in-place.
    
    Args:
        limit: Max number of jobs to analyze in this run (to respect API limits).
    """
    if not settings.is_gemini_configured:
        logger.info("Gemini not configured — skipping analysis pipeline")
        return

    # Identify jobs that haven't been analyzed yet
    # (Checking one of the fields that Gemini populates)
    unprocessed = [j for j in data_store._jobs if j.requires_degree is None][:limit]
    
    if not unprocessed:
        logger.info("All jobs already analyzed. Pipeline complete.")
        return
        
    logger.info("Starting analysis pipeline for %d jobs", len(unprocessed))
    
    # Prepare batch for Gemini
    payloads = [
        {
            "job_title": j.job_title,
            "description": f"{j.job_title} at {j.company_name}\n\n{j.description}",
        }
        for j in unprocessed
    ]
    
    # Run analysis mapping
    results = await analyze_jobs(payloads, batch_size=5)
    
    # Zip results safely and mutate DataStore items
    updated_count = 0
    for job, res in zip(unprocessed, results):
        if not res:
            logger.warning("No result returned for job: %s", job.job_title)
            continue
            
        job.requires_degree = res.get("requires_degree")
        job.requires_vehicle = res.get("requires_vehicle")
        job.requires_experience_1yr = res.get("requires_experience_1yr")
        job.requires_recent_certification = res.get("requires_recent_certification")
        job.requires_continuous_work_history = res.get("requires_continuous_work_history")
        job.estimated_wage_range = res.get("estimated_wage_range")
        job.training_duration_weeks = res.get("training_duration_weeks")
        job.extracted_skills = res.get("extracted_skills", [])
        job.neet_reachable = res.get("neet_reachable")
        job.ltu_reachable = res.get("ltu_reachable")
        job.neet_fit_reason = res.get("neet_fit_reason")
        job.ltu_fit_reason = res.get("ltu_fit_reason")
        job.category = res.get("category")
        
        updated_count += 1
        
    logger.info("Analysis pipeline complete. Updated %d jobs.", updated_count)
