"""
Planner Agent - Decomposes user queries into structured research plans
"""
import os
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.models import ResearchPlan, SubQuestion
from app.graph.state import ResearchState


class PlannerAgent:
    """
    Agent responsible for analyzing user queries and creating structured research plans.
    
    Decomposes complex queries into 3-6 focused sub-questions with search queries
    and priority rankings.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.system_prompt = """You are a research planning expert. Your job is to analyze user queries and create comprehensive research plans.

Given a user's research question, you must:
1. Decompose it into 3-6 focused sub-questions that cover all aspects of the query
2. For each sub-question, generate 2-4 specific search queries that will find relevant information
3. Assign priority rankings (1 = highest priority) to guide research sequence

Guidelines:
- Sub-questions should be specific, focused, and non-overlapping
- Cover different angles: factual data, expert opinions, case studies, trends, risks, opportunities
- Search queries should be concrete and optimized for web search
- Higher priority (1, 2) for foundational questions; lower priority for nuanced/follow-up questions
- If the query is ambiguous, make reasonable assumptions and note them

Return your response as a JSON object with this exact structure:
{
    "sub_questions": [
        {
            "id": "sq1",
            "question": "What are the main...",
            "search_queries": ["query 1", "query 2", "query 3"],
            "priority": 1
        },
        ...
    ]
}

Be thorough but focused. Quality over quantity."""
    
    def plan(self, state: ResearchState) -> Dict[str, Any]:
        """
        Generate a research plan from the user's query.
        
        Args:
            state: Current workflow state containing the query
            
        Returns:
            Updated state with research plan
        """
        query = state["query"]
        
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Create a research plan for this query:\n\n{query}")
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse the JSON response
            plan_data = json.loads(response.content)
            
            # Validate and create ResearchPlan object
            sub_questions = [
                SubQuestion(**sq) for sq in plan_data["sub_questions"]
            ]
            
            research_plan = ResearchPlan(sub_questions=sub_questions)
            
            print(f"✅ Generated research plan with {len(sub_questions)} sub-questions")
            
            return {
                "plan": research_plan,
                "sources_analyzed": 0
            }
            
        except Exception as e:
            error_msg = f"Planner agent failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Return fallback plan
            fallback_plan = ResearchPlan(
                sub_questions=[
                    SubQuestion(
                        id="sq1",
                        question=query,
                        search_queries=[query],
                        priority=1
                    )
                ]
            )
            
            return {
                "plan": fallback_plan,
                "errors": [error_msg],
                "sources_analyzed": 0
            }


def create_planner_node():
    """Factory function to create the planner node for LangGraph"""
    agent = PlannerAgent()
    return agent.plan
