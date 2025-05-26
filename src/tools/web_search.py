from src.tools.registry import BaseTool
from typing import Dict, Any
import requests
from tavily import TavilyClient

class WebSearchTool(BaseTool):
    """Tool for performing web searches using Tavily API."""
    
    def __init__(self, api_key: str):
        self.client = TavilyClient(api_key=api_key)
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return "Search the web for information using Tavily API"
    
    def execute(self, query: str) -> Dict[str, Any]:
        """Execute a web search query."""
        try:
            # Use Tavily client to search
            response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=5
            )
            
            if response and "results" in response:
                # Format the results
                results = []
                for result in response["results"][:3]:  # Take top 3 results
                    results.append(f"Title: {result.get('title', 'N/A')}\n"
                                 f"Content: {result.get('content', 'N/A')[:200]}...\n"
                                 f"URL: {result.get('url', 'N/A')}")
                
                return {
                    "success": True,
                    "result": "\n\n".join(results)
                }
            else:
                return {
                    "success": False,
                    "error": "No search results found"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Search failed: {str(e)}"
            }
