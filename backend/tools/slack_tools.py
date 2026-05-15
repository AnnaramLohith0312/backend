"""
tools/slack_tools.py
Slack notification helper.
Set the SLACK_WEBHOOK_URL environment variable to enable real notifications.
If the variable is absent the function raises RuntimeError (caller should
catch and continue silently).
"""
from __future__ import annotations

import os
import json
import urllib.request
import urllib.error


SLACK_WEBHOOK_URL: str | None = os.getenv("SLACK_WEBHOOK_URL")


def send_slack_message(text: str, channel: str | None = None) -> None:
    """
    POST a plain-text message to the configured Slack Incoming Webhook.

    Raises:
        RuntimeError - if SLACK_WEBHOOK_URL is not set or the request fails.
    """
    if not SLACK_WEBHOOK_URL:
        raise RuntimeError("SLACK_WEBHOOK_URL environment variable not configured.")

    payload: dict = {"text": text}
    if channel:
        payload["channel"] = channel

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Slack returned HTTP {resp.status}")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Slack request failed: {exc}") from exc


def send_incident_alert(incident_id: str, service: str, severity: str, action: str) -> None:
    """Convenience wrapper that formats and sends a standard incident alert."""
    emoji = ":rotating_light:" if severity in ("high", "critical") else ":warning:"
    text = (
        f"{emoji} *SentinelOps Alert*\n"
        f">*Incident*: `{incident_id}`\n"
        f">*Service*: `{service}`\n"
        f">*Severity*: `{severity.upper()}`\n"
        f">*Recommended Action*: _{action}_"
    )
    send_slack_message(text)
