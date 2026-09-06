"""Market data and research aggregation utilities."""

from __future__ import annotations

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def fetch_market_snapshot(company_name: str, ticker: str) -> Dict[str, object]:
    """Fetch a representative, deterministic market snapshot for a company.
    
    In a production implementation this would call external APIs or data providers
    (Bloomberg, FactSet, industry reports, etc.).
    
    Args:
        company_name: Company name
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with market snapshot data including industry, market size,
        growth rate, competitive position, and research notes
        
    Raises:
        ValueError: If company_name or ticker are invalid
    """
    if not company_name or not ticker:
        raise ValueError("company_name and ticker are required")
    
    normalized_name = company_name.strip() or "Example IPO"
    normalized_ticker = ticker.upper()
    
    logger.info(f"Fetching market snapshot for {normalized_name} ({normalized_ticker})")
    
    # Deterministic market sizing based on ticker
    if normalized_ticker == "EXMP":
        base_market_size = 3_200_000_000
        industry = "Software"
        growth_rate = 0.25
        competitive_position = "Emerging competitor with niche focus"
    else:
        base_market_size = 4_800_000_000
        industry = "Enterprise Software"
        growth_rate = 0.31
        competitive_position = "Strong product differentiation with expanding customer base"
    
    snapshot = {
        "company_name": normalized_name,
        "ticker": normalized_ticker,
        "industry": industry,
        "market_size": base_market_size,
        "growth_rate": growth_rate,
        "competitive_position": competitive_position,
        "notes": [
            f"{normalized_name} operates in a rapidly growing digital infrastructure market.",
            "Customer concentration remains manageable and operating leverage is improving.",
            "The sector continues to attract institutional capital and strategic interest.",
        ],
    }
    
    logger.info(f"Market snapshot created: ${base_market_size:,.0f} TAM, {growth_rate*100:.1f}% growth")
    return snapshot


def summarize_market_snapshot(snapshot: Dict[str, object]) -> str:
    """Generate human-readable summary of market snapshot data.
    
    Args:
        snapshot: Market snapshot dictionary from fetch_market_snapshot
        
    Returns:
        Formatted summary string combining key market insights
    """
    notes: List[str] = snapshot.get("notes", [])
    company_name = snapshot.get("company_name", "Company")
    industry = snapshot.get("industry", "Industry")
    
    logger.debug(f"Summarizing market snapshot for {company_name}")
    
    summary_parts = [
        f"{company_name} operates in {industry}.",
    ]
    summary_parts.extend(notes[:2])  # Include top 2 notes
    
    return " | ".join(summary_parts)


def enrich_market_data(snapshot: Dict[str, object], external_data: Dict[str, object] | None = None) -> Dict[str, object]:
    """Enrich market snapshot with additional external data sources.
    
    Args:
        snapshot: Base market snapshot
        external_data: Optional dictionary with additional market data
        
    Returns:
        Enriched market snapshot with merged data
    """
    external_data = external_data or {}
    
    enriched = snapshot.copy()
    
    # Merge external data, preferring external sources if more recent
    if "analyst_estimates" in external_data:
        enriched["analyst_estimates"] = external_data["analyst_estimates"]
    
    if "comparable_companies" in external_data:
        enriched["comparable_companies"] = external_data["comparable_companies"]
    
    if "recent_market_trends" in external_data:
        enriched["recent_market_trends"] = external_data["recent_market_trends"]
    
    logger.info(f"Market data enriched with {len(external_data)} additional fields")
    return enriched


def calculate_market_metrics(snapshot: Dict[str, object]) -> Dict[str, float]:
    """Calculate derived metrics from market snapshot.
    
    Args:
        snapshot: Market snapshot dictionary
        
    Returns:
        Dictionary with calculated market metrics
    """
    market_size = float(snapshot.get("market_size", 0.0))
    growth_rate = float(snapshot.get("growth_rate", 0.0))
    
    # Calculate market growth absolute value
    annual_market_growth = market_size * growth_rate
    
    # Calculate market maturity index (inverse of growth)
    maturity_index = 1.0 if growth_rate < 0.05 else max(0.0, 1.0 - growth_rate)
    
    metrics = {
        "market_size": market_size,
        "annual_growth": annual_market_growth,
        "cagr": growth_rate,
        "maturity_index": maturity_index,
        "market_attractiveness": growth_rate * (1.0 - maturity_index),
    }
    
    logger.debug(f"Market metrics calculated: ${annual_market_growth:,.0f} annual growth")
    return metrics
