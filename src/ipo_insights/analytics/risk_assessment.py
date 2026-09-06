"""Risk assessment utilities for IPO scenarios."""

from __future__ import annotations

import logging
from typing import Dict

logger = logging.getLogger(__name__)


def assess_risk(market_size: float, growth_rate: float, competitive_position: str) -> Dict[str, object]:
    """Create a comprehensive risk assessment for IPO scenarios.
    
    Evaluates multiple risk factors including market size, growth trajectory,
    and competitive positioning to produce a risk score and level classification.
    
    Args:
        market_size: Total addressable market in dollars
        growth_rate: Expected growth rate as decimal (e.g., 0.25 for 25%)
        competitive_position: Description of company's competitive standing
        
    Returns:
        Dictionary with risk score (1-10) and risk level (Low/Moderate/High)
        
    Raises:
        ValueError: If inputs are invalid
    """
    # Validate inputs
    if market_size < 0 or growth_rate < 0:
        raise ValueError("market_size and growth_rate must be non-negative")
    if not competitive_position or not isinstance(competitive_position, str):
        raise ValueError("competitive_position must be a non-empty string")
    
    score = 3  # Base risk score
    
    # Market size risk component
    if market_size < 1_000_000_000:
        score += 2
        logger.debug("Market size below $1B - increased risk")
    elif market_size < 3_500_000_000:
        score += 1
        logger.debug("Market size in moderate range ($1-3.5B)")
    else:
        logger.debug(f"Large market size ${market_size:,.0f} - lower risk")
    
    # Growth rate risk component
    if growth_rate < 0.05:
        score += 2
        logger.debug("Low growth rate - increased risk")
    elif growth_rate < 0.2:
        score += 1
        logger.debug("Moderate growth rate")
    elif growth_rate > 1.0:
        logger.warning(f"Unusually high growth rate: {growth_rate*100:.1f}%")
    else:
        logger.debug(f"Healthy growth rate: {growth_rate*100:.1f}%")
    
    # Competitive positioning risk component
    position_lower = competitive_position.lower()
    if "weak" in position_lower or "challenged" in position_lower:
        score += 2
        logger.debug("Weak competitive position - increased risk")
    elif "strong" in position_lower or "leader" in position_lower or "dominant" in position_lower:
        score -= 1
        logger.debug("Strong competitive position - reduced risk")
    else:
        logger.debug("Neutral competitive position")
    
    # Normalize score
    score = max(1, min(10, score))
    
    # Classify risk level
    if score >= 8:
        risk_level = "High"
    elif score >= 5:
        risk_level = "Moderate"
    else:
        risk_level = "Low"
    
    result = {"score": score, "risk_level": risk_level}
    logger.info(f"Risk assessment: Score {score}/10, Level: {risk_level}")
    return result


def assess_market_concentration_risk(market_size: float, customer_notes: list | None = None) -> float:
    """Assess customer concentration risk for the market.
    
    Args:
        market_size: Total addressable market in dollars
        customer_notes: Optional list of customer-related notes
        
    Returns:
        Concentration risk score (0-1, where 1 is highest risk)
    """
    customer_notes = customer_notes or []
    
    # Base concentration risk from market size
    if market_size < 1_000_000_000:
        concentration_risk = 0.7
    elif market_size < 5_000_000_000:
        concentration_risk = 0.5
    else:
        concentration_risk = 0.3
    
    # Adjust based on customer notes
    notes_str = " ".join(customer_notes).lower()
    if "concentration" in notes_str or "few customers" in notes_str:
        concentration_risk = min(1.0, concentration_risk + 0.2)
    elif "diversified" in notes_str or "many customers" in notes_str:
        concentration_risk = max(0.0, concentration_risk - 0.2)
    
    logger.debug(f"Concentration risk: {concentration_risk:.2f}")
    return concentration_risk


def calculate_overall_risk_score(
    market_risk: float, growth_risk: float, competitive_risk: float, concentration_risk: float
) -> Dict[str, object]:
    """Calculate overall risk score from multiple risk dimensions.
    
    Args:
        market_risk: Market-related risk score (0-1)
        growth_risk: Growth trajectory risk score (0-1)
        competitive_risk: Competitive positioning risk score (0-1)
        concentration_risk: Customer concentration risk score (0-1)
        
    Returns:
        Dictionary with weighted overall risk assessment
    """
    # Weighted average of risk dimensions
    weights = {"market": 0.3, "growth": 0.25, "competitive": 0.25, "concentration": 0.2}
    
    overall_score = (
        market_risk * weights["market"]
        + growth_risk * weights["growth"]
        + competitive_risk * weights["competitive"]
        + concentration_risk * weights["concentration"]
    )
    
    # Convert to 1-10 scale
    overall_score_10 = int(overall_score * 10)
    overall_score_10 = max(1, min(10, overall_score_10))
    
    return {
        "overall_score": overall_score_10,
        "component_scores": {
            "market": market_risk,
            "growth": growth_risk,
            "competitive": competitive_risk,
            "concentration": concentration_risk,
        },
    }
