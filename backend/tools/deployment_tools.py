"""
tools/deployment_tools.py
Simple deployment fetching helpers backed by SQLAlchemy + SQLite.
"""
from __future__ import annotations

from typing import Any, Dict, List

from backend.database import SessionLocal
from backend import models


def get_recent_deployments(service: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch the most recent `limit` deployment records for `service`."""
    db = SessionLocal()
    try:
        rows = (
            db.query(models.Deployment)
            .filter(models.Deployment.service == service)
            .order_by(models.Deployment.timestamp.desc())
            .limit(limit)
            .all()
        )
        result: List[Dict[str, Any]] = []
        for i, r in enumerate(rows):
            entry: Dict[str, Any] = {
                "id":          r.id,
                "service":     r.service,
                "version":     r.version,
                "commit_hash": r.commit_hash,
                "timestamp":   str(r.timestamp),
            }
            # Tag previous stable version for rollback decisions
            if i + 1 < len(rows):
                entry["previous_version"] = rows[i + 1].version
            result.append(entry)
        return result
    finally:
        db.close()


def summarise_deployments(deployments: List[Dict[str, Any]], service: str) -> str:
    """Return a one-paragraph plain-English summary of the deployment list."""
    if not deployments:
        return f"No recent deployments found for {service}."

    latest = deployments[0]
    summary = (
        f"{len(deployments)} deployment(s) for {service}. "
        f"Latest: {latest['version']} at {latest['timestamp']} "
        f"(commit {latest.get('commit_hash', 'N/A')})."
    )
    if latest.get("previous_version"):
        summary += f" Previous stable: {latest['previous_version']}."
    return summary


# Keep old name as alias so existing agent imports don't break
fetch_recent_deployments = get_recent_deployments
