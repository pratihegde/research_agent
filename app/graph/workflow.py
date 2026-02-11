"""
LangGraph workflow definition for the research system
"""
from langgraph.graph import StateGraph, END
from app.graph.state import ResearchState
from app.agents.planner import create_planner_node
from app.agents.researcher import create_research_node
from app.agents.writer import create_writer_node


def create_research_graph():
    """
    Create and compile the research workflow graph.
    
    Graph structure:
    START -> plan -> research -> write_report -> END
    
    Returns:
        Compiled LangGraph workflow
    """
    # Create the graph
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("plan", create_planner_node())
    workflow.add_node("research", create_research_node())
    workflow.add_node("write_report", create_writer_node())
    
    # Define edges (control flow)
    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "research")
    workflow.add_edge("research", "write_report")
    workflow.add_edge("write_report", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


# Create singleton instance
_research_graph = None

def get_research_graph():
    """Get or create the singleton research graph instance"""
    global _research_graph
    if _research_graph is None:
        _research_graph = create_research_graph()
    return _research_graph
