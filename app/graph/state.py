"""
LangGraph state definition for the research workflow
"""
from typing import List, Optional, TypedDict, Annotated
from operator import add
from app.models import ResearchPlan, ResearchNote, Citation


class ResearchState(TypedDict):
    """
    State object for the research workflow.
    
    This state is passed between all nodes in the LangGraph workflow
    and maintains all information needed for the research process.
    """
    # Input
    query: str  # User's research question
    thread_id: str  # Conversation thread identifier
    
    # Planning phase
    plan: Optional[ResearchPlan]  # Generated research plan with sub-questions
    
    # Research phase
    research_notes: Annotated[List[ResearchNote], add]  # Collected findings (appendable)
    
    # Writing phase
    final_report: Optional[str]  # Generated comprehensive report
    executive_summary: Optional[str]  # 5-8 line summary
    key_takeaways: Annotated[List[str], add]  # Main insights (appendable)
    limitations: Optional[str]  # Research constraints and assumptions
    
    # Citations (deduplicated across all research)
    citations: Annotated[List[Citation], add]  # All sources (appendable, will deduplicate)
    
    # Error handling
    errors: Annotated[List[str], add]  # Any errors encountered (appendable)
    
    # Metadata
    sources_analyzed: int  # Total number of sources processed
