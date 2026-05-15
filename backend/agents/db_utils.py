"""
agents/db_utils.py
-----------------------------------------------------------------
Shared DB helper used by all agent nodes to persist incident
status transitions without opening a new FastAPI dependency.
-----------------------------------------------------------------
"""
from __future__ import annotations

from backend.database import SessionLocal
from backend import models


def update_incident_status(incident_id: str, status: str) -> None:
    """Persist a status transition for incident_id.

    Skips silently if incident_id is empty or the incident is already
    marked 'failed' (failure is a terminal state).
    """
    if not incident_id:
        return
    db = None
    try:
        db = SessionLocal()
        incident = (
            db.query(models.Incident)
            .filter(models.Incident.id == incident_id)
            .first()
        )
        if incident and incident.status != "failed":
            incident.status = status
            db.commit()
    except Exception as e:
        print(f"[db_utils] Failed to update incident {incident_id} → {status}: {e}")
    finally:
        if db is not None:
            db.close()
