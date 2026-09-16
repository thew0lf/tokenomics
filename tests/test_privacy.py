import pytest

from tokenomics.models import UsageEvent

LOCAL_SESSION_ID = "550e8400-e29b-41d4-a716-446655440000"


def test_usage_event_rejects_unknown_metadata_keys():
    with pytest.raises(ValueError, match="not privacy-safe"):
        UsageEvent(
            provider="anthropic",
            model="claude-test",
            input_tokens=10,
            output_tokens=5,
            metadata={"prompt": "private conversation"},
        )


def test_usage_event_accepts_allowlisted_metadata():
    event = UsageEvent(
        provider="anthropic",
        model="claude-test",
        input_tokens=10,
        output_tokens=5,
        session_id=LOCAL_SESSION_ID,
        metadata={"cache_hit": True, "finish_reason": "stop", "retry_count": 0},
    )
    assert event.metadata["cache_hit"] is True


def test_usage_event_rejects_provider_conversation_id():
    with pytest.raises(ValueError, match="local UUID4"):
        UsageEvent(
            provider="anthropic",
            model="claude-test",
            input_tokens=10,
            output_tokens=5,
            session_id="provider-conversation-123",
        )
