from ipo_insights.engine import IPOAnalysisEngine


def test_analyze_ipo_returns_report():
    engine = IPOAnalysisEngine(company_name="Northstar Cloud", ticker="NSCL")
    insight = engine.analyze_ipo(ticker="NSCL", company_name="Northstar Cloud", filing_url="https://example.com/filing.pdf")

    assert insight.ticker == "NSCL"
    assert "Northstar Cloud" in insight.company_name
    assert insight.recommendation_score >= 1
    assert insight.recommendation_score <= 10
    assert "IPO Insight" in insight.generate_report()


def test_analyze_ipo_includes_scenario_and_sentiment_data():
    engine = IPOAnalysisEngine(company_name="Northstar Cloud", ticker="NSCL")
    insight = engine.analyze_ipo(ticker="NSCL", company_name="Northstar Cloud", filing_url="https://example.com/filing.pdf")

    assert insight.sentiment_score >= -100
    assert insight.sentiment_score <= 100
    assert insight.sentiment_label in {"Bullish", "Positive", "Neutral", "Cautious"}
    assert insight.fair_value_estimate > 0
    assert insight.valuation_range
    assert "base_case" in insight.valuation_range
    assert insight.risk_heatmap
    assert insight.price_target_band
    assert insight.competitor_benchmark
    assert insight.risk_matrix
    assert insight.investment_grade in {"Buy", "Accumulate", "Watchlist", "Speculative", "Neutral"}
    assert insight.market_catalysts
    assert insight.key_risks
