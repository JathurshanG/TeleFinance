from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RecordKind(str, Enum):
    FACT = "FACT"
    CALCULATED = "CALCULATED"
    FLAG = "FLAG"


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class FinancialFact(BaseModel):
    kind: RecordKind = RecordKind.FACT
    metric: str
    cik: str
    entity: str | None = None
    fiscal_year: int
    fiscal_period: str = "FY"
    start: date | None = None
    end: date
    form: str
    filed: date
    accession_number: str
    taxonomy: str
    xbrl_tag: str
    unit: str
    value: float
    frame: str | None = None
    source_url: str | None = None
    is_amended: bool = False
    is_selected: bool = True


class MetricValue(BaseModel):
    kind: RecordKind = RecordKind.CALCULATED
    metric: str
    fiscal_year: int
    value: float | None = None
    unit: str
    formula: str
    input_metrics: list[str] = Field(default_factory=list)
    reason_na: str | None = None


class AuditFlag(BaseModel):
    kind: RecordKind = RecordKind.FLAG
    code: str
    severity: Severity
    fiscal_year: int | None = None
    metric: str | None = None
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class Filing(BaseModel):
    cik: str
    accession_number: str
    filing_date: date
    report_date: date | None = None
    form: str
    primary_document: str
    is_amended: bool = False
    filing_url: str


class AnalysisBundle(BaseModel):
    cik: str
    entity: str
    ticker: str | None = None
    facts: list[FinancialFact]
    calculated: list[MetricValue]
    flags: list[AuditFlag]
    filings: list[Filing]

