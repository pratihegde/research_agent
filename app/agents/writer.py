"""
Report Writer Agent - Synthesizes research into comprehensive reports
"""
import os
import json
from typing import Dict, Any
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.graph.state import ResearchState


class ReportWriterAgent:
    """
    Agent responsible for synthesizing research notes into comprehensive reports.
    
    Generates:
    - Executive summary (5-8 lines)
    - Well-structured report with clear sections
    - Key takeaways and actionable insights
    - Limitations and assumptions documentation
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.4,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.system_prompt = """You are an expert research report writer who creates comprehensive, well-structured reports.

Given research notes from multiple sub-questions, you must create:
1. Executive Summary (5-8 lines capturing key insights)
2. Full Report (well-structured with clear headings and logical flow)
3. Key Takeaways (3-7 actionable insights)
4. Limitations (data gaps, assumptions, constraints)

Guidelines for the report:
- Start with context and background
- Organize findings into logical sections with clear headings
- Use markdown formatting (##, ###, -, *, etc.)
- Integrate evidence from all sub-questions cohesively
- Highlight important data points and trends
- Address contradictions or uncertainties
- Maintain professional, objective tone
- Be comprehensive but concise
- End with implications and future considerations

Return your response as a JSON object:
{
    "executive_summary": "5-8 line summary...",
    "report": "# Full Report\\n\\n## Section 1\\n\\nContent...",
    "key_takeaways": [
        "First key insight...",
        "Second actionable point...",
        ...
    ],
    "limitations": "Discussion of data gaps, assumptions made, and research constraints..."
}

Create a report that is insightful, well-organized, and actionable."""
    
    def write_report(self, state: ResearchState) -> Dict[str, Any]:
        """
        Generate comprehensive report from research notes.
        
        Args:
            state: Current workflow state with research notes
            
        Returns:
            Updated state with final report, summary, takeaways, and limitations
        """
        query = state["query"]
        research_notes = state.get("research_notes", [])
        plan = state.get("plan")
        
        if not research_notes:
            return {
                "errors": ["No research notes available to write report"],
                "final_report": "Unable to generate report due to lack of research data.",
                "executive_summary": "Research could not be completed.",
                "key_takeaways": ["Unable to generate insights"],
                "limitations": "Research process failed to collect sufficient data."
            }
        
        try:
            print(f"✍️  Writing comprehensive report...")
            
            # Format research notes for LLM
            notes_text = self._format_research_notes(research_notes, plan)
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""Original Query: {query}

Research Notes:
{notes_text}

Create a comprehensive research report addressing the original query.""")
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse JSON response
            report_data = json.loads(response.content)
            
            print(f"✅ Report generated successfully")
            
            return {
                "final_report": report_data.get("report", ""),
                "executive_summary": report_data.get("executive_summary", ""),
                "key_takeaways": report_data.get("key_takeaways", []),
                "limitations": report_data.get("limitations", "")
            }
            
        except Exception as e:
            error_msg = f"Report writer failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Generate fallback report
            fallback_report = self._generate_fallback_report(query, research_notes)
            
            return {
                "final_report": fallback_report,
                "executive_summary": "Report generated with limited synthesis due to processing error.",
                "key_takeaways": ["See detailed findings in report"],
                "limitations": "Report generation encountered errors; synthesis may be incomplete.",
                "errors": [error_msg]
            }
    
    def _format_research_notes(self, research_notes, plan) -> str:
        """Format research notes into readable text for LLM"""
        formatted = []
        
        # Create mapping of sub-question IDs to questions
        sq_map = {}
        if plan:
            sq_map = {sq.id: sq.question for sq in plan.sub_questions}
        
        for note in research_notes:
            sub_q_text = sq_map.get(note.sub_question_id, note.sub_question_id)
            
            formatted.append(f"\n## Sub-Question: {sub_q_text}\n")
            formatted.append("\nEvidence:")
            for bullet in note.evidence_bullets:
                formatted.append(f"- {bullet}")
            
            if note.open_questions:
                formatted.append("\nOpen Questions:")
                for oq in note.open_questions:
                    formatted.append(f"- {oq}")
            
            formatted.append(f"\nSources: {len(note.sources)} sources")
            formatted.append("\n" + "-" * 80)
        
        return "\n".join(formatted)
    
    def _generate_fallback_report(self, query: str, research_notes) -> str:
        """Generate a basic report when LLM synthesis fails"""
        report_lines = [
            f"# Research Report: {query}\n",
            "## Overview\n",
            "This report presents findings from web research on the query above.\n",
            "## Findings\n"
        ]
        
        for i, note in enumerate(research_notes, 1):
            report_lines.append(f"\n### Finding {i}\n")
            for bullet in note.evidence_bullets:
                report_lines.append(f"- {bullet}")
        
        report_lines.append("\n## Conclusion\n")
        report_lines.append("Further analysis recommended based on the findings above.")
        
        return "\n".join(report_lines)


def create_writer_node():
    """Factory function to create the writer node for LangGraph"""
    agent = ReportWriterAgent()
    return agent.write_report
