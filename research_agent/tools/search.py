# tools/search.py
from tavily import TavilyClient
import os

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query: str) -> str:
    results = client.search(query=query, max_results=5)
    
    # Format results cleanly for the LLM
    formatted = []
    for r in results["results"]:
        formatted.append(f"Source: {r['url']}\nContent: {r['content']}\n")
    
    return "\n---\n".join(formatted)