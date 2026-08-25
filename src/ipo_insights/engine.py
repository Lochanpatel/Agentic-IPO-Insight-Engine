"""Main IPO analysis engine."""

from __future__ import annotations

from ipo_insights.agents.coordinator import AgentCoordinator
from ipo_insights.config import get_settings
from ipo_insights.models import IPOInsight


class IPOAnalysisEngine:
    """High-level orchestration layer for IPO analysis."""

    def __init__(self, company_name: str | None = None, ticker: str | None = None):
        settings = get_settings()
        self.company_name = company_name or settings.default_company_name
        self.ticker = (ticker or settings.default_ticker).upper()
        self.coordinator = AgentCoordinator()

    def analyze_ipo(self, ticker: str | None = None, company_name: str | None = None, filing_url: str = "") -> IPOInsight:
        resolved_ticker = (ticker or self.ticker).upper()
        resolved_company = company_name or self.company_name
        return self.coordinator.analyze(resolved_company, resolved_ticker, filing_url)

    def run(self, ticker: str | None = None, company_name: str | None = None, filing_url: str = "") -> str:
        insight = self.analyze_ipo(ticker=ticker, company_name=company_name, filing_url=filing_url)
        return insight.generate_report()
