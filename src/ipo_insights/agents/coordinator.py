"""Coordinator that orchestrates research and analysis agents."""

from __future__ import annotations

from ipo_insights.agents.analysis_agent import AnalysisAgent
from ipo_insights.agents.research_agent import ResearchAgent
from ipo_insights.data.file_parser import parse_filing_summary
from ipo_insights.models import IPOInsight


class AgentCoordinator:
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.analysis_agent = AnalysisAgent()

    def analyze(self, company_name: str, ticker: str, filing_url: str = "") -> IPOInsight:
        research_data = self.research_agent.gather_market_data(company_name, ticker, filing_url)
        filing_summary = parse_filing_summary("")
        if filing_url:
            filing_summary = parse_filing_summary(f"IPO filing for {company_name}: revenue and growth details available")
        return self.analysis_agent.analyze(research_data, filing_summary)
