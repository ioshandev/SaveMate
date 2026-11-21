import aiosqlite
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from database.db import get_db, close_db


@dataclass
class HistoryEntry:
    id: int
    user_id: int
    action_type: str
    platform: Optional[str]
    original_url: Optional[str]
    file_id: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    result_status: str
    error_message: Optional[str]
    created_at: datetime


class HistoryRepository:
    """Repository class for history operations."""

    def __init__(self, db):
        self.db = db

    async def add(
        self,
        user_id: int,
        platform: str,
        url: str,
        title: str,
        action_type: str,
        media_type: str,
        thumbnail_url: Optional[str] = None
    ) -> int:
        """Add a history entry."""
        cursor = await self.db.execute(
            """INSERT INTO history
            (user_id, action_type, platform, original_url, file_id, file_name, result_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, action_type, platform, url, None, title, "success")
        )
        await self.db.commit()
        return cursor.lastrowid

    async def get_user_history(self, user_id: int, page: int = 0, limit: int = 10) -> list[dict]:
        """Get user history with pagination, returns list of dicts."""
        offset = page * limit
        cursor = await self.db.execute(
            """SELECT * FROM history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?""",
            (user_id, limit, offset)
        )
        rows = await cursor.fetchall()
        return [
            {
                "id": row["id"],
                "user_id": row["user_id"],
                "action_type": row["action_type"],
                "platform": row["platform"],
                "original_url": row["original_url"],
                "file_id": row["file_id"],
                "file_name": row["file_name"],
                "title": row["file_name"],  # Alias for backward compatibility
                "file_size": row["file_size"],
                "result_status": row["result_status"],
                "error_message": row["error_message"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    async def get_user_history_count(self, user_id: int) -> int:
        """Get count of user's history entries."""
        cursor = await self.db.execute(
            "SELECT COUNT(*) as count FROM history WHERE user_id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        return row["count"]

    async def clear_user_history(self, user_id: int) -> int:
        """Clear all history for a user."""
        cursor = await self.db.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
        await self.db.commit()
        return cursor.rowcount


# Keep the old function-based API as well
async def add_history(
    user_id: int,
    action_type: str,
    platform: Optional[str] = None,
    original_url: Optional[str] = None,
    file_id: Optional[str] = None,
    file_name: Optional[str] = None,
    file_size: Optional[int] = None,
    result_status: str = "success",
    error_message: Optional[str] = None,
) -> int:
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO history
            (user_id, action_type, platform, original_url, file_id, file_name, file_size, result_status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, action_type, platform, original_url, file_id, file_name, file_size, result_status, error_message)
        )
        await db.commit()
        return cursor.lastrowid
    finally:
        await close_db(db)


async def get_user_history(
    user_id: int,
    limit: int = 10,
    offset: int = 0
) -> list[HistoryEntry]:
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT * FROM history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?""",
            (user_id, limit, offset)
        )
        rows = await cursor.fetchall()
        return [
            HistoryEntry(
                id=row["id"],
                user_id=row["user_id"],
                action_type=row["action_type"],
                platform=row["platform"],
                original_url=row["original_url"],
                file_id=row["file_id"],
                file_name=row["file_name"],
                file_size=row["file_size"],
                result_status=row["result_status"],
                error_message=row["error_message"],
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
            )
            for row in rows
        ]
    finally:
        await close_db(db)


async def get_history_count(user_id: int) -> int:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT COUNT(*) as count FROM history WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return row["count"]
    finally:
        await close_db(db)


async def clear_user_history(user_id: int) -> int:
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
        await db.commit()
        return cursor.rowcount
    finally:
        await close_db(db)