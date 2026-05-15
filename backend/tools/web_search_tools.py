"""
tools/web_search_tools.py
Web search helper for the SentinelOps agents.
Uses the DuckDuckGo Instant Answer JSON API (no API key required) for
lightweight lookups.  Swap `duckduckgo_search` for SerpAPI / Tavily /
Google Custom Search when you need richer results.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
import urllib.error
from typing import Any, Dict, List


def duckduckgo_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search DuckDuckGo and return a list of result dicts.

    Each result has:
      - title (str)
      - url   (str)
      - snippet (str)
    """
    encoded = urllib.parse.quote_plus(query)
    url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_redirect=1&no_html=1"

    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "SentinelOps/1.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
    except urllib.error.URLError as exc:
        raise RuntimeError(f"DuckDuckGo search failed: {exc}") from exc

    results: List[Dict[str, Any]] = []

    # Abstract / Instant Answer
    if data.get("Abstract"):
        results.append({
            "title":   data.get("Heading", query),
            "url":     data.get("AbstractURL", ""),
            "snippet": data.get("Abstract", ""),
        })

    # Related topics
    for topic in data.get("RelatedTopics", [])[:max_results]:
        if "Text" in topic:
            results.append({
                "title":   topic.get("Text", "")[:80],
                "url":     topic.get("FirstURL", ""),
                "snippet": topic.get("Text", ""),
            })
        # Skip nested groups
        if len(results) >= max_results:
            break

    return results[:max_results]


def search_error_context(error_message: str) -> str:
    """
    Search the web for context around an error message.
    Returns a concise text summary of the top result.
    """
    results = duckduckgo_search(error_message, max_results=3)
    if not results:
        return "No web results found."

    lines: list[str] = []
    for r in results:
        lines.append(f"- [{r['title']}]({r['url']}): {r['snippet'][:200]}")
    return "\n".join(lines)
