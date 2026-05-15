"""
tools/github_tools.py
GitHub API helpers - fetch commits, PRs, and file diffs associated with a
deployment.  Set GITHUB_TOKEN + GITHUB_REPO env vars to enable.
"""
from __future__ import annotations

import os
import json
import urllib.request
import urllib.error
from typing import Any, Dict, List

GITHUB_TOKEN: str | None = os.getenv("GITHUB_TOKEN")
GITHUB_REPO:  str | None = os.getenv("GITHUB_REPO")   # e.g. "org/repo-name"
GITHUB_API   = "https://api.github.com"


def _gh_get(path: str) -> Any:
    """Make an authenticated GET request to the GitHub API."""
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN environment variable not configured.")

    url = f"{GITHUB_API}{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub API request failed: {exc}") from exc


def get_commit_details(commit_sha: str, repo: str | None = None) -> Dict[str, Any]:
    """Return metadata and changed files for a specific commit."""
    repo = repo or GITHUB_REPO
    if not repo:
        raise RuntimeError("GITHUB_REPO not configured.")
    data = _gh_get(f"/repos/{repo}/commits/{commit_sha}")
    return {
        "sha": data.get("sha"),
        "message": data.get("commit", {}).get("message", ""),
        "author": data.get("commit", {}).get("author", {}).get("name", ""),
        "date": data.get("commit", {}).get("author", {}).get("date", ""),
        "files_changed": [f["filename"] for f in data.get("files", [])],
        "additions": data.get("stats", {}).get("additions", 0),
        "deletions": data.get("stats", {}).get("deletions", 0),
    }


def get_recent_prs(repo: str | None = None, state: str = "closed", per_page: int = 5) -> List[Dict[str, Any]]:
    """Return recent PRs for the repo."""
    repo = repo or GITHUB_REPO
    if not repo:
        raise RuntimeError("GITHUB_REPO not configured.")
    data = _gh_get(f"/repos/{repo}/pulls?state={state}&per_page={per_page}&sort=updated&direction=desc")
    return [
        {
            "number": pr.get("number"),
            "title":  pr.get("title"),
            "merged_at": pr.get("merged_at"),
            "user": pr.get("user", {}).get("login"),
            "url": pr.get("html_url"),
        }
        for pr in data
    ]
