"""Agent responsible for turning research into investment signals."""

from __future__ import annotations

from ipo_insights.agents.base_agent import BaseAgent
from ipo_insights.analytics.financial_metrics import build_financial_summary
from ipo_insights.analytics.risk_assessment import assess_risk
from ipo_insights.models import IPOInsight, ResearchData


class AnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="analysis_agent")

    def analyze(self, research_data: ResearchData, filing_summary: dict | None = None) -> IPOInsight:
        filing_summary = filing_summary or {}
        metrics = {
            "revenue": 220_000_000,
            "ebitda_margin": 0.20,
            "growth_rate": research_data.growth_rate,
            "market_cap": research_data.market_size * 0.6,
        }
        metrics.update(filing_summary)
        financial_summary = build_financial_summary(metrics)
        risk_info = assess_risk(research_data.market_size, research_data.growth_rate, research_data.competitive_position)

        recommendation_score = 7
        if research_data.growth_rate >= 0.3:
            recommendation_score += 1
        if risk_info["risk_level"] == "High":
            recommendation_score -= 2
        elif risk_info["risk_level"] == "Low":
            recommendation_score += 1
        recommendation_score = max(1, min(10, recommendation_score))

        thesis = (
            f"{research_data.company_name} benefits from a sizeable addressable market and durable growth trajectory, "
            "with a competitive position that supports a constructive near-term IPO thesis. "
            "The valuation and risk profile should remain under active review as filing details are finalized."
        )
        return IPOInsight(
            ticker=research_data.ticker,
            company_name=research_data.company_name,
            filing_url=research_data.filing_url,
            market_summary=f"{research_data.industry} market with a {research_data.growth_rate * 100:.1f}% growth outlook; competitive positioning: {research_data.competitive_position}",
            financial_summary=financial_summary,
            recommendation_score=recommendation_score,
            risk_level=risk_info["risk_level"],
            thesis=thesis,
        )

    def run(self, research_data: ResearchData, filing_summary: dict | None = None):
        return self.analyze(research_data, filing_summary)
