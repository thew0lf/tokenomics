from datetime import datetime, timedelta, timezone

from tokenomics.models import UsageEvent
from tokenomics.optimization import detect_rework, measure_optimization, net_savings


SESSION = "550e8400-e29b-41d4-a716-446655440000"


def event(ts, input_tokens=100, output_tokens=20):
    return UsageEvent("anthropic", "claude", input_tokens, output_tokens, session_id=SESSION, timestamp=ts)


def test_measure_optimization_distinguishes_realized_savings():
    result = measure_optimization(1000, 700)
    assert result.actual_tokens_saved == 300
    assert result.savings_ratio == 0.3


def test_net_savings_accounts_for_tokenomics_overhead():
    assert net_savings(1000, 150) == 850


def test_rework_detection_is_conservative():
    start = datetime.now(timezone.utc)
    findings = detect_rework([event(start), event(start + timedelta(seconds=20))])
    assert len(findings) == 1
    assert findings[0].estimated_rework_tokens == 120


def test_rework_ignores_different_sessions_and_large_gaps():
    start = datetime.now(timezone.utc)
    other = UsageEvent("anthropic", "claude", 100, 20, timestamp=start + timedelta(seconds=20))
    assert detect_rework([event(start), other]) == []
    assert detect_rework([event(start), event(start + timedelta(seconds=301))]) == []
