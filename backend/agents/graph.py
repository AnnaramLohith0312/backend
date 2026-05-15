"""
agents/graph.py
-----------------------------------------------------------------
LangGraph workflow for SentinelOps AI.

Pipeline order (sequential for stability):
  planner -> log -> deploy -> trace -> correlation
          -> memory -> remediation -> reporter -> END
-----------------------------------------------------------------
"""
from __future__ import annotations

from langgraph.graph import StateGraph, END

from .state import AgentState

# ── Agent imports ─────────────────────────────────────────────────────────
from .planner_agent    import planner_agent
from .log_agent        import log_agent
from .deploy_agent     import deploy_agent
from .trace_agent      import trace_agent
from .correlation_agent import correlation_agent
from .memory_agent     import memory_agent
from .remediation_agent import remediation_agent
from .reporter_agent   import reporter_agent

# ── Graph definition ──────────────────────────────────────────────────────

def _build_graph() -> StateGraph:
    g = StateGraph(AgentState)

    g.add_node("planner_agent",     planner_agent)
    g.add_node("log_agent",         log_agent)
    g.add_node("deploy_agent",      deploy_agent)
    g.add_node("trace_agent",       trace_agent)
    g.add_node("correlation_agent", correlation_agent)
    g.add_node("memory_agent",      memory_agent)
    g.add_node("remediation_agent", remediation_agent)
    g.add_node("reporter_agent",    reporter_agent)

    g.set_entry_point("planner_agent")

    g.add_edge("planner_agent",     "log_agent")
    g.add_edge("log_agent",         "deploy_agent")
    g.add_edge("deploy_agent",      "trace_agent")
    g.add_edge("trace_agent",       "correlation_agent")
    g.add_edge("correlation_agent", "memory_agent")
    g.add_edge("memory_agent",      "remediation_agent")
    g.add_edge("remediation_agent", "reporter_agent")
    g.add_edge("reporter_agent",    END)

    return g.compile()


_graph = _build_graph()


# ── Public entry point ────────────────────────────────────────────────────

def run_investigation(incident_id: str, alert_payload: dict) -> dict:
    """
    Execute the full LangGraph investigation pipeline.

    Args:
        incident_id:   UUID of the DB Incident row created by the webhook handler.
        alert_payload: Dict with at minimum {"service", "severity", "message"}.

    Returns:
        Final AgentState dict after all nodes have run.
    """
    initial_state: AgentState = {
        "incident_id":   incident_id,
        "alert_payload": alert_payload,
        "agent_outputs": {},
        "errors":        [],
    }

    print(f"[Graph] Starting investigation for incident {incident_id}")

    final_state = _graph.invoke(initial_state)

    print(f"[Graph] Investigation complete for incident {incident_id}")
    return final_state
