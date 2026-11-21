"""Web API configuration."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class WebConfig:
    """Configuration for the web API."""

    api_key: str
    database_path: Path
    rate_limit_requests: int
    rate_limit_window: int
    cors_origins: List[str]
    allow_unauthenticated_stats: bool = False

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    @classmethod
    def from_env(cls) -> "WebConfig":
        api_key = os.getenv("WEB_API_KEY", "").strip()
        if not api_key:
            import logging
            logging.getLogger(__name__).warning("WEB_API_KEY not set - protected endpoints will be disabled")

        db_path_str = os.getenv("WEB_API_DB_PATH", "")
        if db_path_str:
            database_path = Path(db_path_str).resolve()
        else:
            # Fall back to bot's database path
            database_path = Path("storage/database.sqlite3").resolve()

        rate_limit_requests = int(os.getenv("WEB_RATE_LIMIT_REQUESTS", "100"))
        rate_limit_window = int(os.getenv("WEB_RATE_LIMIT_WINDOW", "60"))

        cors_origins_str = os.getenv("WEB_CORS_ORIGINS", "")
        cors_origins = [
            origin.strip()
            for origin in cors_origins_str.split(",")
            if origin.strip()
        ] or ["*"]  # Allow all by default

        return cls(
            api_key=api_key,
            database_path=database_path,
            rate_limit_requests=rate_limit_requests,
            rate_limit_window=rate_limit_window,
            cors_origins=cors_origins,
            allow_unauthenticated_stats=os.getenv("WEB_ALLOW_PUBLIC_STATS", "false").lower() == "true",
        )


# Global config instance
web_config = WebConfig.from_env()