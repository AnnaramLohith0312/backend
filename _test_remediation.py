from backend.agents.remediation_agent import remediation_agent
from backend.agents.state import AgentState

# Test 1 — deployment-triggered incident (rollback should be #1)
state = AgentState(
    probable_root_cause="Recent deployment change",
    confidence_score=0.85,
    deployment_summary="Found 2 deployments. Latest is v2.14.0 (commit 8f92a1c).",
    historical_matches=[
        {"action": "Rollback v2.13.5", "outcome": "resolved", "confidence": 0.9}
    ],
)
res = remediation_agent(state)
out = res["agent_outputs"]["remediation_agent"]
print("Recommended:", out["recommended_action"])
for c in out["candidates"]:
    print(f"  [{c['confidence']}] {c['action']}")

assert "rollback" in out["recommended_action"].lower(), "Rollback should be top candidate"
print()
print("Test 1 PASS: rollback preferred for deployment incident")

# Test 2 — no clear cause (fallback)
state2 = AgentState(
    probable_root_cause="Undetermined",
    confidence_score=0.4,
    deployment_summary="",
    historical_matches=[],
)
res2 = remediation_agent(state2)
out2 = res2["agent_outputs"]["remediation_agent"]
print("Test 2 recommended:", out2["recommended_action"])
assert "escalate" in out2["recommended_action"].lower()
print("Test 2 PASS: fallback escalation")
print()
print("All tests passed.")
