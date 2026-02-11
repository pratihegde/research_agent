# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Add Your OpenAI API Key

Edit the `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE
```

### Step 2: Start the Server

Open a terminal in the project directory and run:

```bash
# Activate virtual environment (if not already activated)
.venv\Scripts\activate

# Start the server
python app/main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Test the System

Open a **new terminal** and run the test client:

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run test client
python test_client.py
```

This will execute a test query and show you the streaming results!

## 📡 Using the API Directly

### With cURL

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What are the main causes of inflation?\"}" \
  --no-buffer
```

### With Python

```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "What are the main causes of inflation?"},
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

### With JavaScript/Fetch

```javascript
const eventSource = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What are the main causes of inflation?'
  })
});

const reader = eventSource.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  console.log(decoder.decode(value));
}
```

## 🧪 Test Queries to Try

### Simple Factual
```
"What are the main causes of inflation and how do central banks respond?"
```

### Business Strategy
```
"Should a tech company expand into Southeast Asian markets in 2026?"
```

### Technical Analysis
```
"What are the key differences between SQL and NoSQL databases?"
```

### Ambiguous Query
```
"Is it a good idea to invest in AI companies?"
```

## 📊 What to Expect

When you run a query, you'll see:

1. **Thread ID** - Unique identifier for the conversation
2. **Planning** - System analyzing your query
3. **Research Progress** - Updates as each sub-question is researched
4. **Writing** - Report generation begins
5. **Message Chunks** - Report content streaming in real-time
6. **Done** - Complete response with:
   - Executive summary
   - Full report
   - Key takeaways
   - Limitations
   - Citations
   - Metadata

## ⚠️ Troubleshooting

### Server won't start
- Make sure virtual environment is activated
- Check that all dependencies are installed: `uv pip list`
- Verify your OpenAI API key in `.env`

### "Connection refused" error
- Make sure the server is running in another terminal
- Check that it's running on port 8000
- Try accessing http://localhost:8000 in your browser

### API key errors
- Verify your OpenAI API key is correct in `.env`
- Make sure there are no extra spaces or quotes
- Check your OpenAI account has credits

### No search results
- The system will use stub data if Tavily API key is not provided
- This is normal and expected for testing
- Add Tavily API key to `.env` for real web search

## 🎯 Next Steps

1. **Try different queries** - Test with various types of questions
2. **Save example outputs** - Copy results to `examples/` directory
3. **Test multi-turn conversations** - Use the same thread_id for follow-ups
4. **Review the code** - Explore the agent implementations
5. **Create architecture diagrams** - For your documentation

## 📚 Additional Resources

- **Full Documentation**: See `README.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **API Reference**: Visit http://localhost:8000/docs (FastAPI auto-docs)

---

**Happy Researching! 🔍**
