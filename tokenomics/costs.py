"""Provider-neutral cost calculations.

Prices are supplied by the caller so Tokenomics never assumes a current provider
price or contacts a provider to determine cost.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TokenPricing:
    """Price per one million tokens for each usage category."""

    input_per_million: float
    output_per_million: float
    cache_read_per_million: float = 0.0
    cache_write_per_million: float = 0.0


@dataclass(frozen=True, slots=True)
class TokenCost:
    """Calculated cost for one usage event."""

    input_cost: float
    output_cost: float
    cache_read_cost: float
    cache_write_cost: float

    @property
    def total(self) -> float:
        return self.input_cost + self.output_cost + self.cache_read_cost + self.cache_write_cost


def calculate_cost(
    *,
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int = 0,
    cache_write_tokens: int = 0,
    pricing: TokenPricing,
) -> TokenCost:
    """Calculate cost from caller-supplied prices."""
    values = (input_tokens, output_tokens, cache_read_tokens, cache_write_tokens)
    if any(value < 0 for value in values):
        raise ValueError("token counts must be non-negative")

    million = 1_000_000
    return TokenCost(
        input_cost=input_tokens / million * pricing.input_per_million,
        output_cost=output_tokens / million * pricing.output_per_million,
        cache_read_cost=cache_read_tokens / million * pricing.cache_read_per_million,
        cache_write_cost=cache_write_tokens / million * pricing.cache_write_per_million,
    )
