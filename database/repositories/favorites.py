import aiosqlite
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from database.db import get_db, close_db


@dataclass
class Favorite:
    id: int
    user_id: int
    file_id: str
    file_type: str
    file_name: Optional[str]
    file_size: Optional[int]
    caption: Optional[str]
    platform: Optional[str]
    original_url: Optional[str]
    created_at: datetime


class FavoritesRepository:
    """Repository class for favorites operations."""

    def __init__(self, db):
        self.db = db

    async def add(
        self,
        user_id: int,
        file_id: str,
        file_type: str,
        title: Optional[str] = None,
        platform: Optional[str] = None,
        url: Optional[str] = None,
        thumbnail_url: Optional[str] = None
    ) -> int:
        """Add a favorite entry."""
        cursor = await self.db.execute(
            """INSERT INTO favorites
            (user_id, file_id, file_type, file_name, platform, original_url)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, file_id, file_type, title, platform, url)
        )
        await self.db.commit()
        return cursor.lastrowid

    async def get_user_favorites(self, user_id: int, page: int = 0, limit: int = 10) -> list[dict]:
        """Get user favorites with pagination, returns list of dicts."""
        offset = page * limit
        cursor = await self.db.execute(
            """SELECT * FROM favorites
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
                "file_id": row["file_id"],
                "file_type": row["file_type"],
                "file_name": row["file_name"],
                "title": row["file_name"],  # Alias for backward compatibility
                "file_size": row["file_size"],
                "caption": row["caption"],
                "platform": row["platform"],
                "original_url": row["original_url"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    async def get_user_favorites_count(self, user_id: int) -> int:
        """Get count of user's favorites."""
        cursor = await self.db.execute(
            "SELECT COUNT(*) as count FROM favorites WHERE user_id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        return row["count"]

    async def remove_favorite(self, user_id: int, favorite_id: int) -> bool:
        """Remove a favorite."""
        cursor = await self.db.execute(
            "DELETE FROM favorites WHERE user_id = ? AND id = ?",
            (user_id, favorite_id)
        )
        await self.db.commit()
        return cursor.rowcount > 0

    async def get_favorite(self, user_id: int, favorite_id: int) -> Optional[dict]:
        """Get a specific favorite by ID."""
        cursor = await self.db.execute(
            "SELECT * FROM favorites WHERE user_id = ? AND id = ?",
            (user_id, favorite_id)
        )
        row = await cursor.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "file_id": row["file_id"],
            "file_type": row["file_type"],
            "file_name": row["file_name"],
            "title": row["file_name"],  # Alias for backward compatibility
            "file_size": row["file_size"],
            "caption": row["caption"],
            "platform": row["platform"],
            "original_url": row["original_url"],
            "created_at": row["created_at"],
        }

    async def is_favorite(self, user_id: int, url: str) -> bool:
        """Check if a URL is already favorited."""
        cursor = await self.db.execute(
            "SELECT 1 FROM favorites WHERE user_id = ? AND original_url = ?",
            (user_id, url)
        )
        row = await cursor.fetchone()
        return row is not None


# Keep the old function-based API as well
async def add_favorite(
    user_id: int,
    file_id: str,
    file_type: str,
    file_name: Optional[str] = None,
    file_size: Optional[int] = None,
    caption: Optional[str] = None,
    platform: Optional[str] = None,
    original_url: Optional[str] = None,
) -> int:
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO favorites
            (user_id, file_id, file_type, file_name, file_size, caption, platform, original_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, file_id, file_type, file_name, file_size, caption, platform, original_url)
        )
        await db.commit()
        return cursor.lastrowid
    finally:
        await close_db(db)


async def remove_favorite(user_id: int, favorite_id: int) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute(
            "DELETE FROM favorites WHERE user_id = ? AND id = ?",
            (user_id, favorite_id)
        )
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await close_db(db)


async def get_user_favorites(user_id: int, limit: int = 10, offset: int = 0) -> list[Favorite]:
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT * FROM favorites
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?""",
            (user_id, limit, offset)
        )
        rows = await cursor.fetchall()
        return [
            Favorite(
                id=row["id"],
                user_id=row["user_id"],
                file_id=row["file_id"],
                file_type=row["file_type"],
                file_name=row["file_name"],
                file_size=row["file_size"],
                caption=row["caption"],
                platform=row["platform"],
                original_url=row["original_url"],
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
            )
            for row in rows
        ]
    finally:
        await close_db(db)


async def get_favorites_count(user_id: int) -> int:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT COUNT(*) as count FROM favorites WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return row["count"]
    finally:
        await close_db(db)


async def is_favorite(user_id: int, file_id: str) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT 1 FROM favorites WHERE user_id = ? AND file_id = ?", (user_id, file_id))
        row = await cursor.fetchone()
        return row is not None
    finally:
        await close_db(db)