"""Agent responsible for gathering market and company research."""

from __future__ import annotations

import logging
from typing import Optional

from ipo_insights.agents.base_agent import BaseAgent
from ipo_insights.data.market_data import fetch_market_snapshot, summarize_market_snapshot
from ipo_insights.models import ResearchData

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """Gathers and structures market research data for IPO analysis.
    
    This agent collects market data, industry information, and competitive
    positioning to create a structured ResearchData object used by analysis agents.
    """

    def __init__(self):
        super().__init__(name="research_agent")
        logger.info("ResearchAgent initialized")

    def _validate_input(self, company_name: str, ticker: str) -> None:
        """Validate input parameters.
        
        Args:
            company_name: Name of the company
            ticker: Stock ticker symbol
            
        Raises:
            ValueError: If inputs are invalid
        """
        if not company_name or not isinstance(company_name, str):
            raise ValueError(f"company_name must be a non-empty string, got {company_name}")
        if not ticker or not isinstance(ticker, str):
            raise ValueError(f"ticker must be a non-empty string, got {ticker}")
        if len(ticker) > 5:
            logger.warning(f"Ticker {ticker} is unusually long")

    def _enrich_research_data(self, data: ResearchData) -> ResearchData:
        """Enrich research data with additional context.
        
        Args:
            data: Base research data
            
        Returns:
            Enriched research data with additional context
        """
        # Add industry-specific insights
        industry_lower = data.industry.lower()
        if "tech" in industry_lower or "software" in industry_lower:
            if "high growth" not in str(data.notes):
                data.notes.append("High-growth technology sector dynamics")
        elif "finance" in industry_lower or "bank" in industry_lower:
            if "regulatory" not in str(data.notes):
                data.notes.append("Subject to regulatory oversight")
        
        logger.info(f"Research data enriched for {data.company_name}")
        return data

    def gather_market_data(
        self, company_name: str, ticker: str, filing_url: str = ""
    ) -> ResearchData:
        """Gather market research data for a company.
        
        Args:
            company_name: Name of the company
            ticker: Stock ticker symbol
            filing_url: Optional URL to SEC filing
            
        Returns:
            Structured ResearchData object
            
        Raises:
            ValueError: If inputs are invalid
        """
        logger.info(f"Gathering research for {company_name} ({ticker})")
        
        # Validate inputs
        self._validate_input(company_name, ticker)
        
        # Fetch market snapshot
        snapshot = fetch_market_snapshot(company_name, ticker)
        market_summary = summarize_market_snapshot(snapshot)
        
        # Create research data
        research_data = ResearchData(
            company_name=snapshot["company_name"],
            ticker=snapshot["ticker"].upper(),
            industry=str(snapshot["industry"]),
            market_size=float(snapshot["market_size"]),
            growth_rate=float(snapshot["growth_rate"]),
            competitive_position=str(snapshot["competitive_position"]),
            filing_url=filing_url,
            notes=list(snapshot.get("notes", [])),
        )
        
        # Enrich with additional context
        research_data = self._enrich_research_data(research_data)
        
        logger.info(f"Research gathered: {research_data.company_name} - Market size: ${research_data.market_size:,.0f}")
        return research_data

    def run(self, company_name: str, ticker: str, filing_url: str = "") -> ResearchData:
        """Execute the research agent.
        
        Args:
            company_name: Name of the company
            ticker: Stock ticker symbol
            filing_url: Optional URL to SEC filing
            
        Returns:
            ResearchData with gathered market information
        """
        return self.gather_market_data(company_name, ticker, filing_url)
