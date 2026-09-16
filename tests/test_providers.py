from tokenomics.providers import AnthropicUsageAdapter, SessionTracker

SESSION = "550e8400-e29b-41d4-a716-446655440000"


def test_anthropic_adapter_extracts_only_usage():
    response = {
        "usage": {
            "input_tokens": 1000,
            "output_tokens": 250,
            "cache_read_input_tokens": 400,
            "cache_creation_input_tokens": 50,
        },
        "content": [{"text": "private response that must not be stored"}],
    }
    event = AnthropicUsageAdapter().from_response(
        response, model="claude-test", session_id=SESSION
    )
    assert event.total_tokens == 1250
    assert event.cache_read_tokens == 400
    assert event.cache_write_tokens == 50
    assert event.session_id == SESSION
    assert not hasattr(event, "content")


def test_anthropic_adapter_requires_usage():
    try:
        AnthropicUsageAdapter().from_response({"content": []}, model="claude-test")
    except ValueError as exc:
        assert "usage" in str(exc)
    else:
        raise AssertionError("missing usage must be rejected")


def test_session_tracker_aggregates_events():
    adapter = AnthropicUsageAdapter()
    events = [
        adapter.from_response(
            {"usage": {"input_tokens": 100, "output_tokens": 10}},
            model="m",
            session_id=SESSION,
        ),
        adapter.from_response(
            {"usage": {"input_tokens": 200, "output_tokens": 20}},
            model="m",
            session_id=SESSION,
        ),
    ]
    assert SessionTracker.summarize(events) == {
        "events": 2,
        "sessions": 1,
        "tokens": 330,
        "duration_ms": 0,
    }
