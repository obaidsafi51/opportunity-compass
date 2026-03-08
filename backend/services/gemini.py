"""
Google Gemini API client for job description analysis.

Sends job descriptions to Gemini for structured cognitive matching,
producing persona-aware evaluation data for the Opportunity Navigator.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from google import genai
from google.genai import types
from pydantic import BaseModel

from config import settings

logger = logging.getLogger(__name__)

# Gemini model to use — 1.5-flash has separate quota pool and generous free limits
MODEL_NAME = "gemini-1.5-flash"

# System prompt from PRD §9.3
SYSTEM_PROMPT = """You are an expert workforce development AI agent operating exclusively within the municipal context of Montgomery, Alabama. Your task is to analyze job description text and evaluate suitability for specific workforce personas.

For each job description, you must evaluate against these criteria and return structured JSON:

1. requires_degree (Boolean): Does the text require a university/college degree?
2. requires_vehicle (Boolean): Does the text require a personal vehicle or driver's license?
3. requires_experience_1yr (Boolean): Does the text require more than 1 year of prior professional experience?
4. requires_recent_certification (Boolean): Does the text require certifications obtained within the last 2 years?
5. requires_continuous_work_history (Boolean): Does the text imply need for uninterrupted recent employment?
6. estimated_wage_range (String): Extract stated wage or estimate based on Montgomery market rates.
7. training_duration_weeks (Integer): Estimated weeks of training to become job-ready for someone with no prior experience.
8. extracted_skills (Array<String>): Top 3-5 skills required.
9. neet_reachable (Boolean): True if requires_degree == false AND requires_experience_1yr == false.
10. ltu_reachable (Boolean): True if requires_recent_certification == false AND requires_continuous_work_history == false.
11. neet_fit_reason (String): One sentence explaining why this role fits NEET youth. Only generate if neet_reachable == true.
12. ltu_fit_reason (String): One sentence explaining why this role fits long-term unemployed adults. Only generate if ltu_reachable == true.
13. category (String): Occupational category (e.g., "Healthcare", "Construction", "Customer Service").

Output strictly as JSON. Do not include any text outside the JSON object.

--- PERSONA-SPECIFIC TONE & LANGUAGE RULES ---

All generated copy (fit_reason, program descriptions, etc.) MUST follow these rules.

For Long-Term Unemployed (LTU) personas:
  DO:  Use language that conveys dignity, agency, and fresh starts.
       Example: "This role values reliability and life experience."
  DON'T: Use the words "upskill" or "pivot" — these feel corporate/dismissive.
  DON'T: Frame unemployment as a personal failure.

For NEET Youth personas:
  DO:  Use energetic, forward-looking language that emphasizes opportunity
       and immediate income. Example: "Earn while you learn — no degree needed."
  DON'T: Use the phrase "at-risk youth" — this is stigmatizing.
  DON'T: Use condescending or paternalistic language.

General tone across all personas:
  - Write at an 8th-grade reading level.
  - Prefer active voice and short sentences.
  - Avoid jargon, acronyms, and policy-speak.
  - Never say "low-skilled" — say "entry-level" or "no experience required."
"""

class JobAnalysis(BaseModel):
    requires_degree: bool
    requires_vehicle: bool
    requires_experience_1yr: bool
    requires_recent_certification: bool
    requires_continuous_work_history: bool
    estimated_wage_range: str
    training_duration_weeks: int
    extracted_skills: list[str]
    neet_reachable: bool
    ltu_reachable: bool
    neet_fit_reason: str | None
    ltu_fit_reason: str | None
    category: str

class BatchAnalysisResponse(BaseModel):
    jobs: list[JobAnalysis]

async def _process_batch_with_retry(
    client: genai.Client,
    descriptions_chunk: list[dict[str, str]],
    max_retries: int = 4
) -> list[dict[str, Any]]:
    """Process a single chunk of jobs with exponential backoff for rate limits."""
    # Format the prompt
    batch_json = json.dumps(descriptions_chunk, indent=2)
    prompt = f"Analyze the following batch of job descriptions. Respond strictly with formatted JSON matching the supplied schema.\n\n{batch_json}"

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.1,
        response_mime_type="application/json",
        response_schema=BatchAnalysisResponse,
    )

    for attempt in range(max_retries):
        try:
            response = await client.aio.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=config,
            )
            
            text_resp = response.text
            if not text_resp:
                raise ValueError("Empty response from Gemini")
                
            parsed = json.loads(text_resp)
            return parsed.get("jobs", [])
            
        except Exception as exc:
            exc_str = str(exc)
            logger.error("Gemini error (attempt %d/%d): %s", attempt+1, max_retries, exc_str)
            if "429" in exc_str or "quota" in exc_str.lower() or "resource" in exc_str.lower():
                wait_time = 2 ** attempt * 8  # 8s, 16s, 32s, 64s
                logger.warning("Gemini API rate limited. Retrying batch in %ds... (Attempt %d/%d)", wait_time, attempt+1, max_retries)
                await asyncio.sleep(wait_time)
            elif attempt < max_retries - 1:
                logger.warning("Gemini API error: %s. Retrying... (Attempt %d)", exc, attempt+1)
                await asyncio.sleep(2)
            else:
                logger.error("Failed to analyze batch after %d attempts: %s", max_retries, exc)
                return []
    
    return []

async def analyze_jobs(descriptions: list[dict[str, str]], batch_size: int = 5) -> list[dict[str, Any]]:
    """
    Send a batch of job descriptions to Gemini for structured analysis.

    Args:
        descriptions: List of dicts with at minimum a 'description' key
                      and optionally 'job_title'.
        batch_size: Number of descriptions to send in one API call.

    Returns:
        List of structured analysis results (one per job).
    """
    if not settings.is_gemini_configured:
        logger.warning("Gemini API key not configured — returning empty results")
        return []

    client = genai.Client(api_key=settings.gemini_api_key)
    logger.info("Starting Gemini analysis for %d jobs with batch size %d", len(descriptions), batch_size)
    
    results = []
    
    for i in range(0, len(descriptions), batch_size):
        chunk = descriptions[i:i + batch_size]
        logger.info("Processing batch %d (jobs %d to %d)...", (i//batch_size)+1, i, min(i+batch_size, len(descriptions)))
        
        batch_results = await _process_batch_with_retry(client, chunk)
        
        if len(batch_results) == len(chunk):
            results.extend(batch_results)
        else:
            logger.warning("Batch returned %d results, expected %d. Some data may be unaligned.", len(batch_results), len(chunk))
            # Extend whatever we managed to extract
            results.extend(batch_results)
            
        if i + batch_size < len(descriptions):
            await asyncio.sleep(1)  # Throttling between sequential calls

    logger.info("Finished Gemini analysis. Total extracted models: %d", len(results))
    return results
