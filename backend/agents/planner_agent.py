"""
agents/planner_agent.py
-----------------------------------------------------------------
Planner Agent - analyses incoming alerts and builds an execution 
plan for the specialist agents.

Phase 2: LLM Integration (Gemini/OpenAI) with rule-based fallback.
-----------------------------------------------------------------
"""
from __future__ import annotations
import os
from typing import Any, Dict, List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from .state import AgentState
from .db_utils import update_incident_status

# -- LLM Schema -------------------------------------------------------------

class PlannerOutput(BaseModel):
    incident_type: str = Field(description="The classified type of incident.")
    priority: str = Field(description="Priority: critical, high, medium, or low.")
    plan: List[str] = Field(description="Ordered list of agent nodes to run.")

# -- Rule-based Fallback (Phase 1 logic) ------------------------------------

def _plan_rule_based(alert_message: str) -> Dict[str, Any]:
    msg = alert_message.lower()
    
    # Defaults
    itype = "unknown"
    priority = "medium"
    
    if any(k in msg for k in ("latency", "slow", "timeout", "p99")):
        itype = "latency_spike"
        priority = "high"
    elif any(k in msg for k in ("deploy", "regression", "version", "rollout")):
        itype = "deploy_regression"
        priority = "high"
    elif any(k in msg for k in ("oom", "memory", "heap", "crash")):
        itype = "oom_crash"
        priority = "critical"
    elif any(k in msg for k in ("db", "query", "pool", "connection")):
        itype = "dependency_failure"
        priority = "high"

    # Plan is always the same for now to ensure stability
    plan = [
        "log_agent",
        "deploy_agent",
        "trace_agent",
        "correlation_agent",
        "memory_agent",
        "remediation_agent",
        "reporter_agent"
    ]
    
    return {
        "incident_type": itype,
        "priority": priority,
        "plan": plan
    }

# -- LLM Planner ------------------------------------------------------------

_PROMPT = """\
You are the SentinelOps Dispatcher. Your job is to analyze an incoming infrastructure alert and decide which investigative agents should be triggered.

ALERT:
Service: {service}
Severity: {severity}
Message: {message}

AVAILABLE AGENTS:
- log_agent: Analyzes service logs for errors.
- deploy_agent: Checks for recent code deployments.
- trace_agent: Inspects distributed traces for latency/errors.
- memory_agent: Looks for similar past incidents.
- correlation_agent: Synthesizes all evidence (MANDATORY).
- remediation_agent: Recommends a fix (MANDATORY).
- reporter_agent: Finalizes the report (MANDATORY).

TASK:
1. Classify the incident_type (e.g. latency_spike, deploy_regression, oom_crash, etc).
2. Assign a priority (critical, high, medium, low).
3. Build the execution plan as an ordered list of agent names.

{format_instructions}
"""

def _plan_llm(service: str, severity: str, message: str) -> Optional[Dict[str, Any]]:
    """Attempt LLM planning using Gemini or OpenAI."""
    try:
        google_key = os.getenv("GOOGLE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        groq_key = os.getenv("GROQ_API_KEY")
        
        llm = None
        if google_key:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=google_key)
        elif groq_key:
            from langchain_groq import ChatGroq
            llm = ChatGroq(model="llama3-70b-8192", groq_api_key=groq_key)
        elif openai_key:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-4-turbo-preview", openai_api_key=openai_key)
        
        if not llm:
            return None

        parser = JsonOutputParser(pydantic_object=PlannerOutput)
        prompt = ChatPromptTemplate.from_template(_PROMPT)
        
        chain = prompt | llm | parser
        
        result = chain.invoke({
            "service": service,
            "severity": severity,
            "message": message,
            "format_instructions": parser.get_format_instructions()
        })
        return result
    except Exception as e:
        print(f"[PlannerAgent] LLM failed: {e}")
        return None

# -- Node -------------------------------------------------------------------

def planner_agent(state: AgentState) -> AgentState:
    """LangGraph node - analyses alert and produces a plan."""
    print("[PlannerAgent] Analysing alert...")
    
    incident_id = state.get("incident_id")
    update_incident_status(incident_id, "planning")

    try:
        payload = state.get("alert_payload", {})
        service = payload.get("service", "unknown")
        severity = payload.get("severity", "medium")
        message = payload.get("message", "")

        # 1. Try LLM
        result = _plan_llm(service=service, severity=severity, message=message)

        # 2. Fallback
        if not result:
            print("[PlannerAgent] Using rule-based fallback logic.")
            result = _plan_rule_based(alert_message=message)
        else:
            print("[PlannerAgent] LLM planning successful.")

        incident_type = result.get("incident_type", "unknown")
        priority = result.get("priority", "medium")
        plan = result.get("plan", [])

        print(f"[PlannerAgent] service={service}  type={incident_type}  "
              f"priority={priority}  plan={plan}")

        agent_outputs = dict(state.get("agent_outputs") or {})
        agent_outputs["planner_agent"] = {
            "engine": "llm" if result.get("engine") != "rules" else "rules",
            "incident_type": incident_type,
            "priority": priority,
            "plan": plan
        }

        return {
            "incident_type": incident_type,
            "priority":      priority,
            "plan":          plan,
            "agent_outputs": agent_outputs,
        }
    except Exception as e:
        error_msg = f"PlannerAgent error: {e}"
        print(f"[PlannerAgent] {error_msg}")
        update_incident_status(incident_id, "failed")
        errors = list(state.get("errors") or [])
        errors.append(error_msg)
        return {"errors": errors}


# Alias
planner_agent_node = planner_agent
