from datetime import date

from sec_dashboard.metrics import calculate_metrics
from sec_dashboard.models import FinancialFact


def fact(metric: str, value: float, year: int = 2024) -> FinancialFact:
    return FinancialFact(metric=metric, cik="0000320193", fiscal_year=year, start=date(year - 1, 10, 1), end=date(year, 9, 30), form="10-K", filed=date(year, 11, 1), accession_number="0000320193-24-000001", taxonomy="us-gaap", xbrl_tag=metric.replace(" ", ""), unit="USD", value=value)


def metric_value(items, name, year=2024):
    return next(x.value for x in items if x.metric == name and x.fiscal_year == year)


def test_core_calculations():
    facts = [fact("Revenue", 100), fact("Operating Income", 25), fact("Net Income", 20), fact("Operating Cash Flow", 30), fact("CapEx", 10), fact("Assets", 200), fact("Shareholders' Equity", 80), fact("Debt Current", 5), fact("Debt Noncurrent", 35), fact("Current Assets", 60), fact("Current Liabilities", 30)]
    result = calculate_metrics(facts)
    assert metric_value(result, "Free Cash Flow") == 20
    assert metric_value(result, "Operating Margin") == 25
    assert metric_value(result, "Debt") == 40
    assert metric_value(result, "Debt / Equity") == 0.5
    assert metric_value(result, "Current Ratio") == 2


def test_missing_inputs_are_na_not_invented():
    result = calculate_metrics([fact("Revenue", 100)])
    fcf = next(x for x in result if x.metric == "Free Cash Flow")
    assert fcf.value is None
    assert "Missing SEC input" in fcf.reason_na

