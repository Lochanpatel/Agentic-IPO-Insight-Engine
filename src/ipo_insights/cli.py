"""Command line entry point for IPO analysis."""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Optional

from ipo_insights.config import configure_logging, get_settings
from ipo_insights.engine import IPOAnalysisEngine

logger = logging.getLogger(__name__)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser.
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Analyze an IPO opportunity with the Agentic IPO Insight Engine.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m ipo_insights.cli --ticker ACME --company "ACME Corp"
  python -m ipo_insights.cli --ticker TECH --filing-url "https://example.com/s1"
        """,
    )
    
    parser.add_argument(
        "--ticker",
        default="EXMP",
        help="Ticker symbol for the IPO candidate (default: EXMP)",
    )
    parser.add_argument(
        "--company",
        default="Example IPO",
        help="Company name for the IPO candidate (default: Example IPO)",
    )
    parser.add_argument(
        "--filing-url",
        default="",
        help="Optional URL to SEC filing or prospectus document",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level (default: INFO)",
    )
    parser.add_argument(
        "--export-json",
        action="store_true",
        help="Export results as JSON instead of text report",
    )
    parser.add_argument(
        "--executive-summary",
        action="store_true",
        help="Generate executive summary format instead of full report",
    )
    
    return parser


def validate_cli_inputs(ticker: str, company: str) -> tuple[str, str]:
    """Validate and normalize CLI inputs.
    
    Args:
        ticker: Stock ticker symbol
        company: Company name
        
    Returns:
        Tuple of (normalized_ticker, normalized_company)
        
    Raises:
        ValueError: If inputs are invalid
    """
    if not ticker:
        raise ValueError("Ticker is required")
    if not company:
        raise ValueError("Company name is required")
    
    normalized_ticker = ticker.upper().strip()
    normalized_company = company.strip()
    
    if len(normalized_ticker) > 5:
        raise ValueError(f"Ticker too long: {normalized_ticker}")
    
    logger.debug(f"CLI inputs validated: {normalized_ticker}, {normalized_company}")
    return normalized_ticker, normalized_company


def main(args: Optional[list[str]] = None) -> int:
    """Main CLI entry point.
    
    Args:
        args: Optional list of command line arguments (for testing)
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        # Parse arguments
        parser = create_argument_parser()
        parsed_args = parser.parse_args(args)
        
        # Configure logging
        configure_logging(parsed_args.log_level)
        logger.info("IPO Analysis Engine CLI started")
        
        # Validate inputs
        ticker, company = validate_cli_inputs(parsed_args.ticker, parsed_args.company)
        
        logger.info(f"Analyzing {company} ({ticker})")
        
        # Initialize engine
        engine = IPOAnalysisEngine(company_name=company, ticker=ticker)
        
        # Run analysis
        result = engine.run(
            ticker=ticker,
            company_name=company,
            filing_url=parsed_args.filing_url,
        )
        
        # Handle different output formats
        if parsed_args.export_json:
            import json
            from ipo_insights.reporting import export_report_json
            
            insight = engine.analyze_ipo(ticker=ticker, company_name=company, filing_url=parsed_args.filing_url)
            json_data = export_report_json(insight)
            print(json.dumps(json_data, indent=2))
        elif parsed_args.executive_summary:
            from ipo_insights.reporting import build_executive_summary
            
            insight = engine.analyze_ipo(ticker=ticker, company_name=company, filing_url=parsed_args.filing_url)
            print(build_executive_summary(insight))
        else:
            # Default detailed report
            print(result)
        
        logger.info(f"Analysis complete for {ticker}")
        return 0
        
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
