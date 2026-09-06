"""Main IPO analysis engine."""

from __future__ import annotations

import logging
from typing import Optional

from ipo_insights.agents.coordinator import AgentCoordinator
from ipo_insights.config import get_settings
from ipo_insights.models import IPOInsight
from ipo_insights.reporting import build_detailed_report

logger = logging.getLogger(__name__)


class IPOAnalysisEngine:
    """High-level orchestration layer for IPO analysis.
    
    The engine provides a simple interface for end-to-end IPO analysis,
    combining market research, financial analysis, and risk assessment
    into comprehensive investment insights with detailed reporting.
    """

    def __init__(self, company_name: str | None = None, ticker: str | None = None):
        """Initialize the IPO analysis engine.
        
        Args:
            company_name: Default company name for analysis
            ticker: Default stock ticker for analysis
        """
        try:
            settings = get_settings()
            self.company_name = company_name or settings.default_company_name
            self.ticker = (ticker or settings.default_ticker).upper()
            self.coordinator = AgentCoordinator()
            logger.info(f"IPOAnalysisEngine initialized with default: {self.company_name} ({self.ticker})")
        except Exception as e:
            logger.error(f"Engine initialization failed: {e}")
            raise

    def _validate_analysis_inputs(self, ticker: str | None, company_name: str | None) -> tuple:
        """Validate and resolve analysis inputs.
        
        Args:
            ticker: Optional ticker override
            company_name: Optional company name override
            
        Returns:
            Tuple of (resolved_ticker, resolved_company_name)
            
        Raises:
            ValueError: If no valid inputs provided
        """
        resolved_ticker = (ticker or self.ticker).upper() if (ticker or self.ticker) else None
        resolved_company = company_name or self.company_name
        
        if not resolved_ticker or not resolved_company:
            raise ValueError("ticker and company_name must be provided or set as defaults")
        
        return resolved_ticker, resolved_company

    def analyze_ipo(
        self, 
        ticker: str | None = None, 
        company_name: str | None = None, 
        filing_url: str = ""
    ) -> IPOInsight:
        """Analyze an IPO and return structured investment insight.
        
        Args:
            ticker: Stock ticker symbol (uses default if not provided)
            company_name: Company name (uses default if not provided)
            filing_url: Optional URL to SEC filing document
            
        Returns:
            IPOInsight object with analysis results
            
        Raises:
            ValueError: If inputs are invalid
        """
        try:
            resolved_ticker, resolved_company = self._validate_analysis_inputs(ticker, company_name)
            logger.info(f"Analyzing IPO: {resolved_company} ({resolved_ticker})")
            
            insight = self.coordinator.analyze(resolved_company, resolved_ticker, filing_url)
            
            logger.info(f"IPO analysis complete: {resolved_ticker}")
            return insight
        except Exception as e:
            logger.error(f"IPO analysis failed: {e}")
            raise

    def run(
        self, 
        ticker: str | None = None, 
        company_name: str | None = None, 
        filing_url: str = ""
    ) -> str:
        """Execute full IPO analysis pipeline and return formatted report.
        
        This is the primary entry point for end-to-end IPO analysis,
        combining research, analysis, and reporting into a single call.
        
        Args:
            ticker: Stock ticker symbol (uses default if not provided)
            company_name: Company name (uses default if not provided)
            filing_url: Optional URL to SEC filing document
            
        Returns:
            Formatted text report of IPO analysis
            
        Raises:
            ValueError: If inputs are invalid
        """
        logger.info("Starting IPO analysis pipeline")
        try:
            insight = self.analyze_ipo(ticker=ticker, company_name=company_name, filing_url=filing_url)
            report = build_detailed_report(insight)
            logger.info("IPO analysis pipeline completed successfully")
            return report
        except Exception as e:
            logger.error(f"IPO analysis pipeline failed: {e}")
            raise

    def get_coordinator_cache_stats(self) -> dict:
        """Get cache statistics from the coordinator.
        
        Returns:
            Dictionary with cache statistics
        """
        return self.coordinator.get_cache_stats()

    def clear_coordinator_cache(self) -> None:
        """Clear the coordinator's research data cache.
        
        Use this to force fresh data gathering on next analysis.
        """
        self.coordinator.clear_cache()
        logger.info("Coordinator cache cleared via engine")
