"""
Pydantic models for API request/response schemas.

All API endpoints use the standard ResponseEnvelope wrapper
to provide consistent { data, error, source } responses.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Generic response envelope
# ---------------------------------------------------------------------------

T = TypeVar("T")


class DataSource(str, Enum):
    """Indicates where the data originated."""
    LIVE = "live"
    CACHED = "cached"


class ResponseEnvelope(BaseModel, Generic[T]):
    """
    Standard API response wrapper.
    All endpoints return this shape: { data, error, source }.
    """
    data: T | None = None
    error: str | None = None
    source: DataSource = DataSource.LIVE


# ---------------------------------------------------------------------------
# Summary / Overview
# ---------------------------------------------------------------------------

class SummaryResponse(BaseModel):
    """Municipal overview stats for the header strip."""
    population: int = Field(..., description="Total population")
    unemployment_rate: float = Field(..., description="Unemployment rate as percentage")
    total_open_jobs: int = Field(..., description="Total active job postings")
    median_income: int = Field(..., description="Median household income in USD")
    poverty_rate: float = Field(..., description="Poverty rate as percentage")


# ---------------------------------------------------------------------------
# Skills Heatmap
# ---------------------------------------------------------------------------

class SkillRow(BaseModel):
    """Single row in the skills heatmap."""
    skill: str
    count: int = Field(..., description="Number of active postings")
    pct_change: float = Field(..., description="Percentage change vs. prior period")
    is_rising: bool = Field(False, description="True if ≥25% surge")


# ---------------------------------------------------------------------------
# Training Gaps / Deficits
# ---------------------------------------------------------------------------

class Severity(str, Enum):
    BALANCED = "balanced"
    EMERGING = "emerging"
    ACUTE = "acute"


class AlignedProgram(BaseModel):
    """A training program aligned to a deficit."""
    name: str
    provider: str


class GapRow(BaseModel):
    """Single occupation in the training deficit analysis."""
    occupation: str
    severity: Severity
    aligned_programs: list[AlignedProgram] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Opportunities / Role Cards
# ---------------------------------------------------------------------------

class Barriers(BaseModel):
    """Boolean barrier flags from Gemini analysis."""
    requires_degree: bool = False
    requires_vehicle: bool = False
    requires_experience_1yr: bool = False
    requires_recent_certification: bool = False
    requires_continuous_work_history: bool = False


class OpportunityCard(BaseModel):
    """A single reachable role card for the Opportunity Navigator."""
    job_title: str
    fit_reason: str = Field("", description="AI-generated persona-specific fit explanation")
    wage_range: str = Field("", description="Estimated wage range string")
    training_weeks: int = Field(0, description="Estimated weeks of training")
    demand_count: int = Field(0, description="Number of active postings")
    programs: list[ProgramCard] = Field(default_factory=list)
    barriers: Barriers = Field(default_factory=Barriers)


class PersonaType(str, Enum):
    GENERAL = "general"
    LTU = "long_term_unemployed"
    NEET = "neet_youth"


# ---------------------------------------------------------------------------
# Programs
# ---------------------------------------------------------------------------

class ProgramCard(BaseModel):
    """Local training program recommendation."""
    name: str
    provider: str
    benefit: str = Field("", description="Key benefit description")
    eligibility: str = Field("", description="Eligibility match text")
    sectors: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Growth Signals
# ---------------------------------------------------------------------------

class GrowthSignal(BaseModel):
    """Business license / permit growth signal by sector."""
    sector: str
    new_licenses: int = 0
    permits: int = 0
    trend: str = ""  # e.g. "rising", "stable", "declining"


# ---------------------------------------------------------------------------
# Webhook
# ---------------------------------------------------------------------------

class WebhookPayload(BaseModel):
    """
    Incoming payload from Bright Data webhook.
    Flexible model — accepts arbitrary job data.
    """
    data: list[dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal Job Schema (normalised from Bright Data)
# ---------------------------------------------------------------------------

class NormalizedJob(BaseModel):
    """Internal normalized job representation."""
    job_title: str
    company_name: str = ""
    job_location: str = ""
    description: str = ""
    timestamp: str = ""
    salary: str | None = None
    job_type: str = ""
    url: str = ""

    # Fields populated by Gemini analysis
    requires_degree: bool | None = None
    requires_vehicle: bool | None = None
    requires_experience_1yr: bool | None = None
    requires_recent_certification: bool | None = None
    requires_continuous_work_history: bool | None = None
    estimated_wage_range: str | None = None
    training_duration_weeks: int | None = None
    extracted_skills: list[str] = Field(default_factory=list)
    neet_reachable: bool | None = None
    ltu_reachable: bool | None = None
    neet_fit_reason: str | None = None
    ltu_fit_reason: str | None = None
    category: str | None = None
