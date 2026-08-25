"""Command line entry point for IPO analysis."""

from __future__ import annotations

import argparse

from ipo_insights.engine import IPOAnalysisEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze an IPO opportunity with the Agentic IPO Insight Engine.")
    parser.add_argument("--ticker", default="EXMP", help="Ticker symbol for the IPO candidate.")
    parser.add_argument("--company", default="Example IPO", help="Company name for the IPO candidate.")
    parser.add_argument("--filing-url", default="", help="Optional filing or prospectus URL.")
    args = parser.parse_args()

    engine = IPOAnalysisEngine(company_name=args.company, ticker=args.ticker)
    print(engine.run(ticker=args.ticker, company_name=args.company, filing_url=args.filing_url))


if __name__ == "__main__":
    main()
