from __future__ import annotations

from collections import defaultdict

from .models import AuditFlag, FinancialFact, MetricValue, Severity


def run_audit(facts: list[FinancialFact], calculated: list[MetricValue], existing: list[AuditFlag] | None = None) -> list[AuditFlag]:
    flags = list(existing or [])
    rows: dict[int, dict[str, float]] = defaultdict(dict)
    for fact in facts:
        rows[fact.fiscal_year][fact.metric] = fact.value

    for year, row in rows.items():
        assets, liabilities, equity = row.get("Assets"), row.get("Liabilities"), row.get("Shareholders' Equity")
        if None not in (assets, liabilities, equity) and assets:
            delta = assets - liabilities - equity
            if abs(delta) > max(abs(assets) * 0.01, 1_000_000):
                flags.append(AuditFlag(code="BALANCE_SHEET_IMBALANCE", severity=Severity.ERROR, fiscal_year=year, message="Assets do not reconcile to Liabilities + Equity within 1% tolerance.", details={"difference": delta}))
        revenue, gross = row.get("Revenue"), row.get("Gross Profit")
        if revenue is not None and gross is not None and gross > revenue:
            flags.append(AuditFlag(code="GROSS_PROFIT_GT_REVENUE", severity=Severity.ERROR, fiscal_year=year, metric="Gross Profit", message="Gross Profit exceeds Revenue."))
        if row.get("Current Liabilities", 0) < 0 or row.get("Assets", 0) < 0:
            flags.append(AuditFlag(code="IMPOSSIBLE_SIGN", severity=Severity.ERROR, fiscal_year=year, message="A balance-sheet total has an unexpected negative sign."))

    for metric in {m.metric for m in calculated}:
        series = sorted((m.fiscal_year, m.value) for m in calculated if m.metric == metric and m.value is not None)
        for (prev_year, prev), (year, current) in zip(series, series[1:]):
            if prev and abs(current / prev - 1) > 2:
                flags.append(AuditFlag(code="EXTREME_YOY_CHANGE", severity=Severity.WARNING, fiscal_year=year, metric=metric, message=f"Calculated metric changed by more than 200% versus {prev_year}; review source facts."))
    return sorted(flags, key=lambda f: (f.fiscal_year or 0, f.severity.value, f.code), reverse=True)

