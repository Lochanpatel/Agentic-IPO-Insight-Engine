"""Agent responsible for gathering market and company research."""

from __future__ import annotations

from ipo_insights.agents.base_agent import BaseAgent
from ipo_insights.data.market_data import fetch_market_snapshot, summarize_market_snapshot
from ipo_insights.models import ResearchData


class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="research_agent")

    def gather_market_data(self, company_name: str, ticker: str, filing_url: str = "") -> ResearchData:
        snapshot = fetch_market_snapshot(company_name, ticker)
        market_summary = summarize_market_snapshot(snapshot)
        return ResearchData(
            company_name=snapshot["company_name"],
            ticker=snapshot["ticker"],
            industry=str(snapshot["industry"]),
            market_size=float(snapshot["market_size"]),
            growth_rate=float(snapshot["growth_rate"]),
            competitive_position=str(snapshot["competitive_position"]),
            filing_url=filing_url,
            notes=list(snapshot.get("notes", [])),
        )

    def run(self, company_name: str, ticker: str, filing_url: str = ""):
        return self.gather_market_data(company_name, ticker, filing_url)
