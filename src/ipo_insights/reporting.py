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
        f"Risk: {insight.risk_level} | Signal: {insight.valuation_signal} | Confidence: {insight.confidence}"
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
  Investment Thesis:     {insight.confidence}
  Risk Assessment:       {risk_color}

KEY METRICS:
{insight.financial_summary}

SCENARIO ANALYSIS:
{build_scenario_summary(insight)}

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
            "thesis": insight.thesis,
            "scenario_summary": insight.scenario_summary,
            "valuation_range": insight.valuation_range,
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
