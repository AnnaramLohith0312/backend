"""
agents/trace_agent.py
-----------------------------------------------------------------
Trace Agent - fetches distributed trace spans and surfaces
dependency impact or high latency propagation.

Outputs written to AgentState:
  trace_spans, trace_summary, agent_outputs, errors
-----------------------------------------------------------------
"""
from __future__ import annotations

from typing import Any

from backend.tools.trace_tools import fetch_trace_spans, summarise_traces
from .state import AgentState
from .db_utils import update_incident_status


def _build_dependency_chain(service: str, spans: list[dict[str, Any]]) -> list[str]:
    """Mock a dependency chain analysis based on traces."""
    if not spans:
        return [service]
    
    chain = ["api-gateway", service]
    for span in spans:
        if span.get("status") in ("error", "timeout"):
            op = span.get("operation", "unknown-op")
            if "db" in op.lower():
                chain.append(f"database-cluster ({op})")
            elif "http" in op.lower():
                chain.append(f"downstream-service ({op})")
    
    # Remove duplicates but keep order
    seen = set()
    result = []
    for item in chain:
        if item not in seen:
            seen.add(item)
            result.append(item)
            
    return result


def trace_agent(state: AgentState) -> AgentState:
    """LangGraph node - fetches and summarises distributed traces."""
    print("[TraceAgent] Fetching distributed traces...")
    
    incident_id = state.get("incident_id")
    update_incident_status(incident_id, "investigating")

    try:
        payload = state.get("alert_payload") or {}
        service = payload.get("service", "unknown")

        try:
            spans = fetch_trace_spans(service, limit=100)
            trace_summary = summarise_traces(spans, service)
        except Exception as exc:
            error_msg = f"TraceAgent error: {exc}"
            print(f"[TraceAgent] {error_msg}")
            update_incident_status(incident_id, "failed")
            return {
                "trace_spans": [],
                "trace_summary": "Trace fetch failed.",
                "errors": [error_msg],
            }

        dependency_chain = _build_dependency_chain(service, spans)
        
        if len(dependency_chain) > 2:
            trace_summary += f" Dependency impact detected: {' -> '.join(dependency_chain)}."

        print(f"[TraceAgent] {trace_summary}")

        agent_outputs = dict(state.get("agent_outputs") or {})
        agent_outputs["trace_agent"] = {
            "service": service,
            "span_count": len(spans),
            "dependency_chain": dependency_chain,
            "summary": trace_summary,
        }

        return {
            "trace_spans": spans,
            "trace_summary": trace_summary,
            "agent_outputs": agent_outputs,
        }
    except Exception as e:
        error_msg = f"TraceAgent unhandled error: {e}"
        print(f"[TraceAgent] {error_msg}")
        update_incident_status(incident_id, "failed")
        return {"errors": [error_msg]}


# Alias so graph.py keeps working unchanged
trace_agent_node = trace_agent
