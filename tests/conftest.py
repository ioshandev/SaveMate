import pytest
import pytest_asyncio
import asyncio
import aiosqlite
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import importlib

# CRITICAL: Set up environment variables BEFORE any imports that trigger Config.from_env()
os.environ.setdefault("BOT_TOKEN", "test_token")
os.environ.setdefault("ADMIN_IDS", "123456789")
os.environ.setdefault("AI_API_KEY", "test_key")
os.environ.setdefault("AI_BASE_URL", "https://api.openai.com/v1")
os.environ.setdefault("AI_MODEL", "gpt-4o-mini")

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now we can safely import Config
from config import Config


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db_path():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest_asyncio.fixture
async def db_context(test_db_path):
    """Create a test database context (not a connection)."""
    import database.db as db_module

    # Create a test config with temporary database path
    test_config = Config(
        bot_token="test_token",
        admin_ids=[123456789],
        database_path=Path(test_db_path),
        ai_api_key="test_key",
        ai_base_url="https://api.openai.com/v1",
        ai_model="gpt-4o-mini",
        max_file_size=52428800,
        max_download_size=104857600,
        rate_limit_messages=30,
        rate_limit_window=60,
        temp_file_ttl=3600,
        default_language="en",
        log_level="DEBUG",
    )

    # Patch config
    original_config = db_module.config
    db_module.config = test_config

    from database.db import init_db, get_db, close_db
    await init_db()

    db = await get_db()
    yield db

    await close_db(db)
    db_module.config = original_config


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    return Config(
        bot_token="test_token",
        admin_ids=[],
        ai_api_key="test_key",
        ai_base_url="https://api.openai.com/v1",
        ai_model="gpt-4o-mini",
        database_path=Path("/tmp/test_db.sqlite3"),
        max_file_size=52428800,
        max_download_size=104857600,
        rate_limit_messages=30,
        rate_limit_window=60,
        temp_file_ttl=3600,
        default_language="en",
        log_level="DEBUG",
    )


# Module-level mock_config instance for tests that import it directly
@pytest.fixture(scope="session")
def config():
    """Return a config instance for tests."""
    return Config(
        bot_token="test_token",
        admin_ids=[123456789],
        ai_api_key="test_key",
        ai_base_url="https://api.openai.com/v1",
        ai_model="gpt-4o-mini",
        database_path=Path("/tmp/test_db.sqlite3"),
        max_file_size=52428800,
        max_download_size=104857600,
        rate_limit_messages=30,
        rate_limit_window=60,
        temp_file_ttl=3600,
        default_language="en",
        log_level="DEBUG",
    )


@pytest.fixture
def mock_bot():
    """Create a mock bot."""
    bot = AsyncMock()
    bot.id = 123456789
    return bot


@pytest.fixture
def mock_message():
    """Create a mock message."""
    msg = AsyncMock()
    msg.message_id = 1
    msg.date = 1234567890
    msg.chat = MagicMock()
    msg.chat.id = 123456789
    msg.chat.type = "private"
    msg.from_user = MagicMock()
    msg.from_user.id = 123456789
    msg.from_user.username = "testuser"
    msg.from_user.first_name = "Test"
    msg.from_user.last_name = "User"
    msg.from_user.language_code = "en"
    msg.text = "Hello"
    return msg


@pytest.fixture
def mock_callback_query():
    """Create a mock callback query."""
    cb = AsyncMock()
    cb.id = "callback_1"
    cb.from_user = MagicMock()
    cb.from_user.id = 123456789
    cb.from_user.username = "testuser"
    cb.from_user.first_name = "Test"
    cb.message = AsyncMock()
    cb.message.message_id = 1
    cb.message.chat = MagicMock()
    cb.message.chat.id = 123456789
    cb.data = '{"a":"test"}'
    return cb


@pytest.fixture
def mock_state():
    """Create a mock FSM context."""
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()
    state.clear = AsyncMock()
    state.get_state = AsyncMock(return_value=None)
    return state


@pytest.fixture
def mock_db():
    """Create a mock database connection."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.fetchall = AsyncMock(return_value=[])
    db.fetchone = AsyncMock(return_value=None)
    db.commit = AsyncMock()
    return db