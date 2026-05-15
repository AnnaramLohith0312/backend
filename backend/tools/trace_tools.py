"""
tools/trace_tools.py
Utilities for fetching and summarising distributed trace spans.
Currently mocked with DB placeholder - swap for Jaeger / Tempo / Zipkin API.
"""
from __future__ import annotations

from typing import Any, Dict, List

# -- Jaeger / Tempo stub (replace with real HTTP client call) --------------

def fetch_trace_spans(service: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch recent trace spans for `service`.

    TODO: replace the mock below with a real call, e.g.
        requests.get(f"{JAEGER_URL}/api/traces?service={service}&limit={limit}")
    """
    # Mock spans - representative structure
    return [
        {
            "trace_id": "abc123",
            "span_id": "span001",
            "operation": "db.query",
            "service": service,
            "duration_ms": 3200,
            "status": "error",
            "error": "connection pool exhausted",
        },
        {
            "trace_id": "abc123",
            "span_id": "span002",
            "operation": "http.post /checkout",
            "service": service,
            "duration_ms": 4500,
            "status": "timeout",
            "error": None,
        },
    ]


def summarise_traces(spans: List[Dict[str, Any]], service: str) -> str:
    """Produce a short human-readable summary from span dicts."""
    if not spans:
        return f"No trace spans found for {service}."

    error_spans   = [s for s in spans if s.get("status") in ("error", "timeout")]
    slow_spans    = [s for s in spans if s.get("duration_ms", 0) > 1000]

    parts: list[str] = [f"Analysed {len(spans)} trace spans for {service}."]
    if error_spans:
        sample = "; ".join(
            f"{s['operation']} ({s['status']})" for s in error_spans[:3]
        )
        parts.append(f"{len(error_spans)} error/timeout span(s): {sample}.")
    if slow_spans:
        max_ms = max(s["duration_ms"] for s in slow_spans)
        parts.append(f"{len(slow_spans)} slow span(s), worst: {max_ms} ms.")

    return " ".join(parts)
