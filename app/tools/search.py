"""
Web search tool using Tavily API
"""
import os
from typing import List, Dict, Any
from tavily import TavilyClient


class WebSearchTool:
    """
    Web search tool that uses Tavily API for research.
    Falls back to stub data if API key is not available.
    """
    
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        if self.api_key:
            self.client = TavilyClient(api_key=self.api_key)
            self.use_stub = False
        else:
            self.client = None
            self.use_stub = True
            print("⚠️  TAVILY_API_KEY not found. Using stub search results.")
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Execute a web search for the given query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with 'title', 'url', and 'content' fields
        """
        if self.use_stub:
            return self._stub_search(query, max_results)
        
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced",
                include_raw_content=False
            )
            
            results = []
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", "Untitled"),
                    "url": result.get("url", ""),
                    "content": result.get("content", "")
                })
            
            return results
            
        except Exception as e:
            print(f"⚠️  Tavily search failed: {e}. Falling back to stub.")
            return self._stub_search(query, max_results)
    
    def _stub_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Stub search implementation for testing without API key.
        Returns hardcoded results based on query keywords.
        """
        # Generic stub results that work for most queries
        stub_results = [
            {
                "title": f"Research Article: {query[:50]}",
                "url": f"https://example.com/research/{query.replace(' ', '-')[:30]}",
                "content": f"This article discusses {query}. Key findings include multiple perspectives on the topic, "
                          f"recent developments, and expert analysis. The research indicates significant implications "
                          f"for stakeholders and suggests areas for further investigation."
            },
            {
                "title": f"Expert Analysis on {query[:40]}",
                "url": f"https://example.com/analysis/{query.replace(' ', '-')[:30]}",
                "content": f"Industry experts provide insights into {query}. The analysis covers current trends, "
                          f"challenges, and opportunities. Data suggests varying outcomes depending on specific "
                          f"conditions and implementation strategies."
            },
            {
                "title": f"Market Report: {query[:45]}",
                "url": f"https://example.com/market-report/{query.replace(' ', '-')[:30]}",
                "content": f"Comprehensive market analysis regarding {query}. The report examines competitive landscape, "
                          f"regulatory considerations, and growth projections. Key metrics indicate both risks and "
                          f"potential rewards for stakeholders."
            },
            {
                "title": f"Case Study: {query[:50]}",
                "url": f"https://example.com/case-study/{query.replace(' ', '-')[:30]}",
                "content": f"Real-world case study examining {query}. The study presents practical examples, "
                          f"lessons learned, and best practices. Results demonstrate the importance of careful "
                          f"planning and risk assessment."
            },
            {
                "title": f"Technical Overview: {query[:45]}",
                "url": f"https://example.com/technical/{query.replace(' ', '-')[:30]}",
                "content": f"Technical documentation and overview of {query}. This resource covers implementation "
                          f"requirements, infrastructure needs, and technical considerations. The overview includes "
                          f"both theoretical foundations and practical applications."
            }
        ]
        
        return stub_results[:max_results]


# Singleton instance
_search_tool = None

def get_search_tool() -> WebSearchTool:
    """Get or create the singleton search tool instance"""
    global _search_tool
    if _search_tool is None:
        _search_tool = WebSearchTool()
    return _search_tool
