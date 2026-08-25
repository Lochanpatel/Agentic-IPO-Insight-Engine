"""Financial metrics calculations for IPO analysis."""

from __future__ import annotations

from typing import Dict

from ipo_insights.models import FinancialMetrics


def compute_financial_metrics(revenue: float, ebitda_margin: float, growth_rate: float, market_cap: float) -> FinancialMetrics:
    net_margin = max(0.04, ebitda_margin - 0.06)
    return FinancialMetrics(
        revenue=revenue,
        ebitda_margin=ebitda_margin,
        net_margin=net_margin,
        growth_rate=growth_rate,
        market_cap=market_cap,
    )


def summarize_financial_metrics(metrics: FinancialMetrics) -> str:
    return (
        f"Revenue: ${metrics.revenue:,.0f} | EBITDA Margin: {metrics.ebitda_margin * 100:.1f}% | "
        f"Net Margin: {metrics.net_margin * 100:.1f}% | Growth Rate: {metrics.growth_rate * 100:.1f}%"
    )


def build_financial_summary(raw_metrics: Dict[str, object]) -> str:
    revenue = float(raw_metrics.get("revenue", 0.0))
    ebitda_margin = float(raw_metrics.get("ebitda_margin", 0.0))
    growth_rate = float(raw_metrics.get("growth_rate", 0.0))
    market_cap = float(raw_metrics.get("market_cap", revenue * 4.0))
    metrics = compute_financial_metrics(revenue, ebitda_margin, growth_rate, market_cap)
    return summarize_financial_metrics(metrics)
