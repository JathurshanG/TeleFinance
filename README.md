# SEC Financial Audit Dashboard

A traceable Python/Dash pipeline for reviewing up to 15 years of annual SEC EDGAR facts. Apple (`CIK 0000320193`) is the default demonstration company, but the pipeline accepts any SEC ticker or CIK.

The application never fills a missing financial value with an estimate. Missing or unreliable inputs remain `N/A`, with a reason. Every displayed record is explicitly classified as:

- `FACT`: selected from an official SEC Company Facts filing context;
- `CALCULATED`: derived from named SEC inputs and a visible formula;
- `FLAG`: a data-quality observation requiring review.

## Quick start

Python 3.11+ is recommended.

```bash
cd sec_apple_dash_foundation
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and provide an honest SEC User-Agent containing an organization/name and monitored email address:

```text
SEC_USER_AGENT=Example Analytics analyst@example.com
```

Then run:

```bash
python app/app.py
```

Open `http://127.0.0.1:8050`. Enter `AAPL`, `0000320193`, or another US issuer identifier. The first request needs internet access; subsequent requests use the local JSON cache.

Run tests with:

```bash
PYTHONPATH=. pytest -q
```

## Architecture

```text
SEC Company Facts + Submissions
             │
        SECClient (identity, rate limit, HTTP cache)
             │
        ingestion (immutable timestamped raw JSON)
             │
        XBRL normalization (canonical metric/tag map)
             │
        annual 10-K selection (period/unit/form/amendment scoring)
             │
        ┌─────┴────────┐
   audit flags      calculations
        └─────┬────────┘
          AnalysisBundle
                │
        Dash charts + source tables
```

| Module | Responsibility |
|---|---|
| `sec_dashboard/sec_client.py` | Official SEC endpoints, CIK/ticker resolution, throttling, disk cache |
| `sec_dashboard/ingestion.py` | Timestamped raw payload retention |
| `sec_dashboard/tags.py` | Ordered canonical-to-XBRL tag candidates and expected units |
| `sec_dashboard/normalization.py` | Annual period filtering, scoring, provenance, duplicates/amendments |
| `sec_dashboard/metrics.py` | Ratios, FCF, debt and 3/5/10-year trends |
| `sec_dashboard/audit.py` | Accounting and plausibility checks |
| `sec_dashboard/models.py` | Typed FACT/CALCULATED/FLAG contracts |
| `sec_dashboard/service.py` | Pipeline orchestration |
| `sec_dashboard/ui.py` | Dash views, graphs and underlying data tables |

## Selection and audit policy

Company Facts can contain several values for the same concept and fiscal year because later 10-K filings repeat comparative periods, concepts migrate, and filings can be amended. The normalizer:

1. considers only `10-K` and `10-K/A` observations with a fiscal year;
2. requires roughly annual duration (300–400 days) for duration concepts;
3. checks expected units (`USD`, or `USD/shares` for diluted EPS);
4. prefers annual form/context, then the earlier-listed canonical tag, then the latest filing;
5. emits `CONFLICTING_FACTS` if eligible values disagree;
6. emits `AMENDED_VALUE` if the selected source is a 10-K/A;
7. emits `MISSING_METRIC` or `UNIT_MISMATCH` rather than fabricating a value.

The selection policy is deliberately conservative but cannot replace human review. Issuer-specific extension concepts, acquisitions, 52/53-week calendars, taxonomy migrations, segments and restatements can require additional mapping. A production audit workflow should store every candidate fact, add filing-document/calculation-linkbase reconciliation, and obtain reviewer sign-off.

## Metrics

Direct SEC facts include Revenue, Gross Profit, Operating Income, Net Income, diluted EPS, Operating Cash Flow, CapEx, Cash, current assets/liabilities, debt components, Assets, Liabilities, Equity, dividends and repurchases where tagged.

Calculated outputs include Free Cash Flow, total Debt, Revenue Growth, Operating/Net/FCF Margin, ROA, ROE, Debt/Equity, Current Ratio, Cash Conversion and CapEx/Revenue. ROA and ROE currently use ending balances, not average balances; the formula is exposed so that limitation is visible. CapEx is treated as a positive cash outflow and normalized through `abs()` in FCF.

## SEC access and provenance

The client uses only official endpoints:

- `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`
- `https://data.sec.gov/submissions/CIK##########.json`
- `https://www.sec.gov/files/company_tickers.json`

Requests are identified, cached, serialized and limited to a configurable maximum of 10 requests/second (default 5). Keep the User-Agent accurate and comply with the SEC website policy.

Each selected fact preserves CIK, entity, fiscal year/period, start/end dates, form, filing date, accession number, taxonomy, XBRL tag, unit, value, frame, amendment status and an SEC Archives source URL.

## Known boundaries

- Company Facts standardizes data but does not guarantee economic comparability.
- Historical filings omitted from the `recent` submissions block may not appear in the filings tab, though Company Facts can still contain their facts.
- Alternative issuer extension tags are not guessed. Add reviewed candidates in `tags.py`.
- Trends display `N/A` unless enough observations exist. CAGR is used for positive endpoints; otherwise simple total change is shown.
- Balance-sheet reconciliation uses a 1% or $1M tolerance.
- The app is an analytical aid, not an audit opinion or investment advice.

