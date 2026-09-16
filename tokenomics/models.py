from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


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

    Raw prompts, responses, provider conversation IDs, and project content are
    intentionally excluded. Every event gets a local random UUID4 session ID.
    """

    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    session_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        for name in ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens"):
            value = getattr(self, name)
            if value < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.duration_ms is not None and self.duration_ms < 0:
            raise ValueError("duration_ms cannot be negative")
        try:
            session_uuid = UUID(self.session_id)
        except (ValueError, AttributeError, TypeError) as exc:
            raise ValueError("session_id must be a local UUID4") from exc
        if session_uuid.version != 4:
            raise ValueError("session_id must be a local UUID4")
        unknown = set(self.metadata) - SAFE_METADATA_KEYS
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(f"metadata keys are not privacy-safe: {names}")

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens
