import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def parse_comma_separated_ints(value: str) -> list[int]:
    if not value:
        return []
    return [int(x.strip()) for x in value.split(",") if x.strip()]


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_ids: list[int]
    ai_api_key: str | None
    ai_base_url: str
    ai_model: str
    database_path: Path
    max_file_size: int
    max_download_size: int
    rate_limit_messages: int
    rate_limit_window: int
    temp_file_ttl: int
    default_language: str
    log_level: str

    @classmethod
    def from_env(cls) -> "Config":
        bot_token = os.getenv("BOT_TOKEN", "").strip()
        if not bot_token:
            raise ValueError("BOT_TOKEN is required")

        admin_ids_str = os.getenv("ADMIN_IDS", "").strip()
        admin_ids = parse_comma_separated_ints(admin_ids_str)
        if not admin_ids:
            raise ValueError("ADMIN_IDS is required (comma-separated list of user IDs)")

        ai_api_key = os.getenv("AI_API_KEY", "").strip() or None
        ai_base_url = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").strip()
        ai_model = os.getenv("AI_MODEL", "gpt-4o-mini").strip()

        database_path = Path(os.getenv("DATABASE_PATH", "storage/database.sqlite3")).resolve()

        max_file_size = int(os.getenv("MAX_FILE_SIZE", "52428800"))
        max_download_size = int(os.getenv("MAX_DOWNLOAD_SIZE", "104857600"))

        rate_limit_messages = int(os.getenv("RATE_LIMIT_MESSAGES", "30"))
        rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

        temp_file_ttl = int(os.getenv("TEMP_FILE_TTL", "3600"))

        default_language = os.getenv("DEFAULT_LANGUAGE", "en").strip().lower()
        if default_language not in ("en", "si"):
            default_language = "en"

        log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()

        return cls(
            bot_token=bot_token,
            admin_ids=admin_ids,
            ai_api_key=ai_api_key,
            ai_base_url=ai_base_url,
            ai_model=ai_model,
            database_path=database_path,
            max_file_size=max_file_size,
            max_download_size=max_download_size,
            rate_limit_messages=rate_limit_messages,
            rate_limit_window=rate_limit_window,
            temp_file_ttl=temp_file_ttl,
            default_language=default_language,
            log_level=log_level,
        )


config = Config.from_env()