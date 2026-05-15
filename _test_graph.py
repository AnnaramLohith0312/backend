from backend.agents.graph import run_investigation

result = run_investigation(
    "test-graph-001",
    {
        "service":  "billing-service",
        "severity": "high",
        "message":  "Latency spike detected (P99 > 2.4s)",
    },
)

agents_run = list(result.get("agent_outputs", {}).keys())
print()
print("Agents completed:", agents_run)
print("Root cause      :", result.get("probable_root_cause"))
print("Confidence      :", f"{result.get('confidence_score', 0):.0%}")
print("Action          :", result.get("remediation_action"))
print()

# Assertions
assert len(agents_run) == 8, f"Expected 8 agents, got {agents_run}"
assert result.get("probable_root_cause"), "No root cause produced"
assert result.get("remediation_action"),  "No remediation action"

expected_order = [
    "planner_agent", "log_agent", "deploy_agent", "trace_agent",
    "correlation_agent", "memory_agent", "remediation_agent", "reporter_agent",
]
assert agents_run == expected_order, f"Order mismatch: {agents_run}"

print("All assertions passed — graph.py refactor verified.")
