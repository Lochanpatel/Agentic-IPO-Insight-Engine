"""Financial metrics calculations for IPO analysis."""

from __future__ import annotations

import logging
from typing import Dict

from ipo_insights.models import FinancialMetrics

logger = logging.getLogger(__name__)


def compute_financial_metrics(
    revenue: float, ebitda_margin: float, growth_rate: float, market_cap: float
) -> FinancialMetrics:
    """Compute comprehensive financial metrics from base inputs.
    
    Args:
        revenue: Annual revenue in dollars
        ebitda_margin: EBITDA as percentage of revenue (0-1)
        growth_rate: Expected growth rate (0-1)
        market_cap: Market capitalization in dollars
        
    Returns:
        FinancialMetrics object with computed values
        
    Raises:
        ValueError: If inputs are invalid
    """
    if revenue < 0 or ebitda_margin < 0 or market_cap < 0:
        raise ValueError("Financial metrics must be non-negative")
    if not (0 <= ebitda_margin <= 1):
        logger.warning(f"EBITDA margin {ebitda_margin} outside typical range [0, 1]")
    
    # Derive net margin conservatively from EBITDA margin
    net_margin = max(0.04, ebitda_margin - 0.06)
    
    metrics = FinancialMetrics(
        revenue=revenue,
        ebitda_margin=ebitda_margin,
        net_margin=net_margin,
        growth_rate=growth_rate,
        market_cap=market_cap,
    )
    
    logger.debug(f"Computed metrics: Revenue ${revenue:,.0f}, Net Margin {net_margin*100:.1f}%")
    return metrics


def summarize_financial_metrics(metrics: FinancialMetrics) -> str:
    """Generate human-readable summary of financial metrics.
    
    Args:
        metrics: FinancialMetrics object
        
    Returns:
        Formatted string summary
    """
    summary = (
        f"Revenue: ${metrics.revenue:,.0f} | EBITDA Margin: {metrics.ebitda_margin * 100:.1f}% | "
        f"Net Margin: {metrics.net_margin * 100:.1f}% | Growth Rate: {metrics.growth_rate * 100:.1f}%"
    )
    return summary


def calculate_valuation_multiples(revenue: float, market_cap: float) -> Dict[str, float]:
    """Calculate key valuation multiples.
    
    Args:
        revenue: Annual revenue in dollars
        market_cap: Market capitalization in dollars
        
    Returns:
        Dictionary with valuation multiples
    """
    if revenue <= 0:
        logger.warning("Cannot calculate valuation multiples with zero revenue")
        return {"ev_revenue": 0.0, "pe_implied": 0.0}
    
    ev_revenue = market_cap / revenue
    
    return {
        "ev_revenue": ev_revenue,
        "pe_implied": ev_revenue * 1.2,  # Simplified P/E estimation
    }


def build_financial_summary(raw_metrics: Dict[str, object]) -> str:
    """Build comprehensive financial summary from raw metric dictionary.
    
    Args:
        raw_metrics: Dictionary with raw metric values
        
    Returns:
        Formatted financial summary string
    """
    try:
        revenue = float(raw_metrics.get("revenue", 0.0))
        ebitda_margin = float(raw_metrics.get("ebitda_margin", 0.0))
        growth_rate = float(raw_metrics.get("growth_rate", 0.0))
        market_cap = float(raw_metrics.get("market_cap", revenue * 4.0))
        
        metrics = compute_financial_metrics(revenue, ebitda_margin, growth_rate, market_cap)
        summary = summarize_financial_metrics(metrics)
        
        logger.info(f"Financial summary built for company with ${revenue:,.0f} revenue")
        return summary
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to build financial summary: {e}")
        raise
