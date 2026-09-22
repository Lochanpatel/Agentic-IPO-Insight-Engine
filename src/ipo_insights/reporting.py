"""Utilities for building IPO analysis reports."""

from __future__ import annotations

import logging
from datetime import datetime

from ipo_insights.models import IPOInsight

logger = logging.getLogger(__name__)


def build_ipo_summary(insight: IPOInsight) -> str:
    """Build a concise one-line IPO summary.
    
    Args:
        insight: IPOInsight object with analysis results
        
    Returns:
        Formatted summary string
    """
    summary = (
        f"{insight.company_name} ({insight.ticker}) - Score {insight.recommendation_score}/10 | "
        f"Risk: {insight.risk_level} | Signal: {insight.valuation_signal} | "
        f"Grade: {insight.investment_grade} | Confidence: {insight.confidence}"
    )
    logger.debug(f"Summary built for {insight.ticker}")
    return summary


def build_detailed_report(insight: IPOInsight) -> str:
    """Build comprehensive IPO analysis report with timestamp.
    
    Args:
        insight: IPOInsight object with analysis results
        
    Returns:
        Detailed formatted report string
    """
    logger.info(f"Building detailed report for {insight.ticker}")
    
    # Get base report from insight model
    base_report = insight.generate_report()
    
    # Add timestamp and metadata
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    enhanced_report = (
        f"\n{'='*70}\n"
        f"Report Generated: {timestamp}\n"
        f"{'='*70}\n\n"
        f"{base_report}\n\n"
        f"{'='*70}\n"
        f"Report Metadata:\n"
        f"- Model Version: 1.0\n"
        f"- Analysis Depth: Comprehensive\n"
        f"- Data Sources: Market data, Filing summary, Risk assessment\n"
        f"{'='*70}\n"
    )
    
    logger.info(f"Detailed report completed for {insight.ticker}")
    return enhanced_report


def build_executive_summary(insight: IPOInsight) -> str:
    """Build executive summary focused on key takeaways.
    
    Args:
        insight: IPOInsight object with analysis results
        
    Returns:
        Executive summary string
    """
    logger.debug(f"Building executive summary for {insight.ticker}")
    
    summary = [
        f"EXECUTIVE SUMMARY - {insight.company_name} ({insight.ticker})",
        "=" * 60,
        "",
        f"Recommendation Score: {insight.recommendation_score}/10",
        f"Valuation Signal: {insight.valuation_signal}",
        f"Confidence Level: {insight.confidence}",
        f"Investment Grade: {insight.investment_grade}",
        f"Risk Level: {insight.risk_level}",
        "",
        "Investment Thesis:",
        insight.thesis,
        "",
        "Key Drivers:",
    ]
    
    for driver in insight.key_drivers:
        summary.append(f"  • {driver}")
    
    summary.extend([
        "",
        "Comparable Context:",
    ])
    
    for comparable in insight.comparables:
        summary.append(f"  • {comparable}")
    
    summary.extend([
        "",
        "Scenario Analysis:",
        build_scenario_summary(insight),
        "",
        "Financial Profile:",
        insight.financial_summary,
    ])
    
    result = "\n".join(summary)
    logger.debug(f"Executive summary built for {insight.ticker}")
    return result


def build_investor_brief(insight: IPOInsight) -> str:
    """Build concise investor brief with key investment points.
    
    Args:
        insight: IPOInsight object with analysis results
        
    Returns:
        Investor brief string
    """
    logger.debug(f"Building investor brief for {insight.ticker}")
    
    risk_color = "🔴 HIGH" if insight.risk_level == "High" else "🟡 MODERATE" if insight.risk_level == "Moderate" else "🟢 LOW"
    
    brief = f"""
INVESTOR BRIEF - {insight.company_name} ({insight.ticker})
{'='*60}

QUICK STATS:
  Recommendation Score:  {insight.recommendation_score}/10
  Valuation Signal:      {insight.valuation_signal}
  Investment Grade:      {insight.investment_grade}
  Confidence:            {insight.confidence}
  Risk Assessment:       {risk_color}

KEY METRICS:
{insight.financial_summary}

SCENARIO ANALYSIS:
{build_scenario_summary(insight)}

MARKET CATALYSTS:
{chr(10).join(f'  • {item}' for item in insight.market_catalysts) if insight.market_catalysts else '  • No specific catalysts identified.'}

KEY RISKS:
{chr(10).join(f'  • {item}' for item in insight.key_risks) if insight.key_risks else '  • No material risks identified.'}

MARKET CONTEXT:
{insight.market_summary}

INVESTMENT IDEA:
{insight.thesis}

{'='*60}
"""
    
    logger.info(f"Investor brief created for {insight.ticker}")
    return brief


