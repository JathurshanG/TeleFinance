from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from .models import AuditFlag, FinancialFact, Severity
from .tags import EXPECTED_UNITS, INSTANT_METRICS, TAG_CANDIDATES


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _duration_days(row: dict[str, Any]) -> int | None:
    start, end = _date(row.get("start")), _date(row.get("end"))
    return (end - start).days if start and end else None


def _score(row: dict[str, Any], tag_rank: int, instant: bool) -> tuple[int, int, int, int, int]:
    form = row.get("form", "")
    duration = _duration_days(row)
    annual_period = instant or (duration is not None and 330 <= duration <= 380)
    filed = _date(row.get("filed"))
    end = _date(row.get("end"))
    # Company Facts repeats comparative contexts in later filings while assigning
    # the current filing's `fy`. The primary FY context is normally the one whose
    # period end is closest to the filing date. Prefer it over repeated history.
    filing_lag = (filed - end).days if filed and end else 99_999
    return (
        1 if form in {"10-K", "10-K/A"} else 0,
        1 if annual_period else 0,
        -max(0, abs(filing_lag) - 180),
        -tag_rank,
        (filed or date.min).toordinal(),
    )


def normalize_company_facts(payload: dict[str, Any], years: int = 10) -> tuple[list[FinancialFact], list[AuditFlag]]:
    cik = str(payload.get("cik", "")).zfill(10)
    entity = payload.get("entityName")
    us_gaap = payload.get("facts", {}).get("us-gaap", {})
    flags: list[AuditFlag] = []
    selected: list[FinancialFact] = []
    by_metric_year: dict[tuple[str, int], list[FinancialFact]] = defaultdict(list)

    for metric, tags in TAG_CANDIDATES.items():
        found_tag = False
        for tag_rank, tag in enumerate(tags):
            concept = us_gaap.get(tag)
            if not concept:
                continue
            found_tag = True
            for unit, rows in concept.get("units", {}).items():
                for row in rows:
                    fy = row.get("fy")
                    form = row.get("form", "")
                    end = _date(row.get("end"))
                    filed = _date(row.get("filed"))
                    accn = row.get("accn")
                    if not (isinstance(fy, int) and end and filed and accn and form in {"10-K", "10-K/A"}):
                        continue
                    duration = _duration_days(row)
                    if metric not in INSTANT_METRICS and (duration is None or not 300 <= duration <= 400):
                        continue
                    fact = FinancialFact(
                        metric=metric,
                        cik=cik,
                        entity=entity,
                        fiscal_year=fy,
                        fiscal_period=row.get("fp") or "FY",
                        start=_date(row.get("start")),
                        end=end,
                        form=form,
                        filed=filed,
                        accession_number=accn,
                        taxonomy="us-gaap",
                        xbrl_tag=tag,
                        unit=unit,
                        value=float(row["val"]),
                        frame=row.get("frame"),
                        source_url=f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/",
                        is_amended=form.endswith("/A"),
                        is_selected=False,
                    )
                    by_metric_year[(metric, fy)].append(fact)
        if not found_tag:
            flags.append(AuditFlag(code="TAG_NOT_FOUND", severity=Severity.WARNING, metric=metric, message="No candidate XBRL tag exists in Company Facts."))

    fiscal_years = sorted({fy for _, fy in by_metric_year}, reverse=True)[:years]
    for (metric, fy), candidates in by_metric_year.items():
        if fy not in fiscal_years:
            continue
        expected = EXPECTED_UNITS.get(metric, set())
        valid = [f for f in candidates if f.unit in expected] or candidates
        ranked = sorted(
            valid,
            key=lambda f: _score(f.model_dump(mode="json"), TAG_CANDIDATES[metric].index(f.xbrl_tag), metric in INSTANT_METRICS),
            reverse=True,
        )
        chosen = ranked[0].model_copy(update={"is_selected": True})
        selected.append(chosen)
        if chosen.unit not in expected:
            flags.append(AuditFlag(code="UNIT_MISMATCH", severity=Severity.ERROR, fiscal_year=fy, metric=metric, message=f"Expected {sorted(expected)}, got {chosen.unit}."))
        unique_values = {f.value for f in valid}
        if len(valid) > 1 and len(unique_values) > 1:
            flags.append(AuditFlag(code="CONFLICTING_FACTS", severity=Severity.WARNING, fiscal_year=fy, metric=metric, message="Multiple annual 10-K facts disagree; the latest best-scored filing was selected.", details={"candidate_count": len(valid), "selected_accession": chosen.accession_number}))
        if chosen.is_amended:
            flags.append(AuditFlag(code="AMENDED_VALUE", severity=Severity.INFO, fiscal_year=fy, metric=metric, message="Selected value comes from a 10-K/A amendment."))

    for fy in fiscal_years:
        present = {f.metric for f in selected if f.fiscal_year == fy}
        for metric in TAG_CANDIDATES:
            if metric not in present:
                flags.append(AuditFlag(code="MISSING_METRIC", severity=Severity.WARNING, fiscal_year=fy, metric=metric, message="No reliable annual fact selected; displayed as N/A."))
    return sorted(selected, key=lambda f: (f.fiscal_year, f.metric)), flags
