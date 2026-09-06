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
        
        # Calculate recommendation score with refined logic
        recommendation_score = self._calculate_recommendation_score(
            research_data.growth_rate,
            risk_info["risk_level"],
            research_data.competitive_position
        )
        
        # Determine valuation signal
        valuation_signal, confidence = self._determine_valuation_signal(recommendation_score)
        
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
