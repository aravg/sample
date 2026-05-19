from typing import List, Dict, Any


def web_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search the web using DuckDuckGo (no API key required)."""
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", ""),
                })
        return results
    except Exception as e:
        return [{"title": "Search unavailable", "snippet": str(e), "url": ""}]
