"""
tools/memory_tools.py
Simple memory / history helpers backed by SQLAlchemy + SQLite.
No vector search yet - just plain DB queries.
"""
from __future__ import annotations

from typing import Any, Dict, List

from backend.database import SessionLocal
from backend import models


def get_recent_remediation_history(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch the most recent `limit` remediation history rows."""
    db = SessionLocal()
    try:
        rows = (
            db.query(models.RemediationHistory)
            .order_by(models.RemediationHistory.id.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id":          r.id,
                "incident_id": r.incident_id,
                "action":      r.action,
                "outcome":     r.outcome,
                "confidence":  r.confidence,
            }
            for r in rows
        ]
    finally:
        db.close()


def search_similar_incidents(
    service: str,
    hint: str = "",
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Return up to `top_k` past resolved incidents for the same service.
    Simple string-match; swap for vector search when embeddings are added.
    """
    db = SessionLocal()
    try:
        rows = (
            db.query(models.Incident)
            .filter(
                models.Incident.status == "resolved",
                models.Incident.title.contains(service),
            )
            .order_by(models.Incident.created_at.desc())
            .limit(top_k)
            .all()
        )
        return [
            {
                "id":         r.id,
                "title":      r.title,
                "severity":   r.severity,
                "summary":    r.summary or "",
                "created_at": str(r.created_at),
            }
            for r in rows
        ]
    finally:
        db.close()


def format_memory_context(incidents: List[Dict[str, Any]]) -> str:
    """Turn a list of past incidents into a concise context string."""
    if not incidents:
        return "No similar past incidents found."
    lines = ["Similar resolved incidents:"]
    for inc in incidents:
        lines.append(
            f"- [{inc['severity'].upper()}] {inc['title']} "
            f"(resolved {str(inc['created_at'])[:10]}): "
            f"{str(inc['summary'])[:120]}..."
        )
    return "\n".join(lines)
