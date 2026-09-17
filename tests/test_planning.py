import pytest

from tokenomics.planning import ModelProfile, profiles_from_data, recommend_handoff, review_gates


def profile(name: str, input_price: float, output_price: float, *, complexity: str = "high") -> ModelProfile:
    return ModelProfile(
        name=name,
        provider="test",
        input_per_million=input_price,
        output_per_million=output_price,
        capabilities=frozenset({"implementation", "tests", "docs"}),
        max_complexity=complexity,
    )


def test_recommends_cheaper_declared_capable_executor_after_handoff_cost():
    recommendation = recommend_handoff(
        planner=profile("expensive", 15, 75),
        candidates=[profile("expensive", 15, 75), profile("efficient", 3, 15, complexity="medium")],
        task_class="implementation",
        complexity="medium",
        input_tokens=12_000,
        output_tokens=2_000,
        handoff_overhead_tokens=1_000,
    )
    assert recommendation.recommended_executor == "efficient"
    assert recommendation.estimated_net_savings > 0
    assert recommendation.required_reviews == ("QA", "Senior Software Engineer")
    assert "not an automatic handoff" in recommendation.rationale


def test_keeps_planner_when_candidate_is_not_declared_capable():
    recommendation = recommend_handoff(
        planner=profile("planner", 15, 75),
        candidates=[profile("cheap", 1, 1, complexity="low")],
        task_class="implementation",
        complexity="high",
        input_tokens=12_000,
        output_tokens=2_000,
    )
    assert recommendation.recommended_executor is None
    assert recommendation.estimated_net_savings == 0


def test_review_gates_are_risk_based():
    assert review_gates("docs", "low") == ("QA", "Technical Writer")
    assert review_gates("deployment", "high") == ("QA", "Senior Software Engineer", "Architect", "DevOps")
    assert review_gates("security", "medium") == ("QA", "Senior Software Engineer", "Security Specialist")


def test_profile_parser_rejects_invalid_data():
    with pytest.raises(ValueError, match="models list"):
        profiles_from_data({})
