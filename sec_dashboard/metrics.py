from __future__ import annotations

from collections import defaultdict

from .models import FinancialFact, MetricValue


def _calc(metric: str, year: int, value: float | None, unit: str, formula: str, inputs: list[str], reason: str | None = None) -> MetricValue:
    return MetricValue(metric=metric, fiscal_year=year, value=value, unit=unit, formula=formula, input_metrics=inputs, reason_na=reason)


def calculate_metrics(facts: list[FinancialFact]) -> list[MetricValue]:
    values: dict[int, dict[str, float]] = defaultdict(dict)
    for fact in facts:
        if fact.is_selected:
            values[fact.fiscal_year][fact.metric] = fact.value
    out: list[MetricValue] = []
    years = sorted(values)

    def ratio(year: int, name: str, numerator: str, denominator: str, multiplier: float = 1.0, unit: str = "x") -> None:
        row = values[year]
        missing = [key for key in (numerator, denominator) if key not in row]
        if missing or row.get(denominator) == 0:
            reason = f"Missing SEC input(s): {', '.join(missing)}" if missing else f"{denominator} is zero"
            out.append(_calc(name, year, None, unit, f"{numerator} / {denominator}", [numerator, denominator], reason))
        else:
            out.append(_calc(name, year, row[numerator] / row[denominator] * multiplier, unit, f"{numerator} / {denominator}", [numerator, denominator]))

    for idx, year in enumerate(years):
        row = values[year]
        if "Gross Profit" not in row and {"Revenue", "Cost of Revenue"} <= row.keys():
            out.append(_calc("Gross Profit", year, row["Revenue"] - row["Cost of Revenue"], "USD", "Revenue - Cost of Revenue", ["Revenue", "Cost of Revenue"]))
        if {"Operating Cash Flow", "CapEx"} <= row.keys():
            out.append(_calc("Free Cash Flow", year, row["Operating Cash Flow"] - abs(row["CapEx"]), "USD", "Operating Cash Flow - abs(CapEx)", ["Operating Cash Flow", "CapEx"]))
        else:
            missing = sorted({"Operating Cash Flow", "CapEx"} - row.keys())
            out.append(_calc("Free Cash Flow", year, None, "USD", "Operating Cash Flow - abs(CapEx)", ["Operating Cash Flow", "CapEx"], f"Missing SEC input(s): {', '.join(missing)}"))
        debt_parts = [row[x] for x in ("Debt Current", "Debt Noncurrent") if x in row]
        out.append(_calc("Debt", year, sum(debt_parts) if debt_parts else None, "USD", "Debt Current + Debt Noncurrent", ["Debt Current", "Debt Noncurrent"], None if debt_parts else "No debt facts selected"))

        ratio(year, "Operating Margin", "Operating Income", "Revenue", 100, "%")
        ratio(year, "Net Margin", "Net Income", "Revenue", 100, "%")
        ratio(year, "ROA", "Net Income", "Assets", 100, "%")
        ratio(year, "ROE", "Net Income", "Shareholders' Equity", 100, "%")
        ratio(year, "Current Ratio", "Current Assets", "Current Liabilities")
        ratio(year, "Cash Conversion", "Operating Cash Flow", "Net Income")
        ratio(year, "CapEx / Revenue", "CapEx", "Revenue", 100, "%")

        fcf = next((m.value for m in out if m.fiscal_year == year and m.metric == "Free Cash Flow"), None)
        if fcf is not None and row.get("Revenue"):
            out.append(_calc("FCF Margin", year, fcf / row["Revenue"] * 100, "%", "Free Cash Flow / Revenue", ["Free Cash Flow", "Revenue"]))
        else:
            out.append(_calc("FCF Margin", year, None, "%", "Free Cash Flow / Revenue", ["Free Cash Flow", "Revenue"], "Free Cash Flow or Revenue unavailable"))

        debt = next((m.value for m in out if m.fiscal_year == year and m.metric == "Debt"), None)
        equity = row.get("Shareholders' Equity")
        out.append(_calc("Debt / Equity", year, debt / equity if debt is not None and equity else None, "x", "Debt / Shareholders' Equity", ["Debt", "Shareholders' Equity"], None if debt is not None and equity else "Debt or equity unavailable/zero"))

        previous = values[years[idx - 1]].get("Revenue") if idx else None
        current = row.get("Revenue")
        out.append(_calc("Revenue Growth", year, (current / previous - 1) * 100 if current is not None and previous else None, "%", "Revenue / prior-year Revenue - 1", ["Revenue"], None if current is not None and previous else "Current or prior-year Revenue unavailable"))
    return sorted(out, key=lambda m: (m.fiscal_year, m.metric))


def trend_summary(facts: list[FinancialFact], calculated: list[MetricValue]) -> list[dict[str, object]]:
    rows: dict[str, dict[int, float]] = defaultdict(dict)
    for item in [*facts, *calculated]:
        if item.value is not None:
            rows[item.metric][item.fiscal_year] = item.value
    result = []
    for metric, series in sorted(rows.items()):
        years = sorted(series)
        latest = years[-1]
        row: dict[str, object] = {"metric": metric, "latest_year": latest, "latest_value": series[latest]}
        for horizon in (3, 5, 10):
            if len(years) >= horizon and series[years[-horizon]] != 0:
                periods = horizon - 1
                start, end = series[years[-horizon]], series[latest]
                row[f"trend_{horizon}y"] = ((end / start) ** (1 / periods) - 1) * 100 if start > 0 and end >= 0 else (end / start - 1) * 100
            else:
                row[f"trend_{horizon}y"] = None
        result.append(row)
    return result

