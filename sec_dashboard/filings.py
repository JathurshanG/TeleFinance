from __future__ import annotations

from datetime import date
from typing import Any

from .models import Filing


def parse_filings(payload: dict[str, Any], cik: str, limit: int = 40) -> list[Filing]:
    recent = payload.get("filings", {}).get("recent", {})
    result: list[Filing] = []
    forms = recent.get("form", [])
    for idx, form in enumerate(forms):
        if form not in {"10-K", "10-K/A"}:
            continue
        accn = recent["accessionNumber"][idx]
        document = recent["primaryDocument"][idx]
        accession_plain = accn.replace("-", "")
        result.append(Filing(
            cik=cik,
            accession_number=accn,
            filing_date=date.fromisoformat(recent["filingDate"][idx]),
            report_date=date.fromisoformat(recent["reportDate"][idx]) if recent["reportDate"][idx] else None,
            form=form,
            primary_document=document,
            is_amended=form.endswith("/A"),
            filing_url=f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_plain}/{document}",
        ))
        if len(result) >= limit:
            break
    return result

