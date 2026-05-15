from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone

from backend import models
from backend.database import engine, get_db
from backend.agents.graph import run_investigation

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SentinelOps AI",
    description="Autonomous incident investigation from webhook to report.",
    version="1.0.0",
)

# CORS — allow all origins for local development / hackathon demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request schemas ───────────────────────────────────────────────────────

class AlertPayload(BaseModel):
    service: str
    severity: str
    message: str


# ── Health check ──────────────────────────────────────────────────────────

@app.get("/health", tags=["Meta"])
def health():
    """Simple liveness probe."""
    return {"status": "ok", "service": "SentinelOps AI"}


# ── Webhook ingestion ─────────────────────────────────────────────────────

@app.post("/webhook/alert", tags=["Incidents"])
async def receive_alert(
    payload: AlertPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Accept an incoming alert, create an Incident, and kick off investigation."""
    incident = models.Incident(
        title=f"Alert: {payload.message} on {payload.service}",
        severity=payload.severity,
        status="triggered",
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    background_tasks.add_task(run_investigation, incident.id, payload.model_dump())

    return {"status": "accepted", "incident_id": incident.id}


# ── Incident endpoints ────────────────────────────────────────────────────

@app.get("/incidents", tags=["Incidents"])
def list_incidents(
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    List incidents, newest first.
    Optional query param: ?status=investigating|resolved
    """
    query = db.query(models.Incident).order_by(models.Incident.created_at.desc())
    if status:
        query = query.filter(models.Incident.status == status)
    incidents = query.limit(limit).all()
    return {
        "count": len(incidents),
        "incidents": [
            {
                "id":         inc.id,
                "title":      inc.title,
                "severity":   inc.severity,
                "status":     inc.status,
                "created_at": str(inc.created_at),
                "has_report": bool(inc.summary),
            }
            for inc in incidents
        ],
    }


@app.get("/incident/{incident_id}", tags=["Incidents"])
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Get full incident details including investigation outputs and remediation history."""
    import json as _json

    incident = db.query(models.Incident).filter(
        models.Incident.id == incident_id
    ).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    history = db.query(models.RemediationHistory).filter(
        models.RemediationHistory.incident_id == incident_id
    ).all()

    # Decode stored agent_outputs JSON (safe fallback to empty dict)
    try:
        agent_outputs = _json.loads(incident.agent_outputs_json or "{}")
    except Exception:
        agent_outputs = {}

    return {
        "incident": {
            "id":                   incident.id,
            "title":                incident.title,
            "severity":             incident.severity,
            "status":               incident.status,
            "created_at":           str(incident.created_at),
            "summary":              incident.summary,
            "probable_root_cause":  incident.probable_root_cause,
            "causal_chain":         incident.causal_chain,
            "confidence_score":     incident.confidence_score,
            "remediation_action":   incident.remediation_action,
        },
        "agent_outputs": agent_outputs,
        "remediation_history": [
            {
                "id":         h.id,
                "action":     h.action,
                "outcome":    h.outcome,
                "confidence": h.confidence,
            }
            for h in history
        ],
    }


@app.get("/report/{incident_id}", tags=["Reports"])
def get_report(incident_id: str, db: Session = Depends(get_db)):
    """Return the Markdown incident report, or a progress message if not ready."""
    incident = db.query(models.Incident).filter(
        models.Incident.id == incident_id
    ).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if not incident.summary:
        return {"status": "pending", "message": "Report generation in progress."}

    return {"status": "ready", "report": incident.summary}


# ── Simulate endpoint ─────────────────────────────────────────────────────

@app.post("/simulate", tags=["Dev"])
async def simulate_incident(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Seed mock data and trigger a billing-service latency incident.
    Useful for demos and local testing.
    """
    log1    = models.Log(
        service="billing-service",
        level="ERROR",
        message="Database Connection Pool Exhaustion",
        timestamp=datetime.now(timezone.utc),
    )
    deploy1 = models.Deployment(
        service="billing-service",
        version="v2.14.0",
        timestamp=datetime.now(timezone.utc),
        commit_hash="8f92a1c",
    )
    db.add_all([log1, deploy1])
    db.commit()

    payload = AlertPayload(
        service="billing-service",
        severity="high",
        message="Latency spike detected (P99 > 2.4s)",
    )
    return await receive_alert(payload, background_tasks, db)
