"""Utilities for building IPO analysis reports."""

from __future__ import annotations

from ipo_insights.models import IPOInsight


def build_ipo_summary(insight: IPOInsight) -> str:
    return (
        f"{insight.company_name} ({insight.ticker}) - score {insight.recommendation_score}/10 | "
        f"risk {insight.risk_level} | valuation {insight.valuation_signal}"
    )


def build_detailed_report(insight: IPOInsight) -> str:
    return insight.generate_report()
