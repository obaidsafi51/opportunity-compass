"""
API router — primary REST endpoints.

All data endpoints follow the PRD's response envelope:
  { data: T | null, error: string | null, source: "live" | "cached" }
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Query

from models.schemas import (
    Barriers,
    DataSource,
    GapRow,
    GrowthSignal,
    OpportunityCard,
    PersonaType,
    ProgramCard,
    ResponseEnvelope,
    SkillRow,
    SummaryResponse,
)
from services.civic_data import fetch_demographics, fetch_growth_signals
from services.data_store import data_store
from services.gaps_analysis import get_top_skills, get_training_gaps
from services.programs_db import get_all_programs
from services.wage_utils import apply_wage_floor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])


# ---------------------------------------------------------------------------
# GET /api/summary
# ---------------------------------------------------------------------------

@router.get("/summary", response_model=ResponseEnvelope[SummaryResponse])
async def get_summary():
    """
    Municipal overview data — population, unemployment, total jobs, income, poverty.
    Powers the header Overview Strip.
    """
    try:
        demographics = await fetch_demographics()
        summary = SummaryResponse(
            population=demographics.get("population", 200_603),
            unemployment_rate=demographics.get("unemployment_rate", 2.7),
            total_open_jobs=data_store.job_count or demographics.get("total_open_jobs", 0),
            median_income=demographics.get("median_income", 57_300),
            poverty_rate=demographics.get("poverty_rate", 19.7),
        )
        source = DataSource.CACHED if data_store.is_using_seed_data else DataSource.LIVE
        return ResponseEnvelope(data=summary, source=source)
    except Exception as exc:
        logger.error("Error in /api/summary: %s", exc)
        return ResponseEnvelope(error=str(exc), source=DataSource.CACHED)


# ---------------------------------------------------------------------------
# GET /api/skills
# ---------------------------------------------------------------------------

@router.get("/skills", response_model=ResponseEnvelope[list[SkillRow]])
async def get_skills():
    """
    Top 8–10 skills by posting volume for the Skills Heatmap.
    Aggregated from job store data.
    """
    try:
        # Implement real aggregation from data_store jobs
        jobs = data_store.get_all_jobs()
        skills = get_top_skills(jobs, limit=10)
        source = DataSource.CACHED if data_store.is_using_seed_data else DataSource.LIVE
        return ResponseEnvelope(data=skills, source=source)
    except Exception as exc:
        logger.error("Error in /api/skills: %s", exc)
        return ResponseEnvelope(data=[], error=str(exc), source=DataSource.CACHED)


# ---------------------------------------------------------------------------
# GET /api/gaps
# ---------------------------------------------------------------------------

@router.get("/gaps", response_model=ResponseEnvelope[list[GapRow]])
async def get_gaps():
    """
    Training deficit analysis — 3-5 occupations with severity labels.
    Powers the Training Deficit Panel.
    """
    try:
        # Implement real gap analysis
        jobs = data_store.get_all_jobs()
        gaps = get_training_gaps(jobs, limit=5)
        source = DataSource.CACHED if data_store.is_using_seed_data else DataSource.LIVE
        return ResponseEnvelope(data=gaps, source=source)
    except Exception as exc:
        logger.error("Error in /api/gaps: %s", exc)
        return ResponseEnvelope(data=[], error=str(exc), source=DataSource.CACHED)


# ---------------------------------------------------------------------------
# GET /api/opportunities?persona=<general|ltu|neet>
# ---------------------------------------------------------------------------

@router.get("/opportunities", response_model=ResponseEnvelope[list[OpportunityCard]])
async def get_opportunities(
    persona: PersonaType = Query(PersonaType.GENERAL, description="Filter by persona type"),
):
    """
    Persona-filtered reachable roles — top 3 role cards per persona.
    Powers the Opportunity Navigator right panel.
    """
    try:
        jobs = data_store.get_all_jobs()
        
        # 1. Filter by Persona Reachability
        filtered = []
        for j in jobs:
            # We only want analyzed jobs for these specific views if requesting a persona
            if persona == PersonaType.NEET:
                if getattr(j, "neet_reachable", False) is True:
                    filtered.append(j)
            elif persona == PersonaType.LTU:
                if getattr(j, "ltu_reachable", False) is True:
                    filtered.append(j)
            else:
                filtered.append(j)
                
        # 2. Apply $15 Wage Floor Minimum
        filtered = apply_wage_floor(filtered)
        
        # 3. Aggregate into Opportunity Cards (grouped by title to show demand_count)
        # Sort by title, take first seen as canonical base for AI strings
        grouped = {}
        for j in filtered:
            title = j.job_title
            if title not in grouped:
                # Decide which fit string to use based on Persona
                fit = j.neet_fit_reason if persona == PersonaType.NEET else j.ltu_fit_reason
                if not fit:
                    fit = "Matches your current experience level." if persona != PersonaType.GENERAL else ""
                    
                grouped[title] = OpportunityCard(
                    job_title=title,
                    fit_reason=fit,
                    wage_range=j.estimated_wage_range or j.salary or "Unknown",
                    training_weeks=j.training_duration_weeks or 0,
                    demand_count=1,
                    barriers=Barriers(
                        requires_degree=bool(j.requires_degree),
                        requires_vehicle=bool(j.requires_vehicle),
                        requires_experience_1yr=bool(j.requires_experience_1yr),
                        requires_recent_certification=bool(j.requires_recent_certification),
                        requires_continuous_work_history=bool(j.requires_continuous_work_history),
                    )
                )
            else:
                grouped[title].demand_count += 1
                
        # Sort by highest demand, take top 20
        sorted_opps = sorted(grouped.values(), key=lambda x: x.demand_count, reverse=True)[:20]

        source = DataSource.CACHED if data_store.is_using_seed_data else DataSource.LIVE
        return ResponseEnvelope(data=sorted_opps, source=source)
    except Exception as exc:
        logger.error("Error in /api/opportunities: %s", exc)
        return ResponseEnvelope(data=[], error=str(exc), source=DataSource.CACHED)


# ---------------------------------------------------------------------------
# GET /api/programs
# ---------------------------------------------------------------------------

@router.get("/programs", response_model=ResponseEnvelope[list[ProgramCard]])
async def get_programs():
    """
    All local training programs (Montgomery).
    Powers the Pathways Recommender and Aligned Programs strip.
    """
    try:
        programs = get_all_programs()
        source = DataSource.CACHED if data_store.is_using_seed_data else DataSource.LIVE
        return ResponseEnvelope(data=programs, source=source)
    except Exception as exc:
        logger.error("Error in /api/programs: %s", exc)
        return ResponseEnvelope(data=[], error=str(exc), source=DataSource.CACHED)


# ---------------------------------------------------------------------------
# GET /api/growth-signals
# ---------------------------------------------------------------------------

@router.get("/growth-signals", response_model=ResponseEnvelope[list[GrowthSignal]])
async def get_growth_signals():
    """
    New business licenses & permits by sector.
    Provides leading economic indicators.
    """
    try:
        raw = await fetch_growth_signals()
        signals = [GrowthSignal(**item) for item in raw]
        return ResponseEnvelope(data=signals, source=DataSource.CACHED)
    except Exception as exc:
        logger.error("Error in /api/growth-signals: %s", exc)
        return ResponseEnvelope(data=[], error=str(exc), source=DataSource.CACHED)
