import pytest

from tokenomics.ledger import LossEvent, LossType


def test_loss_event_rejects_negative_tokens():
    with pytest.raises(ValueError, match="non-negative"):
        LossEvent(LossType.POLLING, -1, "invalid")


def test_loss_event_rejects_negative_realized_savings():
    with pytest.raises(ValueError, match="actual_tokens_saved"):
        LossEvent(
            LossType.POLLING,
            estimated_tokens=100,
            description="invalid realized savings",
            actual_tokens_saved=-1,
        )


def test_loss_event_rejects_invalid_confidence():
    with pytest.raises(ValueError, match="between 0 and 1"):
        LossEvent(LossType.REWORK, 10, "invalid", confidence=1.1)


def test_loss_event_rejects_blank_description():
    with pytest.raises(ValueError, match="description"):
        LossEvent(LossType.REWORK, 10, "   ")


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
