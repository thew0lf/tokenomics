"""Provider-neutral planning-time cost and review recommendations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Iterable, Mapping

_COMPLEXITY = {"low": 1, "medium": 2, "high": 3}


@dataclass(frozen=True, slots=True)
class ModelProfile:
    """Caller-supplied pricing and capability information for one model."""

    name: str
    provider: str
    input_per_million: float
    output_per_million: float
    capabilities: frozenset[str]
    max_complexity: str

    def __post_init__(self) -> None:
        if not self.name or not self.provider:
            raise ValueError("model profile name and provider are required")
        if not isfinite(self.input_per_million) or not isfinite(self.output_per_million):
            raise ValueError("model pricing must be finite")
        if self.input_per_million < 0 or self.output_per_million < 0:
            raise ValueError("model pricing must be non-negative")
        if not self.capabilities:
            raise ValueError("model profile must declare at least one capability")
        if self.max_complexity not in _COMPLEXITY:
            raise ValueError("max_complexity must be low, medium, or high")

    def supports(self, task_class: str, complexity: str) -> bool:
        return task_class in self.capabilities and _COMPLEXITY[complexity] <= _COMPLEXITY[self.max_complexity]

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        if input_tokens < 0 or output_tokens < 0:
            raise ValueError("token counts must be non-negative")
        return input_tokens / 1_000_000 * self.input_per_million + output_tokens / 1_000_000 * self.output_per_million


@dataclass(frozen=True, slots=True)
class PlanningRecommendation:
    """A recommendation only; Tokenomics never dispatches or switches a model."""

    planner: str
    task_class: str
    complexity: str
    recommended_executor: str | None
    estimated_continue_cost: float
    estimated_handoff_cost: float | None
    estimated_net_savings: float
    handoff_overhead_tokens: int
    required_reviews: tuple[str, ...]
    rationale: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def profiles_from_data(data: Mapping[str, object]) -> list[ModelProfile]:
    """Parse the intentionally small, caller-supplied model-profile format."""
    raw_profiles = data.get("models")
    if not isinstance(raw_profiles, list):
        raise ValueError("model profile data must contain a models list")
    profiles: list[ModelProfile] = []
    for raw in raw_profiles:
        if not isinstance(raw, dict):
            raise ValueError("each model profile must be an object")
        capabilities = raw.get("capabilities")
        if not isinstance(capabilities, list) or not all(isinstance(item, str) for item in capabilities):
            raise ValueError("model profile capabilities must be a list of strings")
        try:
            profiles.append(
                ModelProfile(
                    name=str(raw["name"]),
                    provider=str(raw["provider"]),
                    input_per_million=float(raw["input_per_million"]),
                    output_per_million=float(raw["output_per_million"]),
                    capabilities=frozenset(capabilities),
                    max_complexity=str(raw["max_complexity"]),
                )
            )
        except KeyError as exc:
            raise ValueError(f"model profile is missing {exc.args[0]}") from exc
    return profiles


def review_gates(task_class: str, complexity: str) -> tuple[str, ...]:
    """Return the minimum review lenses justified by the task's declared risk."""
    if not task_class.strip():
        raise ValueError("task_class is required")
    if complexity not in _COMPLEXITY:
        raise ValueError("complexity must be low, medium, or high")

    gates: list[str] = ["QA"]
    if complexity in {"medium", "high"}:
        gates.append("Senior Software Engineer")
    if complexity == "high":
        gates.append("Architect")
    if task_class == "docs":
        gates.append("Technical Writer")
    if task_class == "deployment":
        gates.append("DevOps")
    if task_class == "security":
        gates.append("Security Specialist")
    return tuple(gates)


def recommend_handoff(
    *,
    planner: ModelProfile,
    candidates: Iterable[ModelProfile],
    task_class: str,
    complexity: str,
    input_tokens: int,
    output_tokens: int,
    handoff_overhead_tokens: int = 0,
    minimum_net_savings: float = 0.0,
) -> PlanningRecommendation:
    """Recommend the lowest-cost capable executor after handoff overhead.

    A profile is eligible only when its declared task capability and complexity
    ceiling satisfy the request. Pricing and capabilities are caller supplied;
    Tokenomics does not contact a provider or infer model quality.
    """
    if complexity not in _COMPLEXITY:
        raise ValueError("complexity must be low, medium, or high")
    if input_tokens < 0 or output_tokens < 0 or handoff_overhead_tokens < 0:
        raise ValueError("token counts must be non-negative")
    if not isfinite(minimum_net_savings) or minimum_net_savings < 0:
        raise ValueError("minimum_net_savings must be a finite non-negative number")
    if not planner.supports(task_class, complexity):
        raise ValueError("planner profile does not support the declared task")

    continue_cost = planner.estimate_cost(input_tokens, output_tokens)
    eligible = [candidate for candidate in candidates if candidate.supports(task_class, complexity)]
    options = [
        (candidate.estimate_cost(input_tokens + handoff_overhead_tokens, output_tokens), candidate)
        for candidate in eligible
    ]
    cheaper = [
        (cost, candidate)
        for cost, candidate in options
        if cost < continue_cost and continue_cost - cost >= minimum_net_savings
    ]
    gates = review_gates(task_class, complexity)
    if not cheaper:
        return PlanningRecommendation(
            planner=planner.name,
            task_class=task_class,
            complexity=complexity,
            recommended_executor=None,
            estimated_continue_cost=continue_cost,
            estimated_handoff_cost=None,
            estimated_net_savings=0.0,
            handoff_overhead_tokens=handoff_overhead_tokens,
            required_reviews=gates,
            rationale=(
                "No declared-capable candidate is cheaper after handoff overhead; "
                "keep the work with the planning model."
            ),
        )
    handoff_cost, executor = min(cheaper, key=lambda option: option[0])
    return PlanningRecommendation(
        planner=planner.name,
        task_class=task_class,
        complexity=complexity,
        recommended_executor=executor.name,
        estimated_continue_cost=continue_cost,
        estimated_handoff_cost=handoff_cost,
        estimated_net_savings=continue_cost - handoff_cost,
        handoff_overhead_tokens=handoff_overhead_tokens,
        required_reviews=gates,
        rationale=(
            "A lower-cost declared-capable executor is available after including the handoff "
            "context overhead. This is a recommendation, not an automatic handoff."
        ),
    )
