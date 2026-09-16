from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


SAFE_METADATA_KEYS = frozenset(
    {
        "cache_hit",
        "finish_reason",
        "http_status",
        "retry_count",
        "temperature",
        "max_tokens",
    }
)


@dataclass(slots=True)
class UsageEvent:
    """A privacy-safe record of one AI interaction.

    Raw prompts and responses are intentionally not part of this model. Metadata
    is allowlisted so callers cannot accidentally persist arbitrary conversation
    or project data in the local event store.
    """

    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    session_id: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        for name in ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens"):
            value = getattr(self, name)
            if value < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.duration_ms is not None and self.duration_ms < 0:
            raise ValueError("duration_ms cannot be negative")
        unknown = set(self.metadata) - SAFE_METADATA_KEYS
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(f"metadata keys are not privacy-safe: {names}")

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens
