# Deep Research System - Architecture Document

## 1. System Architecture Overview

The Multi-Agent Deep Research System is built on a modern stack combining FastAPI for high-performance API delivery and LangGraph for complex agentic workflows.

### Components
- **Web UI**: A modern, dark-themed SPA built with Vanilla JS and CSS, providing real-time research monitoring.
- **FastAPI Service**: Handles incoming requests, manages conversation threads, and orchestrates the research workflow via SSE streaming.
- **LangGraph Workflow**: A stateful directed graph that manages the transition between planning, research, and synthesis.
- **Specialized Agents**: 
    - **Planner**: Decomposes queries into actionable research plans.
    - **Researcher**: Conducts web searches and evidence extraction.
    - **Writer**: Synthesizes findings into structured reports.
- **Web Search Tool**: Integrated with Tavily API for high-quality, AI-optimized search results.

### Data Flow
1. User submits a query via the Web UI.
2. FastAPI creates/retrieves a thread and initiates the LangGraph workflow.
3. The workflow streams updates back to the UI via Server-Sent Events (SSE).
4. Agents update the unified `ResearchState` iteratively.
5. The final synthesized report is streamed to the user in chunks.

## 2. LangGraph Workflow Design

The workflow follows a sequential state machine pattern:

`START` ➔ `plan` ➔ `research` ➔ `write_report` ➔ `END`

- **State Management**: Uses a `ResearchState` object that tracks query, plan, research notes, citations, and metadata. Annotated lists allow for additive data collection (e.g., collecting citations from multiple search steps).
- **Execution**: Orchestrated using `astream` to allow the API layer to capture and stream intermediate events without blocking.

## 3. Agent Design Decisions

### Why a 3-Agent Architecture?
- **Separation of Concerns**: Planning requires strategic thinking; Research requires information retrieval and extraction; Writing requires synthesis and objective tone. Separating these ensures each agent's prompt can be focused and optimized.
- **Scalability**: We use **GPT-4o-mini** for the Planner and Researcher for cost-efficiency and speed, but upgrade to **GPT-4o** for the Writer to ensure high-quality, nuanced report generation.

### Alternative Considerations
- **2 Agents (Research + Write)**: Combining Planning into Research often leads to fragmented or shallow search queries. A dedicated Planner ensures comprehensive coverage.
- **4 Agents (Plan + Research + Review + Write)**: A reviewer agent would add quality validation (Bonus Point territory), which is a logical next step for production quality but was omitted for MVP simplicity.

### Trade-offs
- **Sequential vs. Parallel**: Research is currently sequential for simplicity. In a larger production system, sub-questions could be researched in parallel to reduce latency.
- **Persistence**: Used in-memory storage for threads to meet the direct case study requirements, but designed the `ThreadManager` to be easily swappable with a database backend.

## 4. Production Readiness Plan

### 1. Persistence Strategy
- **Database**: Replace in-memory dicts with **PostgreSQL** for message history and **Redis** for state caching.
- **Checkpointing**: Implement `SqliteSaver` or `PostgresSaver` in LangGraph to allow for resumable workflows in case of server failure.

### 2. Scaling Approach
- **Load Balancing**: Use Nginx or AWS ALB to distribute traffic across multiple FastAPI instances running in Docker containers.
- **Task Queues**: For extremely deep research (loops/multiple iterations), move workflow execution to **Celery** with Redis/RabbitMQ.

### 3. Monitoring & Observability
- **LangSmith Integration**: Monitor agent traces, latency, and success rates for every node execution.
- **Prometheus/Grafana**: Track API performance metrics (requests/sec, error rates, token usage costs).

### 4. Error Handling & Reliability
- **Retries**: Implement exponential backoff for LLM and Search API calls.
- **Circuit Breakers**: Use libraries like `resilience4j` (or Python equivalents) to gracefully handle API outages.

### 5. Security & Cost Management
- **Auth**: Integrate OAuth2/JWT for user authentication.
- **Rate Limiting**: Implement per-user and per-thread rate limits.
- **Prompt Injection**: Use specialized guardrails (like LLM Guard) to sanitize user inputs.

---
*Created by Antigravity AI for Greychain Multi-Agent Case Study*
