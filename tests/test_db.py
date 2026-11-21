import pytest
import aiosqlite
import tempfile
import os
from pathlib import Path

from database.db import init_db, get_db, close_db


@pytest.mark.asyncio
async def test_init_db_creates_tables(db_context):
    """Test that init_db creates all required tables."""
    # Check tables exist
    async with db_context.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ) as cursor:
        tables = await cursor.fetchall()
    table_names = {row[0] for row in tables}

    assert "users" in table_names
    assert "history" in table_names
    assert "favorites" in table_names


@pytest.mark.asyncio
async def test_wal_mode_enabled(db_context):
    """Test that WAL mode is enabled."""
    async with db_context.execute("PRAGMA journal_mode") as cursor:
        result = await cursor.fetchone()
    assert result[0].upper() == "WAL"


@pytest.mark.asyncio
async def test_users_table_schema(db_context):
    """Test users table has correct schema."""
    async with db_context.execute("PRAGMA table_info(users)") as cursor:
        columns = await cursor.fetchall()
    column_names = {col[1] for col in columns}

    # The actual schema from db.py
    expected = {
        "id", "username", "first_name", "last_name",
        "language", "notifications_enabled", "total_processed",
        "registered_at", "created_at"
    }
    assert expected.issubset(column_names)


@pytest.mark.asyncio
async def test_history_table_schema(db_context):
    """Test history table has correct schema."""
    async with db_context.execute("PRAGMA table_info(history)") as cursor:
        columns = await cursor.fetchall()
    column_names = {col[1] for col in columns}

    expected = {
        "id", "user_id", "action_type", "platform", "original_url",
        "file_id", "file_name", "file_size", "result_status",
        "error_message", "created_at"
    }
    assert expected.issubset(column_names)


@pytest.mark.asyncio
async def test_favorites_table_schema(db_context):
    """Test favorites table has correct schema."""
    async with db_context.execute("PRAGMA table_info(favorites)") as cursor:
        columns = await cursor.fetchall()
    column_names = {col[1] for col in columns}

    expected = {
        "id", "user_id", "file_id", "file_type", "file_name",
        "file_size", "caption", "platform", "original_url", "created_at"
    }
    assert expected.issubset(column_names)