"""Risk assessment utilities for IPO scenarios."""

from __future__ import annotations

from typing import Dict


def assess_risk(market_size: float, growth_rate: float, competitive_position: str) -> Dict[str, object]:
    """Create a simple risk model used by the engine."""

    score = 3
    if market_size < 3_500_000_000:
        score += 1
    if growth_rate < 0.2:
        score += 1
    if "weak" in competitive_position.lower():
        score += 2
    elif "strong" in competitive_position.lower():
        score -= 1

    score = max(1, min(10, score))
    if score >= 8:
        risk_level = "High"
    elif score >= 5:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    return {"score": score, "risk_level": risk_level}
