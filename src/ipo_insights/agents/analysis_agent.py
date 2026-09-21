"""Agent responsible for turning research into investment signals."""

from __future__ import annotations

import logging
from typing import Tuple

from ipo_insights.agents.base_agent import BaseAgent
from ipo_insights.analytics.financial_metrics import build_financial_summary
from ipo_insights.analytics.risk_assessment import assess_risk
from ipo_insights.models import IPOInsight, ResearchData

logger = logging.getLogger(__name__)


class AnalysisAgent(BaseAgent):
    """Analyzes research data and generates IPO investment signals with confidence metrics.
    
    This agent transforms market research and financial data into actionable investment
    insights, including recommendation scores, valuation signals, and risk assessments.
    """

    def __init__(self):
        super().__init__(name="analysis_agent")
        logger.info("AnalysisAgent initialized")

    def _validate_research_data(self, research_data: ResearchData) -> None:
        """Validate required fields in research data.
        
        Args:
            research_data: The research data to validate
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        if not research_data.company_name or not research_data.ticker:
            raise ValueError("company_name and ticker are required")
        if research_data.market_size <= 0:
            raise ValueError(f"market_size must be positive, got {research_data.market_size}")
        if not (0 <= research_data.growth_rate <= 2):
            logger.warning(f"growth_rate {research_data.growth_rate} is outside typical range [0, 2]")

    def _calculate_dynamic_metrics(self, research_data: ResearchData, filing_summary: dict | None = None) -> dict:
        """Calculate financial metrics dynamically based on research data.
        
        Args:
            research_data: Market research data
            filing_summary: Optional filing-derived financial data
            
        Returns:
            Dictionary of calculated financial metrics
        """
        filing_summary = filing_summary or {}
        
        # Base metrics derived from research data
        base_revenue = research_data.market_size * 0.15  # Typical market capture
        metrics = {
            "revenue": filing_summary.get("revenue", base_revenue),
            "ebitda_margin": filing_summary.get("ebitda_margin", 0.18 + research_data.growth_rate * 0.05),
            "growth_rate": research_data.growth_rate,
            "market_cap": research_data.market_size * 0.6,
        }
        
        return metrics

    def _calculate_recommendation_score(
        self, growth_rate: float, risk_level: str, competitive_position: str
    ) -> int:
        """Calculate recommendation score based on multiple factors.
        
        Args:
            growth_rate: Projected growth rate (decimal)
            risk_level: Risk assessment level (Low/Medium/High)
            competitive_position: Description of competitive positioning
            
        Returns:
            Recommendation score from 1-10
        """
        score = 7  # Base score
        
        # Growth rate component
        if growth_rate >= 0.4:
            score += 2
        elif growth_rate >= 0.3:
            score += 1
        elif growth_rate < 0.05:
            score -= 1
            
        # Risk component
        if risk_level == "High":
            score -= 2
        elif risk_level == "Low":
            score += 1
        elif risk_level == "Medium":
            score += 0  # Neutral
            
        # Competitive positioning bonus
        position_lower = competitive_position.lower()
        if "leader" in position_lower or "dominant" in position_lower:
            score += 1
        elif "challenged" in position_lower or "weak" in position_lower:
            score -= 1
            
        return max(1, min(10, score))

    def _determine_valuation_signal(self, score: int) -> Tuple[str, str]:
        """Determine valuation signal and confidence based on score.
        
        Args:
            score: Recommendation score (1-10)
            
        Returns:
            Tuple of (valuation_signal, confidence_level)
        """
        if score >= 8:
            return "Bullish", "High"
        elif score >= 6:
            return "Constructive", "Medium"
        else:
            return "Cautious", "Low"

    def _calculate_sentiment_score(self, research_data: ResearchData, risk_level: str) -> tuple[int, str]:
        """Estimate sentiment based on growth, market, and risk posture.

        Returns a normalized sentiment score from -100 to 100 plus label.
        """
        score = 50
        score += min(25, int(research_data.growth_rate * 100))
        score += 10 if "strong" in research_data.competitive_position.lower() else 0
        score -= 10 if "weak" in research_data.competitive_position.lower() else 0
        score -= 15 if risk_level == "High" else 0
        score -= 5 if risk_level == "Moderate" else 0

        score = max(-100, min(100, score))
        if score >= 70:
            label = "Bullish"
        elif score >= 45:
            label = "Positive"
        elif score >= 20:
            label = "Neutral"
        else:
            label = "Cautious"
        return score, label

    def _calculate_fair_value_estimate(self, valuation_range: dict[str, float]) -> float:
        """Estimate fair value from base and scenario ranges."""
        if not valuation_range:
            return 0.0
        values = list(valuation_range.values())
        return round(sum(values) / len(values), 2)

    def _build_risk_heatmap(self, market_size: float, growth_rate: float, competitive_position: str, risk_level: str) -> dict[str, str]:
        """Summarize risk factors as a simple heatmap by category."""
        position_text = competitive_position.lower()
        heatmap = {
            "market_size": "Low" if market_size >= 3_500_000_000 else "Medium",
            "growth_rate": "Low" if growth_rate >= 0.25 else "Medium" if growth_rate >= 0.12 else "High",
            "competition": "Low" if "strong" in position_text or "leader" in position_text else "Medium" if "differentiated" in position_text else "High",
            "execution": "Low" if risk_level == "Low" else "Medium" if risk_level == "Moderate" else "High",
        }
        return heatmap

    def _calculate_valuation_range(self, market_cap: float, growth_rate: float, risk_level: str) -> dict[str, float]:
        """Estimate base, bull, and bear valuation ranges.
        
        Args:
            market_cap: Estimated market capitalization
            growth_rate: Growth rate as decimal
            risk_level: Risk level from risk assessment
            
        Returns:
            Dictionary of valuation scenarios keyed by scenario name
        """
        risk_multiplier = {"Low": 0.95, "Moderate": 1.0, "High": 1.12}.get(risk_level, 1.0)
        growth_adjustment = 1.0 + max(0.0, growth_rate)

        base_case = market_cap * 0.9 * risk_multiplier
        bull_case = market_cap * 1.25 * growth_adjustment * risk_multiplier
        bear_case = market_cap * 0.65 * (1.0 - min(0.35, growth_rate))

        return {
            "base_case": round(base_case, 2),
            "bull_case": round(bull_case, 2),
            "bear_case": round(bear_case, 2),
        }

    def _calculate_price_target_band(self, fair_value_estimate: float, confidence: str) -> dict[str, float]:
        """Build a low/base/high price target range around fair value."""
        confidence_multiplier = {"High": 1.08, "Medium": 1.0, "Low": 0.92}.get(confidence, 1.0)
        base = fair_value_estimate * confidence_multiplier
        return {
            "low": round(base * 0.9, 2),
            "base": round(base, 2),
            "high": round(base * 1.15, 2),
        }

    def _build_competitor_benchmark(self, market_cap: float, revenue: float) -> list[dict[str, object]]:
        """Create a simple peer benchmarking set based on estimated company scale."""
        ev_revenue = market_cap / revenue if revenue else 0.0
        peers = [
            {"name": "Peer A", "ev_revenue_multiple": round(ev_revenue * 0.95, 2), "growth_profile": "Strong"},
            {"name": "Peer B", "ev_revenue_multiple": round(ev_revenue * 1.05, 2), "growth_profile": "Moderate"},
            {"name": "Peer C", "ev_revenue_multiple": round(ev_revenue * 0.88, 2), "growth_profile": "Stable"},
        ]
        return peers

    def _build_risk_matrix(self, risk_level: str, sentiment_label: str, market_size: float) -> dict[str, str]:
        """Summarize key risks as a simple matrix."""
        return {
            "market_risk": "Low" if market_size >= 3_500_000_000 else "Medium",
            "execution_risk": risk_level,
            "sentiment_risk": "Low" if sentiment_label in {"Bullish", "Positive"} else "Medium" if sentiment_label == "Neutral" else "High",
            "demand_risk": "Low" if risk_level == "Low" else "Medium" if risk_level == "Moderate" else "High",
        }

    def analyze(self, research_data: ResearchData, filing_summary: dict | None = None) -> IPOInsight:
        """Analyze research data and generate investment signals.
        
        Args:
            research_data: Structured market and company research data
            filing_summary: Optional SEC filing derived financial data
            
        Returns:
            IPOInsight object with recommendation and analysis
            
        Raises:
            ValueError: If research_data validation fails
        """
        logger.info(f"Analyzing IPO for {research_data.company_name} ({research_data.ticker})")
        
        # Validate input data
        self._validate_research_data(research_data)
        
        # Calculate dynamic metrics
        metrics = self._calculate_dynamic_metrics(research_data, filing_summary)
        financial_summary = build_financial_summary(metrics)
        risk_info = assess_risk(
            research_data.market_size, 
            research_data.growth_rate, 
            research_data.competitive_position
        )
        
        valuation_range = self._calculate_valuation_range(
            float(metrics.get("market_cap", 0.0)),
            float(research_data.growth_rate),
            str(risk_info["risk_level"]),
        )

        sentiment_score, sentiment_label = self._calculate_sentiment_score(research_data, str(risk_info["risk_level"]))
        fair_value_estimate = self._calculate_fair_value_estimate(valuation_range)
        risk_heatmap = self._build_risk_heatmap(
            float(research_data.market_size),
            float(research_data.growth_rate),
            research_data.competitive_position,
            str(risk_info["risk_level"]),
        )

        # Calculate recommendation score with refined logic
        recommendation_score = self._calculate_recommendation_score(
            research_data.growth_rate,
            risk_info["risk_level"],
            research_data.competitive_position
        )

        # Determine valuation signal
        valuation_signal, confidence = self._determine_valuation_signal(recommendation_score)

        price_target_band = self._calculate_price_target_band(fair_value_estimate, confidence)
        competitor_benchmark = self._build_competitor_benchmark(
            float(metrics.get("market_cap", 0.0)),
            float(metrics.get("revenue", 0.0)),
        )
        risk_matrix = self._build_risk_matrix(
            str(risk_info["risk_level"]),
            sentiment_label,
            float(research_data.market_size),
        )

        scenario_summary = (
            "Scenario view: base case assumes steady execution, bull case benefits from acceleration, "
            "while bear case reflects slower growth and increased execution risk."
        )
        
        # Generate key drivers from research
        key_drivers = [
            f"Large market opportunity in {research_data.industry}.",
            f"Revenue growth trajectory of {research_data.growth_rate * 100:.1f}% supports long-term demand.",
            f"Competitive positioning: {research_data.competitive_position}.",
        ]
        if research_data.notes:
            key_drivers.extend(research_data.notes[:2])  # Add top 2 research notes
            
        comparables = [
            "Peer A: similar growth profile with robust pipeline execution",
            "Peer B: moderate valuation premium amid strong market demand",
            "Peer C: risk-adjusted benchmark for execution quality",
        ]

        thesis = (
            f"{research_data.company_name} benefits from a sizeable addressable market and durable growth trajectory, "
            "with a competitive position that supports a constructive near-term IPO thesis. "
            "The valuation and risk profile should remain under active review as filing details are finalized."
        )
        
        insight = IPOInsight(
            ticker=research_data.ticker,
            company_name=research_data.company_name,
            filing_url=research_data.filing_url,
            market_summary=f"{research_data.industry} market with a {research_data.growth_rate * 100:.1f}% growth outlook; competitive positioning: {research_data.competitive_position}",
            financial_summary=financial_summary,
            recommendation_score=recommendation_score,
            risk_level=risk_info["risk_level"],
            thesis=thesis,
            valuation_signal=valuation_signal,
            confidence=confidence,
            key_drivers=key_drivers,
            valuation_range=valuation_range,
            fair_value_estimate=fair_value_estimate,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            risk_heatmap=risk_heatmap,
            price_target_band=price_target_band,
            competitor_benchmark=competitor_benchmark,
            risk_matrix=risk_matrix,
            scenario_summary=scenario_summary,
            comparables=comparables,
        )
        
        logger.info(f"Analysis complete: {research_data.company_name} - Score: {recommendation_score}, Signal: {valuation_signal}")
        return insight

    def run(self, research_data: ResearchData, filing_summary: dict | None = None) -> IPOInsight:
        """Execute the analysis agent on research data.
        
        Args:
            research_data: Market and company research data
            filing_summary: Optional SEC filing derived data
            
        Returns:
            IPOInsight with full analysis and recommendations
        """
        return self.analyze(research_data, filing_summary)
