from __future__ import annotations

from .audit import run_audit
from .config import Settings
from .filings import parse_filings
from .ingestion import SECIngestion
from .metrics import calculate_metrics
from .models import AnalysisBundle
from .normalization import normalize_company_facts
from .sec_client import SECClient


class AnalysisService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = SECClient(settings)
        self.ingestion = SECIngestion(self.client, settings.raw_dir)

    def analyze(self, identifier: str, years: int = 10, refresh: bool = False) -> AnalysisBundle:
        cik, ticker = self.client.resolve_identifier(identifier)
        company_facts, submissions = self.ingestion.fetch(cik, refresh=refresh)
        facts, normalization_flags = normalize_company_facts(company_facts, years=years)
        calculated = calculate_metrics(facts)
        flags = run_audit(facts, calculated, normalization_flags)
        return AnalysisBundle(
            cik=cik,
            entity=company_facts.get("entityName", submissions.get("name", "Unknown")),
            ticker=ticker or next(iter(submissions.get("tickers", [])), None),
            facts=facts,
            calculated=calculated,
            flags=flags,
            filings=parse_filings(submissions, cik),
        )

