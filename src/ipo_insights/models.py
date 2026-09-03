"""Data models for IPO insights."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ResearchData:
    """Structured market and company research data."""

    company_name: str
    ticker: str
    industry: str
    market_size: float
    growth_rate: float
    competitive_position: str
    filing_url: str = ""
    notes: List[str] = field(default_factory=list)


@dataclass
class IPOInsight:
    """Output object representing an IPO analysis insight."""

    ticker: str
    company_name: str
    filing_url: str
    market_summary: str
    financial_summary: str
    recommendation_score: int
    risk_level: str
    thesis: str
    valuation_signal: str = "Neutral"
    confidence: str = "Medium"
    key_drivers: List[str] = field(default_factory=list)
    comparables: List[str] = field(default_factory=list)

    def generate_report(self) -> str:
        lines = [
            f"IPO Insight for {self.company_name} ({self.ticker})",
            "=" * 60,
            f"Filing URL: {self.filing_url}",
            "",
            "Market Summary:",
            self.market_summary,
            "",
            "Financial Summary:",
            self.financial_summary,
            "",
            f"Recommendation Score: {self.recommendation_score}/10",
            f"Risk Level: {self.risk_level}",
            f"Valuation Signal: {self.valuation_signal}",
            f"Confidence: {self.confidence}",
            "",
            "Key Drivers:",
        ]

        if self.key_drivers:
            lines.extend(f"- {driver}" for driver in self.key_drivers)
        else:
            lines.append("- No additional drivers captured.")

        lines.extend(["", "Comparable Context:"])

        if self.comparables:
            lines.extend(f"- {company}" for company in self.comparables)
        else:
            lines.append("- No comparable benchmark data available.")

        lines.extend(["", "Investment Thesis:", self.thesis])
        return "\n".join(lines)


@dataclass
class FinancialMetrics:
    revenue: float
    ebitda_margin: float
    net_margin: float
    growth_rate: float
    market_cap: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "revenue": self.revenue,
            "ebitda_margin": self.ebitda_margin,
            "net_margin": self.net_margin,
            "growth_rate": self.growth_rate,
            "market_cap": self.market_cap,
        }
