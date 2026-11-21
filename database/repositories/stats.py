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