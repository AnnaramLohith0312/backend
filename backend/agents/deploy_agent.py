"""
agents/deploy_agent.py
-----------------------------------------------------------------
Deploy Agent - fetches recent deployments and identifies
potential regression candidates.

Outputs written to AgentState:
  recent_deployments, deployment_summary, agent_outputs, errors
-----------------------------------------------------------------
"""
from __future__ import annotations

from backend.tools.deployment_tools import get_recent_deployments
from .state import AgentState
from .db_utils import update_incident_status


def deploy_agent(state: AgentState) -> AgentState:
    """LangGraph node - fetches and summarises recent deployments."""
    print("[DeployAgent] Checking deployments...")
    
    incident_id = state.get("incident_id")
    update_incident_status(incident_id, "investigating")

    try:
        payload = state.get("alert_payload") or {}
        service = payload.get("service", "unknown")

        try:
            deployments = get_recent_deployments(service, limit=10)
        except Exception as exc:
            error_msg = f"DeployAgent error: {exc}"
            print(f"[DeployAgent] {error_msg}")
            update_incident_status(incident_id, "failed")
            errors = list(state.get("errors") or [])
            errors.append(error_msg)
            return {
                "recent_deployments": [],
                "deployment_summary": "Deployment fetch failed.",
                "errors": errors,
            }

        recent_count = len(deployments)
        rollback_candidate = None
        
        if not deployments:
            summary = f"No recent deployments found for {service}."
        else:
            latest = deployments[0]
            version = latest.get("version", "unknown")
            commit = latest.get("commit_hash", "unknown")
            
            # Check if there is a previous version to rollback to
            if latest.get("previous_version"):
                rollback_candidate = latest["previous_version"]
                
            summary = f"Found {recent_count} recent deployment(s) for {service}. Latest is {version} (commit {commit})."
            if rollback_candidate:
                summary += f" Previous stable version: {rollback_candidate}."

        print(f"[DeployAgent] {summary}")

        agent_outputs = dict(state.get("agent_outputs") or {})
        agent_outputs["deploy_agent"] = {
            "service": service,
            "recent_count": recent_count,
            "rollback_candidate": rollback_candidate,
            "summary": summary,
        }

        return {
            "recent_deployments": deployments,
            "deployment_summary": summary,
            "agent_outputs": agent_outputs,
        }
    except Exception as e:
        error_msg = f"DeployAgent unhandled error: {e}"
        print(f"[DeployAgent] {error_msg}")
        update_incident_status(incident_id, "failed")
        errors = list(state.get("errors") or [])
        errors.append(error_msg)
        return {"errors": errors}


# Alias for compatibility with existing graph.py
deploy_agent_node = deploy_agent
