"""Coordinator that orchestrates research and analysis agents."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

from ipo_insights.agents.analysis_agent import AnalysisAgent
from ipo_insights.agents.research_agent import ResearchAgent
from ipo_insights.data.file_parser import parse_filing_summary
from ipo_insights.models import IPOInsight, ResearchData

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Orchestrates research and analysis agents for IPO insights.
    
    The coordinator manages the workflow of gathering research data and
    performing financial analysis to produce comprehensive IPO insights.
    It handles caching and error propagation from sub-agents.
    """

    def __init__(self):
        """Initialize the coordinator with research and analysis agents."""
        self.research_agent = ResearchAgent()
        self.analysis_agent = AnalysisAgent()
        self._cache: dict = {}  # Simple cache for research data
        logger.info("AgentCoordinator initialized")

    def _get_cache_key(self, company_name: str, ticker: str) -> str:
        """Generate a cache key for coordinator results.
        
        Args:
            company_name: Company name
            ticker: Stock ticker
            
        Returns:
            Cache key string
        """
        return f"{company_name.lower()}:{ticker.upper()}"

    def _validate_coordination_inputs(self, company_name: str, ticker: str) -> None:
        """Validate inputs for coordination workflow.
        
        Args:
            company_name: Company name
            ticker: Stock ticker
            
        Raises:
            ValueError: If inputs are invalid
        """
        if not company_name or not ticker:
            raise ValueError("company_name and ticker are required")

    def analyze(
        self, company_name: str, ticker: str, filing_url: str = "", use_cache: bool = True
    ) -> IPOInsight:
        """Analyze an IPO by coordinating research and analysis agents.
        
        Args:
            company_name: Name of the company
            ticker: Stock ticker symbol
            filing_url: Optional URL to SEC filing
            use_cache: Whether to use cached research data
            
        Returns:
            IPOInsight with complete analysis
            
        Raises:
            ValueError: If inputs are invalid
        """
        logger.info(f"Starting IPO analysis for {company_name} ({ticker})")
        
        # Validate inputs
        self._validate_coordination_inputs(company_name, ticker)
        
        # Check cache
        cache_key = self._get_cache_key(company_name, ticker)
        research_data = None
        if use_cache and cache_key in self._cache:
            logger.info(f"Using cached research data for {cache_key}")
            research_data = self._cache[cache_key]
        
        # Gather research if not cached
        if research_data is None:
            try:
                research_data = self.research_agent.gather_market_data(company_name, ticker, filing_url)
                self._cache[cache_key] = research_data
            except Exception as e:
                logger.error(f"Research gathering failed: {e}")
                raise
        
        # Parse filing summary
        filing_summary = {}
        if filing_url:
            try:
                filing_summary = parse_filing_summary(
                    f"IPO filing for {company_name}: revenue and growth details available"
                )
                logger.info(f"Parsed filing summary with {len(filing_summary)} fields")
            except Exception as e:
                logger.warning(f"Filing summary parsing failed: {e}")
        
        # Run analysis
        try:
            insight = self.analysis_agent.analyze(research_data, filing_summary)
            logger.info(f"Analysis complete: {ticker} - Score {insight.recommendation_score}/10")
            return insight
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise

    def clear_cache(self) -> None:
        """Clear the research data cache.
        
        Use this to force fresh data gathering on next analysis.
        """
        self._cache.clear()
        logger.info("Coordinator cache cleared")

    def get_cache_stats(self) -> dict:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        return {
            "cache_size": len(self._cache),
            "cached_companies": list(self._cache.keys()),
        }
