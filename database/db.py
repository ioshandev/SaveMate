import aiosqlite
import logging
from pathlib import Path

from config import config

logger = logging.getLogger(__name__)

SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language TEXT DEFAULT 'en',
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_processed INTEGER DEFAULT 0,
    notifications_enabled INTEGER DEFAULT 1,
    last_activity TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    platform TEXT,
    original_url TEXT,
    file_id TEXT,
    file_name TEXT,
    file_size INTEGER,
    result_status TEXT NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_history_user_id ON history(user_id);
CREATE INDEX IF NOT EXISTS idx_history_created_at ON history(created_at);

CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    file_id TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_name TEXT,
    file_size INTEGER,
    caption TEXT,
    platform TEXT,
    original_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);
"""


async def init_db() -> None:
    db_path = Path(config.database_path) if isinstance(config.database_path, str) else config.database_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(db_path) as db:
        await db.executescript(SCHEMA)
        await db.commit()
    logger.info("Database initialized at %s", db_path)


async def get_db() -> aiosqlite.Connection:
    db_path = Path(config.database_path) if isinstance(config.database_path, str) else config.database_path
    db = await aiosqlite.connect(db_path)
    db.row_factory = aiosqlite.Row
    return db


async def close_db(db: aiosqlite.Connection) -> None:
    await db.close()


class _DbManager:
    """Context manager for database connections."""

    def __init__(self):
        self.db = None

    async def __aenter__(self) -> aiosqlite.Connection:
        self.db = await get_db()
        return self.db

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            await close_db(self.db)
        return False


def get_db_ctx() -> _DbManager:
    """Get a database context manager."""
    return _DbManager()