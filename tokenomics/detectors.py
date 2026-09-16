from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Finding:
    rule_id: str
    severity: str
    message: str
    evidence: str
    estimated_avoidable_tokens: int = 0


_ERROR_HIDING = re.compile(r"(?:2>\s*/dev/null|>/dev/null\s*2>&1)")
_PIPE_TO_TAIL = re.compile(r"\|\s*tail(?:\s+-\d+)?(?:\s|$)")
_POLLING = re.compile(
    r"(?:while\s+true|watch\s+(?:-n\s+\S+\s+)?|sleep\s+\d+.*(?:curl|wget)|cron|setInterval)",
    re.IGNORECASE | re.DOTALL,
)


def detect_hidden_errors(text: str) -> list[Finding]:
    findings: list[Finding] = []
    if _ERROR_HIDING.search(text):
        findings.append(
            Finding(
                "hidden-errors",
                "high",
                "Command output appears to suppress errors.",
                "2>/dev/null or equivalent detected",
            )
        )
    if _PIPE_TO_TAIL.search(text):
        findings.append(
            Finding(
                "pipeline-status",
                "medium",
                "A pipeline ending in tail can hide an upstream failure status.",
                "command | tail detected",
            )
        )
    return findings


def detect_ai_polling(text: str, calls_per_minute: float | None = None) -> list[Finding]:
    if not _POLLING.search(text):
        return []
    evidence = "Polling or repeated-execution construct detected"
    if calls_per_minute is not None:
        evidence += f"; observed AI call rate: {calls_per_minute:g}/min"
    return [
        Finding(
            "ai-polling",
            "high" if calls_per_minute and calls_per_minute > 10 else "medium",
            "AI appears to be inside a polling or repeated-execution path.",
            evidence,
        )
    ]


def detect_context_repetition(repeated_tokens: int, total_input_tokens: int, threshold: float = 0.50) -> list[Finding]:
    if repeated_tokens < 0 or total_input_tokens < 0:
        raise ValueError("token counts must be non-negative")
    if repeated_tokens > total_input_tokens and total_input_tokens > 0:
        raise ValueError("repeated_tokens cannot exceed total_input_tokens")
    if total_input_tokens == 0 or repeated_tokens == 0:
        return []
    ratio = repeated_tokens / total_input_tokens
    if ratio < threshold:
        return []
    return [
        Finding(
            "repeated-context",
            "medium",
            f"Repeated context accounts for {ratio:.0%} of input tokens.",
            f"{repeated_tokens:,} repeated / {total_input_tokens:,} input tokens",
            repeated_tokens,
        )
    ]
