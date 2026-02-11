import asyncio
import json
import httpx
from datetime import datetime

class ResearchClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def run_research(self, query: str, filename: str):
        print(f"🔬 Starting research: {query}")
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat",
                    json={"message": query},
                    headers={"Accept": "text/event-stream"}
                )
                
                final_data = {}
                report_content = ""
                
                async for line in response.aiter_lines():
                    if line.startswith("event: done"):
                        # Next line is data
                        pass
                    elif line.startswith("data: "):
                        data_str = line.replace("data: ", "").strip()
                        if not data_str: continue
                        
                        try:
                            data = json.loads(data_str)
                            
                            # Capture final output
                            if "report" in data:
                                final_data = data
                            
                        except json.JSONDecodeError:
                            pass
                            
                # Save to file
                if final_data:
                    # Add metadata
                    final_data["completion_timestamp"] = datetime.utcnow().isoformat()
                    
                    with open(f"examples/{filename}.json", "w", encoding="utf-8") as f:
                        json.dump(final_data, f, indent=2, ensure_ascii=False)
                    
                    # Save text version
                    with open(f"examples/{filename}.txt", "w", encoding="utf-8") as f:
                        f.write(f"Research Query: {query}\n\n")
                        f.write(f"EXECUTIVE SUMMARY\n{'-'*20}\n{final_data.get('executive_summary', '')}\n\n")
                        f.write(f"FULL REPORT\n{'-'*20}\n{final_data.get('report', '')}\n\n")
                        f.write(f"KEY TAKEAWAYS\n{'-'*20}\n")
                        for t in final_data.get('key_takeaways', []):
                            f.write(f"- {t}\n")
                        f.write(f"\nSOURCES\n{'-'*20}\n")
                        for i, c in enumerate(final_data.get('citations', [])):
                            f.write(f"{i+1}. {c.get('title')} ({c.get('url')})\n")
                            
                    print(f"✅ Saved outputs to examples/{filename}.json and .txt")
                else:
                    print(f"❌ No final data received for {filename}")

            except Exception as e:
                print(f"❌ Error: {str(e)}")

async def main():
    client = ResearchClient()
    
    # Test Case 1: Economic Analysis
    await client.run_research(
        "What are the main causes of inflation and how do central banks respond?",
        "economic_query"
    )
    
    # Test Case 2: Business Strategy
    await client.run_research(
        "Should company X expand into Southeast Asian markets in 2026? Consider risks and opportunities.",
        "business_strategy"
    )

if __name__ == "__main__":
    asyncio.run(main())
