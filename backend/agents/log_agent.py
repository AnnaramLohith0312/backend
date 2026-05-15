"""
agents/log_agent.py
-----------------------------------------------------------------
Log Agent - fetches log records for the affected service,
analyzes frequency of errors, and produces a concise summary.

Outputs written to AgentState:
  raw_logs, logs_summary, agent_outputs, errors
-----------------------------------------------------------------
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from backend.tools.log_tools import get_recent_logs
from .state import AgentState
from .db_utils import update_incident_status


def log_agent(state: AgentState) -> AgentState:
    """LangGraph node - fetches and summarises service logs."""
    print("[LogAgent] Fetching logs...")
    
    incident_id = state.get("incident_id")
    update_incident_status(incident_id, "investigating")

    try:
        payload = state.get("alert_payload") or {}
        service = payload.get("service", "unknown")

        try:
            raw_logs = get_recent_logs(service, limit=50)
        except Exception as exc:
            error_msg = f"LogAgent error: {exc}"
            print(f"[LogAgent] {error_msg}")
            update_incident_status(incident_id, "failed")
            return {
                "raw_logs": [],
                "logs_summary": "Log fetch failed.",
                "errors": [error_msg],
            }

        log_count = len(raw_logs)
        error_logs = [
            log for log in raw_logs 
            if log.get("level", "").upper() in ("ERROR", "CRITICAL")
        ]
        
        top_errors: list[dict[str, Any]] = []

        if not raw_logs:
            logs_summary = f"No logs found for {service}."
        elif not error_logs:
            logs_summary = f"Analysed {log_count} log entries for {service}. No errors detected."
        else:
            counter = Counter(log.get("message", "Unknown error") for log in error_logs)
            top_errors = [{"message": msg, "count": count} for msg, count in counter.most_common(3)]
            
            sample = "; ".join(f"{item['message']} ({item['count']}x)" for item in top_errors)
            logs_summary = f"Analysed {log_count} log entries for {service}. Found {len(error_logs)} error(s). Top: {sample}"

        print(f"[LogAgent] {logs_summary}")

        agent_outputs = dict(state.get("agent_outputs") or {})
        agent_outputs["log_agent"] = {
            "service": service,
            "log_count": log_count,
            "top_errors": top_errors,
            "summary": logs_summary,
        }

        return {
            "raw_logs": raw_logs,
            "logs_summary": logs_summary,
            "agent_outputs": agent_outputs,
        }
    except Exception as e:
        error_msg = f"LogAgent unhandled error: {e}"
        print(f"[LogAgent] {error_msg}")
        update_incident_status(incident_id, "failed")
        return {"errors": [error_msg]}

# Alias so graph.py keeps working unchanged
log_agent_node = log_agent