def export_report_json(insight: IPOInsight) -> dict:
    """Export IPO insight as JSON-serializable dictionary.
    
    Args:
        insight: IPOInsight object with analysis results
        
    Returns:
        Dictionary representation suitable for JSON export
    """
    logger.debug(f"Exporting {insight.ticker} insights to JSON format")
    
    export_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "report_type": "IPO Analysis",
            "version": "1.0",
        },
        "company": {
            "name": insight.company_name,
            "ticker": insight.ticker,
            "filing_url": insight.filing_url,
        },
        "analysis": {
            "recommendation_score": insight.recommendation_score,
            "risk_level": insight.risk_level,
            "valuation_signal": insight.valuation_signal,
            "confidence": insight.confidence,
            "investment_grade": insight.investment_grade,
            "thesis": insight.thesis,
            "scenario_summary": insight.scenario_summary,
            "valuation_range": insight.valuation_range,
            "market_catalysts": insight.market_catalysts,
            "key_risks": insight.key_risks,
        },
        "financials": {
            "market_summary": insight.market_summary,
            "financial_summary": insight.financial_summary,
            "key_drivers": insight.key_drivers,
            "comparables": insight.comparables,
        },
    }
    
    logger.info(f"JSON export prepared for {insight.ticker}")
    return export_data


def build_scenario_summary(insight: IPOInsight) -> str:
    """Build a succinct scenario analysis summary.
    
    Args:
        insight: IPOInsight object with analysis results
        
    Returns:
        Scenario summary string
    """
    if not insight.valuation_range:
        return "No scenario analysis available."

    base_case = insight.valuation_range.get("base_case", 0.0)
    bull_case = insight.valuation_range.get("bull_case", 0.0)
    bear_case = insight.valuation_range.get("bear_case", 0.0)
    return (
        f"Valuation range: base ${base_case:,.0f} | bull ${bull_case:,.0f} | bear ${bear_case:,.0f}. "
        f"{insight.scenario_summary or 'Scenario analysis indicates a moderate outlook.'}"
    )


def build_institutional_memo(insight: IPOInsight) -> str:
    """Build a structured, memo-style report suitable for institutional distribution.

    The memo includes an executive summary, detailed financials, scenario analysis,
    peer benchmarking, market catalysts, risks, and a concise recommendation.
    """
    # Header
    lines = [
        f"INSTITUTIONAL MEMO - {insight.company_name} ({insight.ticker})",
        "=" * 80,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    # Executive summary
    lines.append("EXECUTIVE SUMMARY")
    lines.append("-" * 40)
    lines.append(build_executive_summary(insight))
    lines.append("")

    # Financials
    lines.append("DETAILED FINANCIAL PROFILE")
    lines.append("-" * 40)
    lines.append(insight.financial_summary)
    lines.append("")

    # Scenario analysis
    lines.append("SCENARIO ANALYSIS")
    lines.append("-" * 40)
    if insight.valuation_range:
        base = insight.valuation_range.get("base_case", 0.0)
        bull = insight.valuation_range.get("bull_case", 0.0)
        bear = insight.valuation_range.get("bear_case", 0.0)
        lines.append(f"Base: ${base:,.0f} | Bull: ${bull:,.0f} | Bear: ${bear:,.0f}")
        lines.append("")
    lines.append(build_scenario_summary(insight))
    lines.append("")

    # Peer benchmarking table (text)
    lines.append("PEER BENCHMARKING")
    lines.append("-" * 40)
    if insight.competitor_benchmark:
        lines.append(f"{'Peer':<20} {'EV/Rev':>8} {'Profile':>12}")
        lines.append(f"{'-'*42}")
        for peer in insight.competitor_benchmark:
            name = peer.get('name', 'Peer')
            ev = peer.get('ev_revenue_multiple', 0.0)
            profile = peer.get('growth_profile', '')
            lines.append(f"{name:<20} {ev:8.2f} {profile:>12}")
    else:
        lines.append("No peer benchmarking available.")
    lines.append("")

    # Catalysts & Risks
    lines.append("MARKET CATALYSTS")
    lines.append("-" * 40)
    if insight.market_catalysts:
        for c in insight.market_catalysts:
            lines.append(f"- {c}")
    else:
        lines.append("- None identified")
    lines.append("")

    lines.append("KEY RISKS")
    lines.append("-" * 40)
    if insight.key_risks:
        for r in insight.key_risks:
            lines.append(f"- {r}")
    else:
        lines.append("- None identified")
    lines.append("")

    # Recommendation and metadata
    lines.append("RECOMMENDATION")
    lines.append("-" * 40)
    lines.append(f"Recommendation Score: {insight.recommendation_score}/10")
    lines.append(f"Valuation Signal: {insight.valuation_signal} | Confidence: {insight.confidence} | Grade: {insight.investment_grade}")
    lines.append("")

    # Append JSON-export hint for downstream systems
    lines.append("EXPORT NOTE: Use export_report_json(insight) for machine-readable payload.")

    return "\n".join(lines)


def export_report_html(insight: IPOInsight) -> str:
    """Export the institutional memo as a minimal HTML document.

    This is intended for quick email/portal rendering; styling is intentionally minimal.
    """
    memo = build_institutional_memo(insight)
    html = (
        "<html><head><meta charset='utf-8'><title>Institutional Memo</title>"
        "<style>body{font-family:Arial,Helvetica,sans-serif;margin:20px;white-space:pre-wrap}</style></head>"
        "<body>"
        f"<pre>{memo}</pre>"
        "</body></html>"
    )
    return html
