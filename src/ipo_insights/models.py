"""Data models for IPO insights."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ResearchData:
    """Structured market and company research data.
    
    Contains core market research, company fundamentals, and competitive
    analysis used as input to the analysis agent.
    
    Attributes:
        company_name: Name of the company
        ticker: Stock ticker symbol
        industry: Target industry/sector
        market_size: Total addressable market (TAM) in dollars
        growth_rate: Expected growth rate as decimal (0-1+)
        competitive_position: Description of competitive standing
        filing_url: Optional URL to SEC filing document
        notes: Optional list of research notes or insights
    """

    company_name: str
    ticker: str
    industry: str
    market_size: float
    growth_rate: float
    competitive_position: str
    filing_url: str = ""
    notes: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate research data after initialization."""
        if not self.company_name or not self.ticker:
            logger.warning("Missing company_name or ticker in ResearchData")
        if self.market_size < 0:
            logger.warning(f"Negative market_size in ResearchData: {self.market_size}")
        if not (0 <= self.growth_rate <= 2):
            logger.warning(f"Unusual growth_rate in ResearchData: {self.growth_rate}")

    def get_summary(self) -> str:
        """Get a summary string of the research data.
        
        Returns:
            One-line summary of research data
        """
        return (
            f"{self.company_name} ({self.ticker}) in {self.industry}: "
            f"${self.market_size:,.0f} TAM, {self.growth_rate*100:.1f}% growth"
        )

    def to_dict(self) -> Dict[str, object]:
        """Convert research data to dictionary.
        
        Returns:
            Dictionary representation of research data
        """
        return {
            "company_name": self.company_name,
            "ticker": self.ticker,
            "industry": self.industry,
            "market_size": self.market_size,
            "growth_rate": self.growth_rate,
            "competitive_position": self.competitive_position,
            "filing_url": self.filing_url,
            "notes": self.notes,
        }


