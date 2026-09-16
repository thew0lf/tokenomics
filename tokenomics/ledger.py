"""Local Token Loss Ledger.

The ledger records observations about avoidable token usage without storing
private prompts, responses, source code, or file contents.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4


class LossType(StrEnum):
    """Known categories of token waste."""

    REWORK = "rework"
    REPEATED_CONTEXT = "repeated_context"
    EXCESSIVE_OUTPUT = "excessive_output"
    POLLING = "polling"
    RETRY_LOOP = "retry_loop"
    HIDDEN_ERROR = "hidden_error"
    VERIFICATION = "verification"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class LossEvent:
    """A privacy-safe observation of potential token loss."""

    loss_type: LossType
    estimated_tokens: int
    description: str
    confidence: float = 0.0
    source: str = "detector"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    actual_tokens_saved: int | None = None
    recommendation_accepted: bool | None = None

    def __post_init__(self) -> None:
        if self.estimated_tokens < 0:
            raise ValueError("estimated_tokens must be non-negative")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

    @property
    def realized_savings(self) -> int | None:
        """Return measured savings once the recommendation has been tested."""
        return self.actual_tokens_saved
