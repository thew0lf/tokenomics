from __future__ import annotations

import json
from pathlib import Path
import sqlite3

from .ledger import LossEvent
from .models import UsageEvent


SCHEMA = """
CREATE TABLE IF NOT EXISTS usage_events (
    event_id TEXT PRIMARY KEY,
    session_id TEXT,
    timestamp TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    cache_read_tokens INTEGER NOT NULL,
    cache_write_tokens INTEGER NOT NULL,
    duration_ms INTEGER,
    metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_usage_events_session ON usage_events(session_id);
CREATE INDEX IF NOT EXISTS idx_usage_events_timestamp ON usage_events(timestamp);

CREATE TABLE IF NOT EXISTS loss_events (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    loss_type TEXT NOT NULL,
    estimated_tokens INTEGER NOT NULL,
    description TEXT NOT NULL,
    confidence REAL NOT NULL,
    source TEXT NOT NULL,
    actual_tokens_saved INTEGER,
    recommendation_accepted INTEGER
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
                (
                    event.event_id,
                    event.session_id,
                    event.timestamp.isoformat(),
                    event.provider,
                    event.model,
                    event.input_tokens,
                    event.output_tokens,
                    event.cache_read_tokens,
                    event.cache_write_tokens,
                    event.duration_ms,
                    json.dumps(event.metadata, sort_keys=True),
                ),
            )

    def add_loss(self, event: LossEvent) -> None:
        """Persist a privacy-safe loss observation."""
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO loss_events
                (id, created_at, loss_type, estimated_tokens, description, confidence,
                 source, actual_tokens_saved, recommendation_accepted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event.id,
                    event.created_at.isoformat(),
                    event.loss_type.value,
                    event.estimated_tokens,
                    event.description,
                    event.confidence,
                    event.source,
                    event.actual_tokens_saved,
                    None
                    if event.recommendation_accepted is None
                    else int(event.recommendation_accepted),
                ),
            )

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

    def losses(self, limit: int = 100) -> list[dict[str, object]]:
        """Return recent loss observations without private content."""
        if limit < 1:
            raise ValueError("limit must be positive")
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT id, created_at, loss_type, estimated_tokens, description,
                          confidence, source, actual_tokens_saved, recommendation_accepted
                   FROM loss_events
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def savings(self) -> dict[str, int]:
        """Summarize estimated and measured token savings from the loss ledger."""
        with self._connect() as conn:
            row = conn.execute(
                """SELECT COALESCE(SUM(estimated_tokens), 0) AS estimated_tokens,
                          COALESCE(SUM(actual_tokens_saved), 0) AS actual_tokens_saved
                   FROM loss_events"""
            ).fetchone()
        return dict(row)
