"""
FastAPI application for the Multi-Agent Deep Research System
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from app.models import ChatRequest, ErrorResponse
from app.services.streaming import get_streaming_service
from app.services.threads import get_thread_manager


# Create FastAPI app
app = FastAPI(
    title="Deep Research System",
    description="Multi-Agent LangGraph Research System with Real-time Streaming",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Deep Research System",
        "version": "1.0.0",
        "description": "Multi-Agent LangGraph Research System",
        "endpoints": {
            "chat": "POST /chat - Execute research with SSE streaming",
            "health": "GET /health - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    thread_manager = get_thread_manager()
    return {
        "status": "healthy",
        "active_threads": thread_manager.get_thread_count()
    }


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Execute research workflow with real-time SSE streaming.
    
    This endpoint:
    1. Accepts user message and optional thread_id
    2. Creates or retrieves conversation thread
    3. Executes LangGraph research workflow
    4. Streams progress updates via Server-Sent Events
    
    Args:
        request: ChatRequest with message and optional thread_id
        
    Returns:
        StreamingResponse with SSE events
    """
    try:
        # Validate request
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )
        
        # Get or create thread
        thread_manager = get_thread_manager()
        thread_id, thread = thread_manager.get_or_create_thread(request.thread_id)
        
        # Add user message to thread
        thread_manager.add_message(thread_id, "user", request.message)
        
        # Get streaming service
        streaming_service = get_streaming_service()
        
        # Create SSE stream
        async def event_generator():
            try:
                async for event in streaming_service.stream_research(
                    query=request.message,
                    thread_id=thread_id
                ):
                    yield event
            except Exception as e:
                # Send error event
                import json
                error_event = f"event: error\ndata: {json.dumps({'error': str(e), 'thread_id': thread_id})}\n\n"
                yield error_event
        
        # Return SSE response
        return EventSourceResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable buffering for nginx
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/threads/{thread_id}")
async def get_thread_history(thread_id: str):
    """
    Get conversation history for a thread.
    
    Args:
        thread_id: Thread identifier
        
    Returns:
        Thread history with messages
    """
    thread_manager = get_thread_manager()
    thread = thread_manager.get_thread(thread_id)
    
    if not thread:
        raise HTTPException(
            status_code=404,
            detail=f"Thread {thread_id} not found"
        )
    
    return {
        "thread_id": thread.thread_id,
        "created_at": thread.created_at,
        "updated_at": thread.updated_at,
        "message_count": len(thread.messages),
        "messages": thread.get_history()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
