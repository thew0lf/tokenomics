from tokenomics.detectors import detect_ai_polling, detect_context_repetition, detect_hidden_errors


def test_hidden_error_redirection_is_detected():
    findings = detect_hidden_errors("php bin/console app:report 2>/dev/null")
    assert any(f.rule_id == "hidden-errors" for f in findings)


def test_tail_pipeline_is_detected():
    findings = detect_hidden_errors("docker logs app | tail -20")
    assert any(f.rule_id == "pipeline-status" for f in findings)


def test_polling_is_detected():
    findings = detect_ai_polling("while true; do curl localhost/ai; sleep 5; done", 12)
    assert findings[0].rule_id == "ai-polling"
    assert findings[0].severity == "high"


def test_repeated_context_estimates_avoidable_tokens():
    findings = detect_context_repetition(600, 1000)
    assert findings[0].estimated_avoidable_tokens == 600


def test_small_repetition_is_ignored():
    assert detect_context_repetition(100, 1000) == []
