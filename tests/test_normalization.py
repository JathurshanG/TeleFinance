from sec_dashboard.normalization import normalize_company_facts


def test_latest_amended_fact_wins_and_is_flagged():
    payload = {"cik": 320193, "entityName": "Example", "facts": {"us-gaap": {"RevenueFromContractWithCustomerExcludingAssessedTax": {"units": {"USD": [
        {"start": "2023-10-01", "end": "2024-09-28", "val": 100, "accn": "a", "fy": 2024, "fp": "FY", "form": "10-K", "filed": "2024-11-01"},
        {"start": "2023-10-01", "end": "2024-09-28", "val": 101, "accn": "b", "fy": 2024, "fp": "FY", "form": "10-K/A", "filed": "2024-12-01"},
    ]}}}}}
    facts, flags = normalize_company_facts(payload, years=10)
    revenue = next(x for x in facts if x.metric == "Revenue")
    assert revenue.value == 101
    assert revenue.is_amended
    assert any(x.code == "CONFLICTING_FACTS" for x in flags)
    assert any(x.code == "AMENDED_VALUE" for x in flags)


def test_primary_period_beats_later_filed_comparative_context():
    payload = {"cik": 320193, "entityName": "Example", "facts": {"us-gaap": {"RevenueFromContractWithCustomerExcludingAssessedTax": {"units": {"USD": [
        {"start": "2024-10-01", "end": "2025-09-30", "val": 120, "accn": "primary", "fy": 2025, "fp": "FY", "form": "10-K", "filed": "2025-11-01"},
        {"start": "2022-10-01", "end": "2023-09-30", "val": 90, "accn": "comparative", "fy": 2025, "fp": "FY", "form": "10-K", "filed": "2025-11-01"},
    ]}}}}}
    facts, _ = normalize_company_facts(payload, years=10)
    revenue = next(x for x in facts if x.metric == "Revenue")
    assert revenue.value == 120
    assert revenue.accession_number == "primary"
