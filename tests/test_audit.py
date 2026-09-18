from datetime import date

from sec_dashboard.audit import run_audit
from sec_dashboard.models import FinancialFact


def _fact(metric, value):
    return FinancialFact(metric=metric, cik="0000000001", fiscal_year=2024, end=date(2024, 12, 31), form="10-K", filed=date(2025, 2, 1), accession_number="x", taxonomy="us-gaap", xbrl_tag=metric, unit="USD", value=value)


def test_balance_sheet_imbalance():
    flags = run_audit([_fact("Assets", 100_000_000), _fact("Liabilities", 50_000_000), _fact("Shareholders' Equity", 30_000_000)], [])
    assert any(flag.code == "BALANCE_SHEET_IMBALANCE" for flag in flags)
