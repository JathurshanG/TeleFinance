from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    sec_user_agent: str = os.getenv("SEC_USER_AGENT", "")
    rate_limit: float = float(os.getenv("SEC_RATE_LIMIT_PER_SECOND", "5"))
    timeout: int = int(os.getenv("SEC_TIMEOUT_SECONDS", "30"))
    cache_dir: Path = Path(os.getenv("SEC_CACHE_DIR", "data/cache"))
    raw_dir: Path = Path(os.getenv("SEC_RAW_DIR", "data/raw"))
    default_cik: str = os.getenv("DEFAULT_CIK", "0000320193")
    default_years: int = int(os.getenv("DEFAULT_YEARS", "10"))
    host: str = os.getenv("DASH_HOST", "127.0.0.1")
    port: int = int(os.getenv("DASH_PORT", "8050"))
    debug: bool = _bool("DASH_DEBUG")

    def validate(self) -> None:
        if not self.sec_user_agent or "@" not in self.sec_user_agent:
            raise ValueError(
                "SEC_USER_AGENT must identify your organization and contact email. "
                "Copy .env.example to .env and set it before fetching SEC data."
            )
        if not 0 < self.rate_limit <= 10:
            raise ValueError("SEC_RATE_LIMIT_PER_SECOND must be between 0 and 10.")

    def prepare_dirs(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()

