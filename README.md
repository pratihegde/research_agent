# Multi-Agent Deep Research System

A sophisticated research system powered by LangGraph and FastAPI that intelligently processes user queries, conducts comprehensive web research, and generates structured reports with proper citations.

## 🌟 Features

- **Multi-Agent Architecture**: Three specialized agents (Planner, Researcher, Writer) working in concert
- **LangGraph Workflow**: Structured state management and control flow
- **Real-time Streaming**: Server-Sent Events (SSE) for live progress updates
- **Thread-based Conversations**: Maintain context across multiple queries
- **Comprehensive Reports**: Executive summaries, structured content, key takeaways, and citations
- **Graceful Degradation**: Handles API failures and partial results elegantly

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Service                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │         POST /chat (SSE Streaming)                │  │
│  └──────────────────────────────────────────────────┘  │
│                          │                              │
│                          ▼                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │          LangGraph Workflow                       │  │
│  │                                                    │  │
│  │  ┌──────┐    ┌──────────┐    ┌────────────┐     │  │
│  │  │ Plan │───▶│ Research │───▶│ Write Report│     │  │
│  │  └──────┘    └──────────┘    └────────────┘     │  │
│  │                                                    │  │
│  │  State: query, plan, research_notes, report...    │  │
│  └──────────────────────────────────────────────────┘  │
│                          │                              │
│                          ▼                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Web Search Tool                      │  │
│  │         (Tavily API / Stub Fallback)              │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

#### 1. Planner Agent
- Analyzes user queries
- Decomposes into 3-6 focused sub-questions
- Generates search queries for each sub-question
- Assigns priority rankings

#### 2. Research Agent
- Executes web searches for each sub-question
- Collects and synthesizes evidence
- Deduplicates sources
- Identifies data gaps and contradictions

#### 3. Report Writer Agent
- Synthesizes research into comprehensive reports
- Generates executive summaries
- Extracts key takeaways
- Documents limitations and assumptions

## 📋 Prerequisites

- Python 3.10 or higher
- OpenAI API key (required)
- Tavily API key (optional - system will use stub data if not provided)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd greychain
```

### 2. Set Up Virtual Environment

Using `uv` (recommended):
```bash
uv venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

Or using standard Python:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # Optional
```

### 5. Run the Application

```bash
python -m uvicorn app.main:app --reload
```

Or:

```bash
python app/main.py
```

The API will be available at `http://localhost:8000`

## 📡 API Usage

### Chat Endpoint (SSE Streaming)

**Endpoint:** `POST /chat`

**Request:**
```json
{
  "message": "Should company X expand into Southeast Asian markets in 2026?",
  "thread_id": "optional-thread-id"
}
```

**Response:** Server-Sent Events stream

**Event Types:**
- `thread_id` - Thread identifier for the conversation
- `planning` - Research plan generated
- `research_progress` - Updates as sub-questions are researched
- `writing` - Report generation started
- `message` - Report content chunks
- `done` - Complete response with full report and citations
- `error` - Error details if workflow fails

### Example with cURL

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main causes of inflation and how do central banks respond?"
  }' \
  --no-buffer
```

### Example with Python

```python
import requests
import json

url = "http://localhost:8000/chat"
data = {
    "message": "Is it a good idea to invest in AI companies?",
    "thread_id": None  # Will create new thread
}

response = requests.post(url, json=data, stream=True)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('event:'):
            event_type = line.split(':', 1)[1].strip()
        elif line.startswith('data:'):
            data = line.split(':', 1)[1].strip()
            print(f"{event_type}: {data}")
```

### Other Endpoints

**Health Check:**
```bash
GET /health
```

**Get Thread History:**
```bash
GET /threads/{thread_id}
```

## 📁 Project Structure

```
greychain/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # Pydantic request/response models
│   ├── graph/
│   │   ├── state.py         # LangGraph state definition
│   │   └── workflow.py      # LangGraph workflow
│   ├── agents/
│   │   ├── planner.py       # Planner agent
│   │   ├── researcher.py    # Research agent
│   │   └── writer.py        # Report writer agent
│   ├── tools/
│   │   └── search.py        # Web search tool (Tavily)
│   └── services/
│       ├── streaming.py     # SSE streaming service
│       └── threads.py       # Thread management
├── examples/                # Sample outputs
├── tests/                   # Unit and integration tests
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🧪 Testing

The system includes several test scenarios:

### Test Case 1: Simple Factual Query
```json
{
  "message": "What are the main causes of inflation and how do central banks respond?"
}
```

### Test Case 2: Ambiguous Business Query
```json
{
  "message": "Is it a good idea to invest in AI companies?"
}
```

### Test Case 3: Multi-Turn Conversation
```python
# First request
response1 = requests.post(url, json={
    "message": "What are the benefits of renewable energy?"
})
thread_id = extract_thread_id(response1)

# Follow-up request
response2 = requests.post(url, json={
    "message": "What are the main challenges in adoption?",
    "thread_id": thread_id
})
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY` (required): Your OpenAI API key
- `TAVILY_API_KEY` (optional): Your Tavily API key for web search

### Model Configuration

The system uses:
- **Planner & Researcher**: GPT-4o-mini (fast, cost-effective)
- **Report Writer**: GPT-4o (higher quality synthesis)

You can modify these in the respective agent files.

## 🚨 Error Handling

The system implements graceful degradation:

- **Search API Failures**: Falls back to stub data
- **LLM Failures**: Uses fallback templates
- **Partial Research**: Continues with available data
- **Network Issues**: Streams error events via SSE

## 📊 Response Format

The final `done` event contains:

```json
{
  "thread_id": "uuid",
  "query": "Original question",
  "executive_summary": "5-8 line summary",
  "report": "Full markdown report",
  "key_takeaways": ["insight 1", "insight 2"],
  "limitations": "Data gaps and assumptions",
  "citations": [
    {"title": "Source title", "url": "https://..."}
  ],
  "metadata": {
    "sub_question_count": 5,
    "sources_analyzed": 15,
    "completion_timestamp": "2025-02-11T10:30:00Z"
  }
}
```

## 🔮 Future Enhancements

### Production Readiness
- PostgreSQL for thread persistence
- Redis for caching
- LangGraph checkpointing for resumable workflows
- Celery for background task processing

### Features
- Quality validation node
- Iterative refinement (max 1 loop)
- Token-level streaming
- Advanced source credibility scoring

### Infrastructure
- Docker containerization
- Kubernetes deployment
- Monitoring and observability
- Rate limiting and cost management

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using LangGraph, FastAPI, and OpenAI**
