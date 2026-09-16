from tokenomics.models import UsageEvent
from tokenomics.storage import EventStore


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
            session_id="session-1",
        )
    )

    assert store.count() == 1
    assert store.totals() == {
        "input_tokens": 1000,
        "output_tokens": 250,
        "cache_read_tokens": 100,
        "cache_write_tokens": 50,
    }
