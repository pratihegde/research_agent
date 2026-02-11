"""
Research Agent - Executes web searches and collects evidence
"""
import os
from typing import Dict, Any, List, Set
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.models import ResearchNote, Citation
from app.graph.state import ResearchState
from app.tools.search import get_search_tool


class ResearchAgent:
    """
    Agent responsible for executing web searches and synthesizing findings.
    
    For each sub-question, this agent:
    - Executes multiple search queries
    - Extracts relevant evidence bullets
    - Identifies data gaps and contradictions
    - Deduplicates sources
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.search_tool = get_search_tool()
        
        self.system_prompt = """You are a research analyst expert at extracting insights from web search results.

Given a sub-question and search results, you must:
1. Extract 4-8 evidence bullets that directly answer the sub-question
2. Identify any contradictions, uncertainties, or data gaps
3. Note any open questions that require further investigation

Guidelines:
- Evidence bullets should be specific, factual, and well-sourced
- Include quantitative data when available (numbers, percentages, dates)
- Note conflicting information or uncertainty
- Be concise but informative
- Focus on relevance to the sub-question

Return your analysis as a JSON object:
{
    "evidence_bullets": [
        "Specific finding from source A...",
        "Data point from source B showing...",
        ...
    ],
    "open_questions": [
        "Unclear whether...",
        "Conflicting data on...",
        ...
    ]
}

Be thorough and critical in your analysis."""
    
    def research(self, state: ResearchState) -> Dict[str, Any]:
        """
        Execute research for all sub-questions in the plan.
        
        Args:
            state: Current workflow state with research plan
            
        Returns:
            Updated state with research notes and citations
        """
        plan = state.get("plan")
        if not plan:
            return {"errors": ["No research plan available"]}
        
        research_notes = []
        all_citations = []
        seen_urls: Set[str] = set()
        total_sources = 0
        errors = []
        
        # Sort sub-questions by priority
        sorted_questions = sorted(
            plan.sub_questions,
            key=lambda sq: sq.priority
        )
        
        for sub_q in sorted_questions:
            try:
                print(f"🔍 Researching: {sub_q.question}")
                
                # Collect search results for all queries
                all_results = []
                for search_query in sub_q.search_queries[:3]:  # Limit to 3 queries per sub-question
                    results = self.search_tool.search(search_query, max_results=3)
                    all_results.extend(results)
                    total_sources += len(results)
                
                # Deduplicate sources for this sub-question
                unique_results = []
                sub_q_citations = []
                
                for result in all_results:
                    url = result.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        unique_results.append(result)
                        sub_q_citations.append(
                            Citation(
                                title=result.get("title", "Untitled"),
                                url=url
                            )
                        )
                
                # Synthesize findings using LLM
                evidence_bullets, open_questions = self._synthesize_findings(
                    sub_q.question,
                    unique_results
                )
                
                # Create research note
                note = ResearchNote(
                    sub_question_id=sub_q.id,
                    evidence_bullets=evidence_bullets,
                    sources=sub_q_citations,
                    open_questions=open_questions
                )
                
                research_notes.append(note)
                all_citations.extend(sub_q_citations)
                
                print(f"  ✅ Found {len(evidence_bullets)} evidence points from {len(sub_q_citations)} sources")
                
            except Exception as e:
                error_msg = f"Research failed for sub-question '{sub_q.question}': {str(e)}"
                print(f"  ❌ {error_msg}")
                errors.append(error_msg)
                
                # Add partial note even on failure
                research_notes.append(
                    ResearchNote(
                        sub_question_id=sub_q.id,
                        evidence_bullets=["Research incomplete due to error"],
                        sources=[],
                        open_questions=["Unable to complete research for this question"]
                    )
                )
        
        return {
            "research_notes": research_notes,
            "citations": all_citations,
            "sources_analyzed": total_sources,
            "errors": errors if errors else []
        }
    
    def _synthesize_findings(
        self,
        sub_question: str,
        search_results: List[Dict[str, Any]]
    ) -> tuple[List[str], List[str]]:
        """
        Use LLM to synthesize search results into evidence bullets.
        
        Args:
            sub_question: The sub-question being researched
            search_results: List of search results with title, url, content
            
        Returns:
            Tuple of (evidence_bullets, open_questions)
        """
        if not search_results:
            return (
                ["No search results available for this question"],
                ["Unable to find relevant information"]
            )
        
        # Format search results for LLM
        results_text = "\n\n".join([
            f"Source: {r['title']}\nURL: {r['url']}\nContent: {r['content']}"
            for r in search_results[:10]  # Limit to avoid token limits
        ])
        
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""Sub-question: {sub_question}

Search Results:
{results_text}

Analyze these results and extract evidence bullets and open questions.""")
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse JSON response
            import json
            analysis = json.loads(response.content)
            
            return (
                analysis.get("evidence_bullets", []),
                analysis.get("open_questions", [])
            )
            
        except Exception as e:
            print(f"  ⚠️  Synthesis failed, using fallback: {e}")
            # Fallback: extract first sentences from each result
            evidence = [
                f"{r['content'][:200]}..." 
                for r in search_results[:6]
            ]
            return (evidence, ["Unable to fully synthesize findings"])


def create_research_node():
    """Factory function to create the research node for LangGraph"""
    agent = ResearchAgent()
    return agent.research
