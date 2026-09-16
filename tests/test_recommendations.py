from tokenomics.detectors import detect_ai_polling, detect_context_repetition
from tokenomics.recommendations import recommend


def test_polling_recommendation_is_actionable():
    findings = detect_ai_polling("while true; do curl localhost/ai; sleep 5; done", 12)
    results = recommend(findings)
    assert len(results) == 1
    assert results[0].rule_id == "ai-polling"
    assert "locally" in results[0].action


def test_repeated_context_estimate_flows_to_recommendation():
    findings = detect_context_repetition(750, 1000)
    results = recommend(findings)
    assert results[0].estimated_savings_tokens == 750
