# Shared state schema for the research agent graph
from typing import TypedDict


class ResearchState(TypedDict):
    """State object for the research agent."""
    topic: str
    research_notes: str
    fact_check_feedback: str
    final_report: str
    iteration_count: int
    quality_approved: bool