"""
E2E API test: /simulate -> /incident/{id} -> /report/{id}
"""
import urllib.request, json, time

BASE = "http://127.0.0.1:8009"

# ── Step 1: POST /simulate ─────────────────────────────────────────────
print("STEP 1: POST /simulate")
req = urllib.request.Request(f"{BASE}/simulate", method="POST")
req.add_header("Content-Type", "application/json")
with urllib.request.urlopen(req) as r:
    sim = json.loads(r.read())
print("  Response:", sim)
incident_id = sim["incident_id"]
assert incident_id, "No incident_id returned"
print(f"  Incident ID: {incident_id}")

# ── Step 2: Poll until resolved (background task) ─────────────────────
print("\nSTEP 2: Polling GET /incident/{id} until resolved...")
for attempt in range(15):
    time.sleep(2)
    with urllib.request.urlopen(f"{BASE}/incident/{incident_id}") as r:
        data = json.loads(r.read())
    status = data["incident"]["status"]
    print(f"  Attempt {attempt+1}: status={status}")
    if status == "resolved":
        break
else:
    raise AssertionError("Incident never resolved after 30s")

# ── Step 3: Validate all enriched fields ─────────────────────────────
print("\nSTEP 3: Validating enriched GET /incident/{id}")
inc = data["incident"]
agent_outputs = data.get("agent_outputs", {})
history = data.get("remediation_history", [])

print(f"  probable_root_cause : {inc.get('probable_root_cause')}")
print(f"  causal_chain        : {str(inc.get('causal_chain', ''))[:80]}...")
print(f"  confidence_score    : {inc.get('confidence_score')}")
print(f"  remediation_action  : {inc.get('remediation_action')}")
print(f"  agent_outputs keys  : {list(agent_outputs.keys())}")
print(f"  remediation_history : {len(history)} row(s)")

assert inc.get("probable_root_cause"),  "probable_root_cause missing"
assert inc.get("causal_chain"),         "causal_chain missing"
assert inc.get("confidence_score"),     "confidence_score missing"
assert inc.get("remediation_action"),   "remediation_action missing"
assert len(agent_outputs) == 8,         f"Expected 8 agent_outputs, got {len(agent_outputs)}"
assert "planner_agent"    in agent_outputs
assert "log_agent"        in agent_outputs
assert "deploy_agent"     in agent_outputs
assert "trace_agent"      in agent_outputs
assert "correlation_agent" in agent_outputs
assert "memory_agent"     in agent_outputs
assert "remediation_agent" in agent_outputs
assert "reporter_agent"   in agent_outputs
print("  All field assertions PASSED")

# ── Step 4: GET /report/{id} ──────────────────────────────────────────
print("\nSTEP 4: GET /report/{id}")
with urllib.request.urlopen(f"{BASE}/report/{incident_id}") as r:
    report = json.loads(r.read())
print(f"  status : {report.get('status')}")
print(f"  report : {str(report.get('report', ''))[:120]}...")
assert report.get("status") == "ready",        "Report not ready"
assert "SentinelOps Incident Report" in report["report"], "Report content missing"
print("  Report assertion PASSED")

print("\n========================================")
print("All E2E assertions PASSED.")
print("========================================")
