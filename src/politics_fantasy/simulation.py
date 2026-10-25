"""Toy fantasy-market simulation for auditing game mechanics, not political behaviour.

Agents are intentionally naive and no effect from this generator is empirical.
"""
from __future__ import annotations
import random
from statistics import mean
from dataclasses import dataclass


@dataclass(frozen=True)
class MarketSummary:
    seed: int
    clubs: int
    assets: int
    rounds: int
    mean_value: float
    price_gini: float
    top_20_percent_value_share: float
    note: str = "SYNTHETIC_RULE_DEPENDENT"


def gini(values: list[float]) -> float:
    if any(v < 0 for v in values):
        raise ValueError("Nonnegative values required")
    if not values or sum(values) == 0:
        return 0.0
    ordered = sorted(values)
    n = len(ordered)
    return sum((2 * i - n - 1) * v for i, v in enumerate(ordered, 1)) / (n * sum(ordered))


def simulate_auction(seed: int = 47, clubs: int = 10, assets: int = 100,
                     rounds: int = 12, volatility: float = 0.10,
                     popularity_weight: float = 0.5) -> MarketSummary:
    """No political outcomes are generated; bids depend on invented perceived value."""
    if clubs < 2 or assets < 10 or rounds < 1 or not 0 <= popularity_weight <= 1:
        raise ValueError("Invalid simulation parameters")
    rng = random.Random(seed)
    intrinsic = [rng.uniform(2, 10) for _ in range(assets)]
    popularity = [rng.uniform(2, 10) for _ in range(assets)]
    prices = [3.0 for _ in range(assets)]
    for _ in range(rounds):
        for i in range(assets):
            private_bids = [max(0.01, (1 - popularity_weight) * intrinsic[i]
                                + popularity_weight * popularity[i]
                                + rng.gauss(0, 1.2)) for _ in range(clubs)]
            # Prices update from the highest bid; this assumption creates market pressure.
            prices[i] = max(0.01, prices[i] * (1 - volatility) + volatility * max(private_bids))
    top = sorted(prices, reverse=True)[:max(1, int(assets * .2))]
    return MarketSummary(seed, clubs, assets, rounds, mean(prices), gini(prices),
                         sum(top) / sum(prices))


if __name__ == "__main__":
    demo = simulate_auction()
    print("DATA SYNTHETIC — NOT POLITICAL EMPIRICAL EVIDENCE")
    print(demo)