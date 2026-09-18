from __future__ import annotations

import hashlib
import json
import threading
import time
from pathlib import Path
from typing import Any

import requests

from .config import Settings


class SECClient:
    """Polite, cached client for official SEC JSON endpoints."""

    DATA_BASE = "https://data.sec.gov"
    WWW_BASE = "https://www.sec.gov"

    def __init__(self, settings: Settings):
        settings.validate()
        settings.prepare_dirs()
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": settings.sec_user_agent,
                "Accept-Encoding": "gzip, deflate",
                "Accept": "application/json",
            }
        )
        self._lock = threading.Lock()
        self._last_request = 0.0

    @staticmethod
    def normalize_cik(cik: str | int) -> str:
        digits = "".join(filter(str.isdigit, str(cik)))
        if not digits or len(digits) > 10:
            raise ValueError(f"Invalid CIK: {cik!r}")
        return digits.zfill(10)

    def _cache_path(self, url: str) -> Path:
        return self.settings.cache_dir / f"{hashlib.sha256(url.encode()).hexdigest()}.json"

    def _throttle(self) -> None:
        with self._lock:
            interval = 1.0 / self.settings.rate_limit
            wait = interval - (time.monotonic() - self._last_request)
            if wait > 0:
                time.sleep(wait)
            self._last_request = time.monotonic()

    def get_json(self, url: str, *, refresh: bool = False) -> dict[str, Any]:
        cache = self._cache_path(url)
        if cache.exists() and not refresh:
            return json.loads(cache.read_text(encoding="utf-8"))
        self._throttle()
        response = self.session.get(url, timeout=self.settings.timeout)
        response.raise_for_status()
        payload = response.json()
        cache.write_text(json.dumps(payload), encoding="utf-8")
        return payload

    def company_facts(self, cik: str | int, *, refresh: bool = False) -> dict[str, Any]:
        cik10 = self.normalize_cik(cik)
        return self.get_json(f"{self.DATA_BASE}/api/xbrl/companyfacts/CIK{cik10}.json", refresh=refresh)

    def submissions(self, cik: str | int, *, refresh: bool = False) -> dict[str, Any]:
        cik10 = self.normalize_cik(cik)
        return self.get_json(f"{self.DATA_BASE}/submissions/CIK{cik10}.json", refresh=refresh)

    def company_tickers(self, *, refresh: bool = False) -> dict[str, Any]:
        return self.get_json(f"{self.WWW_BASE}/files/company_tickers.json", refresh=refresh)

    def resolve_identifier(self, identifier: str) -> tuple[str, str | None]:
        if identifier.strip().isdigit():
            return self.normalize_cik(identifier), None
        ticker = identifier.strip().upper()
        for row in self.company_tickers().values():
            if row.get("ticker", "").upper() == ticker:
                return self.normalize_cik(row["cik_str"]), ticker
        raise ValueError(f"Ticker not found in SEC mapping: {ticker}")

