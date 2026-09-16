from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from .ledger import LossEvent
from .models import UsageEvent

SCHEMA = """
CREATE TABLE IF NOT EXISTS usage_events (
    event_id TEXT PRIMARY KEY, session_id TEXT, timestamp TEXT NOT NULL,
    provider TEXT NOT NULL, model TEXT NOT NULL, input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL, cache_read_tokens INTEGER NOT NULL,
    cache_write_tokens INTEGER NOT NULL, duration_ms INTEGER, metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_usage_events_session ON usage_events(session_id);
CREATE INDEX IF NOT EXISTS idx_usage_events_timestamp ON usage_events(timestamp);
CREATE TABLE IF NOT EXISTS loss_events (
    id TEXT PRIMARY KEY, created_at TEXT NOT NULL, loss_type TEXT NOT NULL,
    estimated_tokens INTEGER NOT NULL, description TEXT NOT NULL, confidence REAL NOT NULL,
    source TEXT NOT NULL, actual_tokens_saved INTEGER, recommendation_accepted INTEGER
);
CREATE INDEX IF NOT EXISTS idx_loss_events_created_at ON loss_events(created_at);
CREATE INDEX IF NOT EXISTS idx_loss_events_type ON loss_events(loss_type);
"""


class EventStore:
    """Small local SQLite store. No network access is performed."""

    def __init__(self, path: str | Path = ".tokenomics/tokenomics.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=5)
        conn.row_factory = sqlite3.Row
        return conn

    def add(self, event: UsageEvent) -> None:
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO usage_events
                (event_id, session_id, timestamp, provider, model, input_tokens,
                 output_tokens, cache_read_tokens, cache_write_tokens, duration_ms, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (event.event_id, event.session_id, event.timestamp.isoformat(), event.provider,
                 event.model, event.input_tokens, event.output_tokens, event.cache_read_tokens,
                 event.cache_write_tokens, event.duration_ms, json.dumps(event.metadata, sort_keys=True)),
            )

    def add_loss(self, event: LossEvent) -> None:
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO loss_events
                (id, created_at, loss_type, estimated_tokens, description, confidence,
                 source, actual_tokens_saved, recommendation_accepted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (event.id, event.created_at.isoformat(), event.loss_type.value, event.estimated_tokens,
                 event.description, event.confidence, event.source, event.actual_tokens_saved,
                 None if event.recommendation_accepted is None else int(event.recommendation_accepted)),
            )

    def update_loss_outcome(self, loss_id: str, actual_tokens_saved: int, recommendation_accepted: bool) -> None:
        if actual_tokens_saved < 0:
            raise ValueError("actual_tokens_saved must be non-negative")
        with self._connect() as conn:
            cursor = conn.execute(
                "UPDATE loss_events SET actual_tokens_saved = ?, recommendation_accepted = ? WHERE id = ?",
                (actual_tokens_saved, int(recommendation_accepted), loss_id),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"loss event not found: {loss_id}")

    def count(self) -> int:
        with self._connect() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM usage_events").fetchone()[0])

    def loss_count(self) -> int:
        with self._connect() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM loss_events").fetchone()[0])

    def totals(self) -> dict[str, int]:
        with self._connect() as conn:
            row = conn.execute(
                """SELECT COALESCE(SUM(input_tokens), 0) AS input_tokens,
                          COALESCE(SUM(output_tokens), 0) AS output_tokens,
                          COALESCE(SUM(cache_read_tokens), 0) AS cache_read_tokens,
                          COALESCE(SUM(cache_write_tokens), 0) AS cache_write_tokens
                   FROM usage_events"""
            ).fetchone()
        return dict(row)

    def events_for_session(self, session_id: str, limit: int = 1000) -> list[UsageEvent]:
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT event_id, session_id, timestamp, provider, model, input_tokens,
                          output_tokens, cache_read_tokens, cache_write_tokens, duration_ms, metadata_json
                   FROM usage_events WHERE session_id = ? ORDER BY timestamp LIMIT ?""",
                (session_id, limit),
            ).fetchall()
        return [
            UsageEvent(provider=row["provider"], model=row["model"], input_tokens=row["input_tokens"],
                       output_tokens=row["output_tokens"], cache_read_tokens=row["cache_read_tokens"],
                       cache_write_tokens=row["cache_write_tokens"], session_id=row["session_id"],
                       timestamp=datetime.fromisoformat(row["timestamp"]), duration_ms=row["duration_ms"],
                       metadata=json.loads(row["metadata_json"]), event_id=row["event_id"])
            for row in rows
        ]

    def losses(self, limit: int = 100) -> list[dict[str, object]]:
        if limit < 1:
            raise ValueError("limit must be positive")
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT id, created_at, loss_type, estimated_tokens, description,
                          confidence, source, actual_tokens_saved, recommendation_accepted
                   FROM loss_events ORDER BY created_at DESC LIMIT ?""", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]

    def savings(self) -> dict[str, int]:
        with self._connect() as conn:
            row = conn.execute(
                """SELECT COALESCE(SUM(estimated_tokens), 0) AS estimated_tokens,
                          COALESCE(SUM(actual_tokens_saved), 0) AS actual_tokens_saved
                   FROM loss_events"""
            ).fetchone()
        return dict(row)
