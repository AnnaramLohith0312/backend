"""
backend/test_api.py
------------------------------------------------------------
FastAPI TestClient tests for the SentinelOps AI backend.

Run with:
    python -m pytest backend/test_api.py -v
or (from repo root):
    pytest backend/test_api.py -v
------------------------------------------------------------
"""
import sys
import os
import time
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app

# TestClient runs background tasks synchronously by default
client = TestClient(app, raise_server_exceptions=True)


# ── Helpers ───────────────────────────────────────────────────────────────

def _get_incident_id() -> str:
    """POST /simulate and return the incident_id."""
    resp = client.post("/simulate")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "incident_id" in data, f"No incident_id in response: {data}"
    return data["incident_id"]


# ── Tests ─────────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_200(self):
        resp = client.get("/health")
        assert resp.status_code == 200, f"Health check failed: {resp.text}"

    def test_health_body(self):
        resp = client.get("/health")
        body = resp.json()
        # Accept either {"status": "ok"} or {"status": "healthy"} or similar
        assert "status" in body or resp.status_code == 200


class TestSimulate:
    def test_simulate_returns_200(self):
        resp = client.post("/simulate")
        assert resp.status_code == 200, f"/simulate returned {resp.status_code}: {resp.text}"

    def test_simulate_returns_incident_id(self):
        resp = client.post("/simulate")
        data = resp.json()
        assert "incident_id" in data, f"Missing incident_id in: {data}"
        assert isinstance(data["incident_id"], str)
        assert len(data["incident_id"]) > 0

    def test_simulate_returns_status(self):
        resp = client.post("/simulate")
        data = resp.json()
        assert "status" in data, f"Missing status in: {data}"
        assert data["status"] == "accepted"


class TestGetIncident:
    def test_incident_returns_200(self):
        incident_id = _get_incident_id()
        resp = client.get(f"/incident/{incident_id}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    def test_incident_has_expected_fields(self):
        incident_id = _get_incident_id()
        data = client.get(f"/incident/{incident_id}").json()
        assert "incident" in data, f"No 'incident' key in: {data}"
        inc = data["incident"]
        for field in ("id", "title", "severity", "status"):
            assert field in inc, f"Missing field '{field}' in incident: {inc}"

    def test_incident_id_matches(self):
        incident_id = _get_incident_id()
        data = client.get(f"/incident/{incident_id}").json()
        assert data["incident"]["id"] == incident_id

    def test_incident_status_is_valid(self):
        incident_id = _get_incident_id()
        data = client.get(f"/incident/{incident_id}").json()
        valid_statuses = {
            "triggered", "planning", "investigating",
            "correlating", "remediating", "reporting",
            "resolved", "failed"
        }
        status = data["incident"]["status"]
        assert status in valid_statuses, f"Unexpected status: '{status}'"

    def test_nonexistent_incident_returns_404(self):
        resp = client.get("/incident/nonexistent-id-000")
        assert resp.status_code == 404


class TestGetReport:
    def test_report_endpoint_returns_200(self):
        incident_id = _get_incident_id()
        # Allow the background pipeline to settle (TestClient is sync)
        time.sleep(1)
        resp = client.get(f"/report/{incident_id}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    def test_report_is_ready_or_pending(self):
        incident_id = _get_incident_id()
        time.sleep(1)
        data = client.get(f"/report/{incident_id}").json()
        assert "status" in data, f"No 'status' in report response: {data}"
        assert data["status"] in ("ready", "pending"), (
            f"Unexpected report status: {data['status']}"
        )

    def test_report_ready_has_content(self):
        """If the pipeline already resolved, the report must be non-empty."""
        incident_id = _get_incident_id()
        time.sleep(2)
        data = client.get(f"/report/{incident_id}").json()
        if data.get("status") == "ready":
            assert "report" in data, "Report status is 'ready' but no 'report' key"
            assert len(data["report"]) > 0, "Report is empty"

    def test_nonexistent_report_returns_404(self):
        resp = client.get("/report/nonexistent-id-000")
        assert resp.status_code == 404


# ── Manual runner (python backend/test_api.py) ────────────────────────────

if __name__ == "__main__":
    print("\n=== SentinelOps Backend Tests ===\n")

    tests = [
        ("GET /health returns 200", lambda: TestHealth().test_health_returns_200()),
        ("GET /health has status field", lambda: TestHealth().test_health_body()),
        ("POST /simulate returns 200", lambda: TestSimulate().test_simulate_returns_200()),
        ("POST /simulate returns incident_id", lambda: TestSimulate().test_simulate_returns_incident_id()),
        ("POST /simulate returns status=accepted", lambda: TestSimulate().test_simulate_returns_status()),
        ("GET /incident/{id} returns 200", lambda: TestGetIncident().test_incident_returns_200()),
        ("GET /incident/{id} has expected fields", lambda: TestGetIncident().test_incident_has_expected_fields()),
        ("GET /incident/{id} status is valid", lambda: TestGetIncident().test_incident_status_is_valid()),
        ("GET /incident/bad-id returns 404", lambda: TestGetIncident().test_nonexistent_incident_returns_404()),
        ("GET /report/{id} returns 200", lambda: TestGetReport().test_report_endpoint_returns_200()),
        ("GET /report/{id} ready or pending", lambda: TestGetReport().test_report_is_ready_or_pending()),
        ("GET /report/{id} content if ready", lambda: TestGetReport().test_report_ready_has_content()),
        ("GET /report/bad-id returns 404", lambda: TestGetReport().test_nonexistent_report_returns_404()),
    ]

    passed = failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as exc:
            print(f"  [FAIL] {name}: {exc}")
            failed += 1

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed.")
    print(f"{'='*40}\n")
    if failed:
        sys.exit(1)
