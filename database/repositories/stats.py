import aiosqlite
from dataclasses import dataclass
from typing import Optional

from database.db import get_db, close_db


@dataclass
class PlatformStats:
    platform: str
    count: int


@dataclass
class BotStats:
    total_users: int
    active_users: int
    total_processed: int
    platform_stats: list[PlatformStats]


class StatsRepository:
    """Repository class for statistics operations."""

    def __init__(self, db):
        self.db = db

    async def get_bot_stats(self) -> dict:
        """Get basic bot statistics."""
        cursor = await self.db.execute("SELECT COUNT(*) as count FROM users")
        row = await cursor.fetchone()
        total_users = row["count"]

        cursor = await self.db.execute(
            "SELECT COUNT(*) as count FROM users WHERE registered_at >= datetime('now', '-7 days')"
        )
        row = await cursor.fetchone()
        active_users_7d = row["count"]

        cursor = await self.db.execute("SELECT SUM(total_processed) as total FROM users")
        row = await cursor.fetchone()
        total_processed = row["total"] or 0

        cursor = await self.db.execute(
            """SELECT platform, COUNT(*) as count FROM history
            WHERE platform IS NOT NULL
            GROUP BY platform
            ORDER BY count DESC"""
        )
        rows = await cursor.fetchall()
        platform_stats = {
            row["platform"]: row["count"]
            for row in rows
        }

        return {
            "total_users": total_users,
            "active_users_24h": active_users_7d,  # Using 7d for compatibility
            "active_users_7d": active_users_7d,
            "total_processed": total_processed,
            "by_platform": platform_stats,
        }

    async def get_detailed_stats(self) -> dict:
        """Get detailed bot statistics."""
        stats = await self.get_bot_stats()

        cursor = await self.db.execute("SELECT COUNT(*) as count FROM history")
        row = await cursor.fetchone()
        total_history = row["count"]

        cursor = await self.db.execute("SELECT COUNT(*) as count FROM favorites")
        row = await cursor.fetchone()
        total_favorites = row["count"]

        # Get media type breakdown
        cursor = await self.db.execute(
            "SELECT media_type, COUNT(*) as count FROM history WHERE media_type IS NOT NULL GROUP BY media_type"
        )
        rows = await cursor.fetchall()
        by_media_type = {row["media_type"]: row["count"] for row in rows}

        stats["total_history"] = total_history
        stats["total_favorites"] = total_favorites
        stats["by_media_type"] = by_media_type

        return stats


async def get_bot_stats() -> BotStats:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT COUNT(*) as count FROM users")
        row = await cursor.fetchone()
        total_users = row["count"]

        cursor = await db.execute(
            "SELECT COUNT(*) as count FROM users WHERE registered_at >= datetime('now', '-7 days')"
        )
        row = await cursor.fetchone()
        active_users = row["count"]

        cursor = await db.execute("SELECT SUM(total_processed) as total FROM users")
        row = await cursor.fetchone()
        total_processed = row["total"] or 0

        cursor = await db.execute(
            """SELECT platform, COUNT(*) as count FROM history
            WHERE platform IS NOT NULL
            GROUP BY platform
            ORDER BY count DESC"""
        )
        rows = await cursor.fetchall()
        platform_stats = [
            PlatformStats(platform=row["platform"], count=row["count"])
            for row in rows
        ]

        return BotStats(
            total_users=total_users,
            active_users=active_users,
            total_processed=total_processed,
            platform_stats=platform_stats,
        )
    finally:
        await close_db(db)


async def get_user_stats(user_id: int) -> Optional[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return None

        cursor = await db.execute(
            "SELECT COUNT(*) as count FROM history WHERE user_id = ?",
            (user_id,)
        )
        history_count = (await cursor.fetchone())["count"]

        cursor = await db.execute(
            "SELECT COUNT(*) as count FROM favorites WHERE user_id = ?",
            (user_id,)
        )
        favorites_count = (await cursor.fetchone())["count"]

        return {
            "id": row["id"],
            "username": row["username"],
            "first_name": row["first_name"],
            "language": row["language"],
            "registered_at": row["registered_at"],
            "total_processed": row["total_processed"],
            "notifications_enabled": bool(row["notifications_enabled"]),
            "history_count": history_count,
            "favorites_count": favorites_count,
        }
    finally:
        await close_db(db)