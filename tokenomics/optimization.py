"""Measurement loop helpers. No model calls or network access."""

from __future__ import annotations

from dataclasses import dataclass

from .models import UsageEvent


@dataclass(frozen=True, slots=True)
class OptimizationMeasurement:
    baseline_tokens: int
    optimized_tokens: int
    actual_tokens_saved: int
    savings_ratio: float


@dataclass(frozen=True, slots=True)
class ReworkFinding:
    event_indexes: tuple[int, ...]
    estimated_rework_tokens: int
    confidence: float
    reason: str


def measure_optimization(baseline_tokens: int, optimized_tokens: int) -> OptimizationMeasurement:
    if baseline_tokens < 0 or optimized_tokens < 0:
        raise ValueError("token counts must be non-negative")
    saved = max(0, baseline_tokens - optimized_tokens)
    ratio = saved / baseline_tokens if baseline_tokens else 0.0
    return OptimizationMeasurement(baseline_tokens, optimized_tokens, saved, ratio)


def detect_rework(events: list[UsageEvent], *, max_gap_seconds: float = 300.0) -> list[ReworkFinding]:
    """Detect conservative same-shape retries within a session.

    This deliberately uses only aggregate metadata. It does not compare prompt or
    response contents, so a finding means "possible rework", not semantic duplication.
    """
    if max_gap_seconds <= 0:
        raise ValueError("max_gap_seconds must be positive")
    findings: list[ReworkFinding] = []
    for index in range(1, len(events)):
        previous, current = events[index - 1], events[index]
        if previous.session_id != current.session_id:
            continue
        gap = (current.timestamp - previous.timestamp).total_seconds()
        if gap < 0 or gap > max_gap_seconds:
            continue
        if (previous.input_tokens, previous.output_tokens) != (current.input_tokens, current.output_tokens):
            continue
        estimated = current.input_tokens + current.output_tokens
        findings.append(
            ReworkFinding(
                event_indexes=(index - 1, index),
                estimated_rework_tokens=estimated,
                confidence=0.65,
                reason="Two same-shape AI calls occurred close together in one session.",
            )
        )
    return findings


def net_savings(actual_tokens_saved: int, tokenomics_overhead_tokens: int) -> int:
    if actual_tokens_saved < 0 or tokenomics_overhead_tokens < 0:
        raise ValueError("token counts must be non-negative")
    return actual_tokens_saved - tokenomics_overhead_tokens
