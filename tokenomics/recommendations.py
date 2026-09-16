"""Turn deterministic findings into actionable, privacy-safe recommendations."""

from dataclasses import dataclass

from .detectors import Finding


@dataclass(frozen=True, slots=True)
class Recommendation:
    rule_id: str
    action: str
    rationale: str
    estimated_savings_tokens: int


_ACTIONS = {
    "hidden-errors": (
        "Keep stderr visible and handle expected failures explicitly.",
        "Hidden failures can cause unnecessary retries and rework.",
    ),
    "pipeline-status": (
        "Capture the command exit status before truncating output.",
        "A presentation command should not become the source of truth for success.",
    ),
    "ai-polling": (
        "Monitor state locally and invoke AI only when meaningful state changes.",
        "Repeated unchanged state can create a large token stream with little new information.",
    ),
    "repeated-context": (
        "Keep stable context local and send only the changed or necessary portion.",
        "Repeated context consumes input tokens without adding equivalent new information.",
    ),
}


def recommendation_for_rule(rule_id: str) -> tuple[str, str]:
    """Return the deterministic action and rationale for a finding rule."""
    return _ACTIONS.get(
        rule_id,
        (
            "Review the interaction for avoidable repeated work.",
            "Potential token waste was detected.",
        ),
    )


def recommend(findings: list[Finding]) -> list[Recommendation]:
    """Generate deterministic recommendations without calling an AI service."""
    results: list[Recommendation] = []
    for finding in findings:
        action, rationale = recommendation_for_rule(finding.rule_id)
        results.append(
            Recommendation(
                rule_id=finding.rule_id,
                action=action,
                rationale=rationale,
                estimated_savings_tokens=finding.estimated_avoidable_tokens,
            )
        )
    return results
