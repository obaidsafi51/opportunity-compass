"""
Aggregation logic for skills heatmaps and training gaps.
"""

from collections import Counter
from typing import Sequence

from models.schemas import AlignedProgram, GapRow, NormalizedJob, Severity, SkillRow
from services.programs_db import MOCK_PROGRAMS


def get_top_skills(jobs: Sequence[NormalizedJob], limit: int = 10) -> list[SkillRow]:
    """
    Aggregate extracted_skills from all jobs.
    If no extracted skills exist (e.g. unanalyzed seed data), creates
    a fallback distribution based on categories to populate the heatmap.
    """
    skill_counts = Counter()
    for job in jobs:
        if job.extracted_skills:
            for skill in job.extracted_skills:
                # Basic normalization
                s = skill.title().strip()
                if s:
                    skill_counts[s] += 1
                    
    # Fallback logic for unanalyzed seed data strictly to populate heatmap
    if not skill_counts and jobs:
        for job in jobs:
            cat = job.job_title.lower()
            if "nurse" in cat or "cna" in cat or "medical" in cat:
                skill_counts["Patient Care"] += 1
                skill_counts["Medical Terminology"] += 1
                skill_counts["CPR"] += 1
            elif "driver" in cat or "delivery" in cat:
                skill_counts["Commercial Driving"] += 1
                skill_counts["Logistics"] += 1
            elif "cook" in cat or "food" in cat:
                skill_counts["Food Safety"] += 1
                skill_counts["Customer Service"] += 1
            else:
                skill_counts["Communication"] += 1
                skill_counts["Teamwork"] += 1

    top = skill_counts.most_common(limit)
    rows = []
    
    # Generate pseudo pct_change for visual demo purposes (simulate trend)
    import hashlib
    for skill, count in top:
        # Use a stable hash to generate consistent -10 to +30 % changes
        hash_val = int(hashlib.md5(skill.encode()).hexdigest(), 16)
        pct = (hash_val % 40) - 10
        rows.append(
            SkillRow(
                skill=skill,
                count=count,
                pct_change=float(pct),
                is_rising=(pct >= 25)
            )
        )
        
    return rows


def get_training_gaps(jobs: Sequence[NormalizedJob], limit: int = 5) -> list[GapRow]:
    """
    Identify occupational mismatches (gaps) based on high-demand roles.
    Assign string severities and map appropriate mitigation programs.
    """
    # Count occurrences of job titles
    counts = Counter()
    category_map = {}
    for job in jobs:
        title = job.job_title
        counts[title] += 1
        category_map[title] = job.category or "General"
        
    top_jobs = counts.most_common(limit)
    rows = []
    
    for title, count in top_jobs:
        # Determine strict severity rules
        if count > 50:
            sev = Severity.ACUTE
        elif count > 20:
            sev = Severity.EMERGING
        else:
            sev = Severity.BALANCED
            
        # Match programs
        cat = category_map[title]
        aligned = []
        for prog in MOCK_PROGRAMS:
            # Map loosely based on sector or string matches
            matching_sectors = [s for s in prog.sectors if s.lower() in cat.lower() or s.lower() in title.lower()]
            if matching_sectors or (cat == "General" and "Customer" in prog.sectors):
                aligned.append(AlignedProgram(name=prog.name, provider=prog.provider))
                
        # Fallback if no specific program perfectly matches (give generic or first)
        if not aligned and MOCK_PROGRAMS:
            # Trenholm/Job Corps default as catchalls
            aligned.append(AlignedProgram(
                name=MOCK_PROGRAMS[0].name, 
                provider=MOCK_PROGRAMS[0].provider
            ))
            
        # Only take top 2 programs
        rows.append(GapRow(
            occupation=title,
            severity=sev,
            aligned_programs=aligned[:2]
        ))
        
    return rows
