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
