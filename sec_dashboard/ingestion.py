from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .sec_client import SECClient


class SECIngestion:
    def __init__(self, client: SECClient, raw_dir: Path):
        self.client = client
        self.raw_dir = raw_dir
        raw_dir.mkdir(parents=True, exist_ok=True)

    def fetch(self, cik: str, *, refresh: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
        cik10 = self.client.normalize_cik(cik)
        facts = self.client.company_facts(cik10, refresh=refresh)
        submissions = self.client.submissions(cik10, refresh=refresh)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        target = self.raw_dir / cik10
        target.mkdir(parents=True, exist_ok=True)
        (target / f"companyfacts_{stamp}.json").write_text(json.dumps(facts), encoding="utf-8")
        (target / f"submissions_{stamp}.json").write_text(json.dumps(submissions), encoding="utf-8")
        return facts, submissions

