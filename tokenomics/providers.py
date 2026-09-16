"""Provider adapters that extract usage metadata without storing model content."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import uuid4

from .models import UsageEvent


class UsageAdapter(Protocol):
    provider: str

    def from_response(
        self, response: Any, *, model: str, session_id: str | None = None, duration_ms: int | None = None
    ) -> UsageEvent: ...


def _value(source: Any, name: str, default: int = 0) -> int:
    if isinstance(source, dict):
        return int(source.get(name, default) or default)
    return int(getattr(source, name, default) or default)


@dataclass(frozen=True, slots=True)
class AnthropicUsageAdapter:
    """Extract usage fields from an Anthropic Messages API response.

    Only numeric usage fields and a generated local session ID are retained.
    The response content is never copied into the event.
    """

    provider: str = "anthropic"

    def from_response(
        self,
        response: Any,
        *,
        model: str,
        session_id: str | None = None,
        duration_ms: int | None = None,
    ) -> UsageEvent:
        usage = response.get("usage") if isinstance(response, dict) else getattr(response, "usage", None)
        if usage is None:
            raise ValueError("Anthropic response does not contain usage data")

        return UsageEvent(
            provider=self.provider,
            model=model,
            input_tokens=_value(usage, "input_tokens"),
            output_tokens=_value(usage, "output_tokens"),
            cache_read_tokens=_value(usage, "cache_read_input_tokens"),
            cache_write_tokens=_value(usage, "cache_creation_input_tokens"),
            session_id=session_id or str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            duration_ms=duration_ms,
        )


class SessionTracker:
    """Reconstruct session aggregates from privacy-safe usage events."""

    @staticmethod
    def summarize(events: list[UsageEvent]) -> dict[str, object]:
        if not events:
            return {"events": 0, "sessions": 0, "tokens": 0, "duration_ms": 0}
        sessions = {event.session_id for event in events}
        return {
            "events": len(events),
            "sessions": len(sessions),
            "tokens": sum(event.total_tokens for event in events),
            "duration_ms": sum(event.duration_ms or 0 for event in events),
        }
