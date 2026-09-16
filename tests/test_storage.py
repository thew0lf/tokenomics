from tokenomics.ledger import LossEvent, LossType
from tokenomics.models import UsageEvent
from tokenomics.storage import EventStore

LOCAL_SESSION_ID = "550e8400-e29b-41d4-a716-446655440000"


def test_event_store_persists_usage(tmp_path):
    store = EventStore(tmp_path / "tokenomics.db")
    store.add(
        UsageEvent(
            provider="anthropic",
            model="claude-test",
            input_tokens=1000,
            output_tokens=250,
            cache_read_tokens=100,
            cache_write_tokens=50,
            session_id=LOCAL_SESSION_ID,
        )
    )

    assert store.count() == 1
    assert store.totals() == {
        "input_tokens": 1000,
        "output_tokens": 250,
        "cache_read_tokens": 100,
        "cache_write_tokens": 50,
    }


def test_event_store_persists_loss_event(tmp_path):
    store = EventStore(tmp_path / "tokenomics.db")
    store.add_loss(
        LossEvent(
            loss_type=LossType.POLLING,
            estimated_tokens=12000,
            description="AI invoked repeatedly without meaningful state changes.",
            confidence=0.85,
        )
    )
    assert store.loss_count() == 1
    assert store.savings() == {"estimated_tokens": 12000, "actual_tokens_saved": 0}
    assert store.losses()[0]["loss_type"] == "polling"


def test_event_store_updates_loss_outcome(tmp_path):
    store = EventStore(tmp_path / "tokenomics.db")
    event = LossEvent(
        loss_type=LossType.REPEATED_CONTEXT,
        estimated_tokens=1000,
        description="Repeated context",
        confidence=0.9,
    )
    store.add_loss(event)

    store.update_loss_outcome(event.id, actual_tokens_saved=720, recommendation_accepted=True)

    assert store.losses()[0]["actual_tokens_saved"] == 720
    assert store.losses()[0]["recommendation_accepted"] == 1
    assert store.savings() == {"estimated_tokens": 1000, "actual_tokens_saved": 720}


def test_event_store_rejects_unknown_loss_outcome(tmp_path):
    store = EventStore(tmp_path / "tokenomics.db")
    try:
        store.update_loss_outcome("missing", actual_tokens_saved=1, recommendation_accepted=False)
    except KeyError as exc:
        assert "missing" in str(exc)
    else:
        raise AssertionError("expected missing loss event to raise KeyError")
