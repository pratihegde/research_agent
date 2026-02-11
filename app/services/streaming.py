"""
Server-Sent Events (SSE) streaming service for real-time updates
"""
import json
import asyncio
from typing import AsyncGenerator, Dict, Any
from datetime import datetime
from app.graph.workflow import get_research_graph
from app.models import ChatResponse, ChatMetadata, Citation


class StreamingService:
    """
    Service for streaming research workflow progress via SSE.
    """
    
    async def stream_research(
        self,
        query: str,
        thread_id: str
    ) -> AsyncGenerator[str, None]:
        """
        Execute research workflow and stream progress updates.
        """
        try:
            # Send thread_id event
            yield self._format_sse_event("thread_id", {"thread_id": thread_id})
            
            # Initialize state
            initial_state = {
                "query": query,
                "thread_id": thread_id,
                "plan": None,
                "research_notes": [],
                "final_report": None,
                "executive_summary": None,
                "key_takeaways": [],
                "limitations": None,
                "citations": [],
                "errors": [],
                "sources_analyzed": 0
            }
            
            graph = get_research_graph()
            final_state = initial_state
            
            # Use astream to monitor progress
            async for event_data in graph.astream(initial_state, stream_mode="updates"):
                # event_data is a dict where key is node name and value is the output of that node
                for node_name, output in event_data.items():
                    # Update internal state tracker
                    final_state.update(output)
                    
                    if node_name == "plan":
                        sub_count = len(output.get("plan").sub_questions) if output.get("plan") else 0
                        yield self._format_sse_event("planning", {
                            "status": f"Generated research plan with {sub_count} focus areas.",
                            "sub_question_count": sub_count
                        })
                    
                    elif node_name == "research":
                        yield self._format_sse_event("research_progress", {
                            "status": "Research completed for all sub-questions.",
                            "sources_analyzed": output.get("sources_analyzed", 0)
                        })
                    
                    elif node_name == "write_report":
                        yield self._format_sse_event("writing", {"status": "Synthesis complete. Streaming final report..."})
            
            # Stream final response parts
            response = self._build_response(final_state, thread_id)
            
            # Stream report content in chunks for effect
            report_chunks = self._chunk_text(response.report, chunk_size=500)
            for chunk in report_chunks:
                yield self._format_sse_event("message", {"content": chunk})
                await asyncio.sleep(0.05)
            
            # Send final done event
            yield self._format_sse_event("done", response.model_dump())
            
        except Exception as e:
            import traceback
            print(f"❌ Stream error: {traceback.format_exc()}")
            error_data = {
                "error": str(e),
                "detail": "Research workflow failed",
                "thread_id": thread_id
            }
            yield self._format_sse_event("error", error_data)
    
    def _execute_with_callbacks(self, graph, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute graph and track progress.
        This runs synchronously but we track state changes.
        """
        # For now, execute directly
        # In a more advanced implementation, we could use LangGraph's streaming
        result = graph.invoke(initial_state)
        return result
    
    def _build_response(self, state: Dict[str, Any], thread_id: str) -> ChatResponse:
        """Build final ChatResponse from workflow state"""
        
        # Deduplicate citations
        seen_urls = set()
        unique_citations = []
        for citation in state.get("citations", []):
            if citation.url not in seen_urls:
                seen_urls.add(citation.url)
                unique_citations.append(citation)
        
        # Build metadata
        plan = state.get("plan")
        metadata = ChatMetadata(
            sub_question_count=len(plan.sub_questions) if plan else 0,
            sources_analyzed=state.get("sources_analyzed", 0),
            completion_timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
        # Build response
        response = ChatResponse(
            thread_id=thread_id,
            query=state["query"],
            executive_summary=state.get("executive_summary", ""),
            report=state.get("final_report", ""),
            key_takeaways=state.get("key_takeaways", []),
            limitations=state.get("limitations", ""),
            citations=unique_citations,
            metadata=metadata
        )
        
        return response
    
    def _format_sse_event(self, event_type: str, data: Any) -> str:
        """Format data as SSE event"""
        json_data = json.dumps(data) if not isinstance(data, str) else data
        return f"event: {event_type}\ndata: {json_data}\n\n"
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> list[str]:
        """Split text into chunks for streaming"""
        if not text:
            return []
        
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
        return chunks


# Singleton instance
_streaming_service = None

def get_streaming_service() -> StreamingService:
    """Get or create the singleton streaming service instance"""
    global _streaming_service
    if _streaming_service is None:
        _streaming_service = StreamingService()
    return _streaming_service
