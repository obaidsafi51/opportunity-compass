"""
Utility for parsing and filtering wages on analyzed jobs.
Provides the $15/hr living wage floor logic mandated by the PRD.
"""

import re
from typing import Sequence

from models.schemas import NormalizedJob


def parse_hourly_rate(wage_str: str | None) -> float | None:
    """
    Attempt to extract a numeric hourly rate from a free-text wage string.
    e.g., "$14-18/hr" -> 16.0 (average)
          "$16.50/hour" -> 16.5
          "$35,000/yr" -> 16.82 (assuming 2080 hrs)
    """
    if not wage_str:
        return None

    s = wage_str.lower().replace(",", "")
    
    # Check for direct hourly numeric pairs like "$14-18" or "14 - 18"
    hourly_range = re.findall(r"(?:^|\$| )(\d+(?:\.\d+)?)(?:\s*-\s*|\s+to\s+)(?:$|\$| )?(\d+(?:\.\d+)?)(?:/hr|/hour| per hour)?", s)
    if hourly_range:
        low, high = float(hourly_range[0][0]), float(hourly_range[0][1])
        # If the numbers look like annual salaries but missing K (e.g. 30000), skip logic or parse
        if low < 150:
            return (low + high) / 2.0

    # Check for single hourly numeric
    hourly_single = re.findall(r"(?:^|\$| )(\d+(?:\.\d+)?)(?:/hr|/hour| per hour)", s)
    if hourly_single:
        val = float(hourly_single[0])
        if val < 150:
            return val
            
    # Check annual
    annual_range = re.findall(r"(?:^|\$| )(\d{4,6})(?:\s*-\s*|\s+to\s+)(?:$|\$| )?(\d{4,6})(?:/yr|/year| per year)?", s)
    if annual_range:
        low, high = float(annual_range[0][0]), float(annual_range[0][1])
        return ((low + high) / 2.0) / 2080.0
        
    annual_single = re.findall(r"(?:^|\$| )(\d{4,6})(?:/yr|/year| per year)?", s)
    if annual_single:
        return float(annual_single[0]) / 2080.0

    return None

def apply_wage_floor(jobs: Sequence[NormalizedJob], floor: float = 15.0) -> list[NormalizedJob]:
    """
    Filter out jobs strictly below the wage floor.
    If a job's wage cannot be parsed, it is INCLUDED in the results (err on the side of showing).
    If the resulting filtered list is too small (<3), it returns the original unfiltered list.
    """
    filtered = []
    
    for job in jobs:
        # Try estimated_wage_range first (Gemini-produced), fall back to raw salary
        rate = parse_hourly_rate(job.estimated_wage_range) or parse_hourly_rate(job.salary)
        if rate is None:
            # Couldn't parse either field, include it to be safe
            filtered.append(job)
        elif rate >= floor:
            filtered.append(job)
            
    if len(filtered) < 3 and len(jobs) >= 3:
        # Relax constraints if we drop below 3 results
        return list(jobs)
        
    return filtered