@dataclass
class IPOInsight:
    """Output object representing a complete IPO analysis insight.
    
    Contains all analysis results including recommendation scores, risk assessment,
    financial summaries, and investment thesis.
    
    Attributes:
        ticker: Stock ticker symbol
        company_name: Company name
        filing_url: Optional URL to SEC filing
        market_summary: Summary of market opportunity
        financial_summary: Summary of financial metrics
        recommendation_score: Investment recommendation (1-10)
        risk_level: Risk assessment (Low/Moderate/High)
        thesis: Investment thesis statement
        valuation_signal: Valuation signal (Bullish/Constructive/Cautious)
        confidence: Confidence level (Low/Medium/High)
        key_drivers: List of key investment drivers
        comparables: List of comparable company benchmarks
    """

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
    valuation_range: Dict[str, float] = field(default_factory=dict)
    fair_value_estimate: float = 0.0
    sentiment_score: int = 50
    sentiment_label: str = "Neutral"
    risk_heatmap: Dict[str, str] = field(default_factory=dict)
    price_target_band: Dict[str, float] = field(default_factory=dict)
    competitor_benchmark: List[Dict[str, object]] = field(default_factory=list)
    risk_matrix: Dict[str, str] = field(default_factory=dict)
    scenario_summary: str = ""
    comparables: List[str] = field(default_factory=list)
    market_catalysts: List[str] = field(default_factory=list)
    key_risks: List[str] = field(default_factory=list)
    investment_grade: str = "Neutral"

    def __post_init__(self) -> None:
        """Validate IPOInsight after initialization."""
        if not (1 <= self.recommendation_score <= 10):
            logger.warning(f"Invalid recommendation_score: {self.recommendation_score}")
        if self.risk_level not in ("Low", "Moderate", "High"):
            logger.warning(f"Invalid risk_level: {self.risk_level}")
        if self.valuation_signal not in ("Bullish", "Constructive", "Cautious", "Neutral"):
            logger.warning(f"Invalid valuation_signal: {self.valuation_signal}")
        if self.confidence not in ("Low", "Medium", "High"):
            logger.warning(f"Invalid confidence: {self.confidence}")
        if self.investment_grade not in ("Buy", "Accumulate", "Watchlist", "Speculative", "Neutral"):
            logger.warning(f"Invalid investment_grade: {self.investment_grade}")

    def is_bullish(self) -> bool:
        """Check if insight indicates bullish outlook.
        
        Returns:
            True if recommendation is bullish
        """
        return self.valuation_signal == "Bullish" and self.recommendation_score >= 8

    def is_cautious(self) -> bool:
        """Check if insight indicates cautious outlook.
        
        Returns:
            True if recommendation is cautious
        """
        return self.valuation_signal == "Cautious" and self.recommendation_score < 6

    def get_risk_indicator(self) -> str:
        """Get emoji/text risk indicator.
        
        Returns:
            Risk indicator string
        """
        if self.risk_level == "High":
            return "🔴 HIGH RISK"
        elif self.risk_level == "Moderate":
            return "🟡 MODERATE RISK"
        else:
            return "🟢 LOW RISK"

    def generate_report(self) -> str:
        """Generate full text report from IPO insight.
        
        Returns:
            Formatted multi-line report
        """
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
        ]

        if self.valuation_range:
            lines.extend(["Scenario Analysis:"])
            for label, value in self.valuation_range.items():
                lines.append(f"- {label.replace('_', ' ').title()}: ${value:,.0f}")
            lines.append(f"Fair Value Estimate: ${self.fair_value_estimate:,.0f}")
            lines.append(f"Sentiment: {self.sentiment_label} ({self.sentiment_score})")
            if self.scenario_summary:
                lines.append(self.scenario_summary)
            lines.append("")

        if self.price_target_band:
            lines.extend(["Price Target Band:"])
            for label, value in self.price_target_band.items():
                lines.append(f"- {label.replace('_', ' ').title()}: ${value:,.0f}")
            lines.append("")

        if self.risk_heatmap:
            lines.extend(["Risk Heatmap:"])
            for label, level in self.risk_heatmap.items():
                lines.append(f"- {label.replace('_', ' ').title()}: {level}")
            lines.append("")

        if self.competitor_benchmark:
            lines.extend(["Competitor Benchmarking:"])
            for comp in self.competitor_benchmark:
                name = comp.get("name", "Competitor")
                multiple = comp.get("ev_revenue_multiple", 0.0)
                lines.append(f"- {name}: EV/Revenue {multiple:.2f}x")
            lines.append("")

        if self.risk_matrix:
            lines.extend(["Risk Matrix:"])
            for label, level in self.risk_matrix.items():
                lines.append(f"- {label.replace('_', ' ').title()}: {level}")
            lines.append("")

        lines.extend([
            f"Recommendation Score: {self.recommendation_score}/10",
            f"Risk Level: {self.risk_level}",
            f"Valuation Signal: {self.valuation_signal}",
            f"Confidence: {self.confidence}",
            "",
            "Key Drivers:",
        ])

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

        lines.append("\nMarket Catalysts:")
        if self.market_catalysts:
            lines.extend(f"- {catalyst}" for catalyst in self.market_catalysts)
        else:
            lines.append("- No specific market catalysts identified.")

        lines.append("\nKey Risks:")
        if self.key_risks:
            lines.extend(f"- {risk}" for risk in self.key_risks)
        else:
            lines.append("- No key risks identified.")

        lines.append(f"\nInvestment Grade: {self.investment_grade}")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, object]:
        """Convert IPO insight to dictionary.
        
        Returns:
            Dictionary representation of insight
        """
        return {
            "ticker": self.ticker,
            "company_name": self.company_name,
            "filing_url": self.filing_url,
            "market_summary": self.market_summary,
            "financial_summary": self.financial_summary,
            "recommendation_score": self.recommendation_score,
            "risk_level": self.risk_level,
            "thesis": self.thesis,
            "valuation_signal": self.valuation_signal,
            "confidence": self.confidence,
            "key_drivers": self.key_drivers,
            "valuation_range": self.valuation_range,
            "fair_value_estimate": self.fair_value_estimate,
            "sentiment_score": self.sentiment_score,
            "sentiment_label": self.sentiment_label,
            "risk_heatmap": self.risk_heatmap,
            "price_target_band": self.price_target_band,
            "competitor_benchmark": self.competitor_benchmark,
            "risk_matrix": self.risk_matrix,
            "scenario_summary": self.scenario_summary,
            "comparables": self.comparables,
            "market_catalysts": self.market_catalysts,
            "key_risks": self.key_risks,
            "investment_grade": self.investment_grade,
        }


@dataclass
class FinancialMetrics:
    """Financial metrics for IPO company analysis.
    
    Attributes:
        revenue: Annual revenue in dollars
        ebitda_margin: EBITDA as percentage of revenue (0-1)
        net_margin: Net profit margin (0-1)
        growth_rate: Expected growth rate (0-1+)
        market_cap: Market capitalization in dollars
    """

    revenue: float
    ebitda_margin: float
    net_margin: float
    growth_rate: float = 0.0
    market_cap: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        """Convert metrics to dictionary.
        
        Returns:
            Dictionary of financial metrics
        """
        return {
            "revenue": self.revenue,
            "ebitda_margin": self.ebitda_margin,
            "net_margin": self.net_margin,
            "growth_rate": self.growth_rate,
            "market_cap": self.market_cap,
        }

    def get_ev_revenue_multiple(self) -> float:
        """Calculate EV/Revenue multiple.
        
        Returns:
            EV/Revenue multiple, or 0 if revenue is 0
        """
        if self.revenue <= 0:
            logger.warning("Cannot calculate EV/Revenue with zero revenue")
            return 0.0
        return self.market_cap / self.revenue

    def get_pe_implied(self) -> float:
        """Calculate implied P/E multiple (simplified).
        
        Returns:
            Implied P/E multiple based on margins and EV/Revenue
        """
        net_income = self.revenue * self.net_margin
        if net_income <= 0:
            logger.warning("Cannot calculate P/E with non-positive net income")
            return 0.0
        return self.market_cap / net_income
