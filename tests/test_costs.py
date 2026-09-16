import pytest

from tokenomics.costs import TokenPricing, calculate_cost


def test_cost_calculation():
    cost = calculate_cost(
        input_tokens=1_000_000,
        output_tokens=500_000,
        pricing=TokenPricing(input_per_million=3.0, output_per_million=15.0),
    )
    assert cost.input_cost == pytest.approx(3.0)
    assert cost.output_cost == pytest.approx(7.5)
    assert cost.total == pytest.approx(10.5)


def test_negative_tokens_are_rejected():
    with pytest.raises(ValueError):
        calculate_cost(
            input_tokens=-1,
            output_tokens=0,
            pricing=TokenPricing(input_per_million=1.0, output_per_million=1.0),
        )
