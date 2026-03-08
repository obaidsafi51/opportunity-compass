"""
Static local training programs for Montgomery, AL.
Forms the base recommender set.
"""

from typing import Any

from models.schemas import ProgramCard

MOCK_PROGRAMS: list[ProgramCard] = [
    ProgramCard(
        name="Certified Nursing Assistant (CNA) Fast-Track",
        provider="Trenholm State Community College",
        benefit="Get certified in 6 weeks with clinical placement.",
        eligibility="Must have high school diploma or GED.",
        sectors=["Healthcare"]
    ),
    ProgramCard(
        name="Commercial Driver's License (CDL) Training",
        provider="Montgomery Job Corps Center",
        benefit="Free housing and meals during training. Includes job placement.",
        eligibility="Ages 16-24, income eligible.",
        sectors=["Logistics", "Transportation"]
    ),
    ProgramCard(
        name="Advanced Manufacturing Technician Program",
        provider="AIDT / Montgomery Technology Center",
        benefit="Direct pipeline to local automotive manufacturers.",
        eligibility="Must pass basic aptitude test.",
        sectors=["Manufacturing", "Automotive"]
    ),
    ProgramCard(
        name="IT Pathways Boot Camp",
        provider="TechMGM",
        benefit="Learn fundamentals of web development and IT support.",
        eligibility="Open to all Montgomery County residents.",
        sectors=["Technology", "Customer Service"]
    ),
    ProgramCard(
        name="Construction Apprenticeship",
        provider="Alabama AGC",
        benefit="Earn while you learn. Immediate placement as laborer.",
        eligibility="Must be 18+ and pass drug screening.",
        sectors=["Construction", "Trades"]
    ),
]

def get_all_programs() -> list[ProgramCard]:
    return MOCK_PROGRAMS
