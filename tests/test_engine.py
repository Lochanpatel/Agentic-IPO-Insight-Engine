from ipo_insights.engine import IPOAnalysisEngine


def test_analyze_ipo_returns_report():
    engine = IPOAnalysisEngine(company_name="Northstar Cloud", ticker="NSCL")
    insight = engine.analyze_ipo(ticker="NSCL", company_name="Northstar Cloud", filing_url="https://example.com/filing.pdf")

    assert insight.ticker == "NSCL"
    assert "Northstar Cloud" in insight.company_name
    assert insight.recommendation_score >= 1
    assert insight.recommendation_score <= 10
    assert "IPO Insight" in insight.generate_report()
