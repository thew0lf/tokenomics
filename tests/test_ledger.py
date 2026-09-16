from tokenomics.ledger import LossEvent, LossType


def test_loss_event_rejects_negative_tokens():
    try:
        LossEvent(LossType.POLLING, -1, "invalid")
    except ValueError as exc:
        assert "non-negative" in str(exc)
    else:
        raise AssertionError("negative token estimates must be rejected")


def test_loss_event_rejects_invalid_confidence():
    try:
        LossEvent(LossType.REWORK, 10, "invalid", confidence=1.1)
    except ValueError as exc:
        assert "between 0 and 1" in str(exc)
    else:
        raise AssertionError("invalid confidence must be rejected")


def test_loss_event_can_record_realized_savings():
    event = LossEvent(
        LossType.REPEATED_CONTEXT,
        estimated_tokens=1000,
        description="Repeated context",
        confidence=0.9,
    )
    event.recommendation_accepted = True
    event.actual_tokens_saved = 720
    assert event.realized_savings == 720
