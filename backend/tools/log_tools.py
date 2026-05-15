"""
tools/log_tools.py
Simple log fetching helpers backed by SQLAlchemy + SQLite.
"""
from __future__ import annotations

from typing import Any, Dict, List

from backend.database import SessionLocal
from backend import models


def get_recent_logs(service: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Fetch the most recent `limit` log records for `service`."""
    db = SessionLocal()
    try:
        rows = (
            db.query(models.Log)
            .filter(models.Log.service == service)
            .order_by(models.Log.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id":        r.id,
                "service":   r.service,
                "level":     r.level,
                "message":   r.message,
                "timestamp": str(r.timestamp),
            }
            for r in rows
        ]
    finally:
        db.close()


def summarise_logs(logs: List[Dict[str, Any]], service: str) -> str:
    """Return a one-paragraph plain-English summary of the log list."""
    if not logs:
        return f"No logs found for {service}."

    errors   = [l for l in logs if l.get("level", "").upper() in ("ERROR", "CRITICAL")]
    warnings = [l for l in logs if l.get("level", "").upper() == "WARNING"]

    parts = [f"Analysed {len(logs)} log entries for {service}."]
    if errors:
        sample = "; ".join(l["message"] for l in errors[:3])
        parts.append(f"{len(errors)} ERROR(s): {sample}")
    if warnings:
        parts.append(f"{len(warnings)} WARNING(s) found.")
    if not errors and not warnings:
        parts.append("No errors or warnings detected.")
    return " ".join(parts)


# Keep old name as alias so existing agent imports don't break
fetch_recent_logs = get_recent_logs
