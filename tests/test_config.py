import pytest
from pathlib import Path
from config import Config


def test_config_creation():
    """Test Config dataclass creation."""
    config = Config(
        bot_token="test_token",
        admin_ids=[123, 456],
        ai_api_key="test_key",
        ai_base_url="https://api.openai.com/v1",
        ai_model="gpt-4o-mini",
        database_path=Path("/tmp/test.db"),
        max_file_size=52428800,
        max_download_size=104857600,
        rate_limit_messages=30,
        rate_limit_window=60,
        temp_file_ttl=3600,
        default_language="en",
        log_level="INFO",
    )
    assert config.bot_token == "test_token"
    assert config.admin_ids == [123, 456]
    assert config.ai_api_key == "test_key"
    assert config.ai_base_url == "https://api.openai.com/v1"
    assert config.ai_model == "gpt-4o-mini"


def test_config_defaults():
    """Test Config default values."""
    config = Config(
        bot_token="test",
        admin_ids=[],
        ai_api_key=None,
        ai_base_url="https://api.openai.com/v1",
        ai_model="gpt-4o-mini",
        database_path=Path("/tmp/test.db"),
        max_file_size=52428800,
        max_download_size=104857600,
        rate_limit_messages=30,
        rate_limit_window=60,
        temp_file_ttl=3600,
        default_language="en",
        log_level="INFO",
    )
    assert config.ai_base_url == "https://api.openai.com/v1"
    assert config.ai_model == "gpt-4o-mini"
    assert config.rate_limit_messages == 30
    assert config.rate_limit_window == 60
    assert config.log_level == "INFO"
    assert config.default_language == "en"


def test_config_from_env(monkeypatch):
    """Test Config from_env method."""
    monkeypatch.setenv("BOT_TOKEN", "env_token")
    monkeypatch.setenv("ADMIN_IDS", "111,222")
    monkeypatch.setenv("AI_API_KEY", "env_key")
    monkeypatch.setenv("RATE_LIMIT_MESSAGES", "50")
    monkeypatch.setenv("DEFAULT_LANGUAGE", "si")

    config = Config.from_env()
    assert config.bot_token == "env_token"
    assert config.admin_ids == [111, 222]
    assert config.ai_api_key == "env_key"
    assert config.rate_limit_messages == 50
    assert config.default_language == "si"


def test_admin_ids_parsing():
    """Test admin IDs parsing."""
    config = Config(
        bot_token="test",
        admin_ids=[1, 2, 3],
        ai_api_key=None,
        ai_base_url="https://api.openai.com/v1",
        ai_model="gpt-4o-mini",
        database_path=Path("/tmp/test.db"),
        max_file_size=52428800,
        max_download_size=104857600,
        rate_limit_messages=30,
        rate_limit_window=60,
        temp_file_ttl=3600,
        default_language="en",
        log_level="INFO",
    )
    assert config.admin_ids == [1, 2, 3]

    config = Config(
        bot_token="test",
        admin_ids=[],
        ai_api_key=None,
        ai_base_url="https://api.openai.com/v1",
        ai_model="gpt-4o-mini",
        database_path=Path("/tmp/test.db"),
        max_file_size=52428800,
        max_download_size=104857600,
        rate_limit_messages=30,
        rate_limit_window=60,
        temp_file_ttl=3600,
        default_language="en",
        log_level="INFO",
    )
    assert config.admin_ids == []