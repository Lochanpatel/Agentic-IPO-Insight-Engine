"""Market data and research aggregation utilities."""

from __future__ import annotations

from typing import Dict, List


def fetch_market_snapshot(company_name: str, ticker: str) -> Dict[str, object]:
    """Return a representative, deterministic market snapshot for a company.

    In a production implementation this would call external APIs or data providers.
    """

    normalized_name = company_name.strip() or "Example IPO"
    base_market_size = 4800000000 if ticker.upper() != "EXMP" else 3200000000
    return {
        "company_name": normalized_name,
        "ticker": ticker.upper(),
        "industry": "Enterprise Software",
        "market_size": base_market_size,
        "growth_rate": 0.31,
        "competitive_position": "Strong product differentiation with expanding customer base",
        "notes": [
            f"{normalized_name} operates in a rapidly growing digital infrastructure market.",
            "Customer concentration remains manageable and operating leverage is improving.",
            "The sector continues to attract institutional capital and strategic interest.",
        ],
    }


def summarize_market_snapshot(snapshot: Dict[str, object]) -> str:
    notes: List[str] = snapshot.get("notes", [])
    return " | ".join(notes[:2])
