import aiosqlite
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

from database.db import get_db, close_db


@dataclass
class User:
    id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    language: str
    registered_at: datetime
    total_processed: int
    notifications_enabled: bool
    last_activity: Optional[datetime] = None


class UserRepository:
    """Repository class for user operations."""

    def __init__(self, db):
        self.db = db

    async def get_or_create(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: Optional[str] = "en"
    ) -> User:
        """Get existing user or create new one."""
        cursor = await self.db.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()

        if row:
            return User(
                id=row["id"],
                username=row["username"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                language=row["language"],
                registered_at=datetime.fromisoformat(row["registered_at"]) if row["registered_at"] else datetime.now(),
                total_processed=row["total_processed"],
                notifications_enabled=bool(row["notifications_enabled"]),
                last_activity=datetime.fromisoformat(row["last_activity"]) if row["last_activity"] else None,
            )

        await self.db.execute(
            "INSERT INTO users (id, username, first_name, last_name, language) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, first_name, last_name, language_code)
        )
        await self.db.commit()

        return User(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language=language_code,
            registered_at=datetime.now(),
            total_processed=0,
            notifications_enabled=True,
        )

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        cursor = await self.db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row:
            return None
        return User(
            id=row["id"],
            username=row["username"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            language=row["language"],
            registered_at=datetime.fromisoformat(row["registered_at"]) if row["registered_at"] else datetime.now(),
            total_processed=row["total_processed"],
            notifications_enabled=bool(row["notifications_enabled"]),
            last_activity=datetime.fromisoformat(row["last_activity"]) if row["last_activity"] else None,
        )

    async def update_language(self, user_id: int, language: str) -> bool:
        """Update user's language."""
        cursor = await self.db.execute(
            "UPDATE users SET language = ? WHERE id = ?",
            (language, user_id)
        )
        await self.db.commit()
        return cursor.rowcount > 0

    async def update_notifications(self, user_id: int, enabled: bool) -> bool:
        """Update user's notification setting."""
        cursor = await self.db.execute(
            "UPDATE users SET notifications_enabled = ? WHERE id = ?",
            (1 if enabled else 0, user_id)
        )
        await self.db.commit()
        return cursor.rowcount > 0

    async def increment_processed(self, user_id: int) -> None:
        """Increment processed count for user."""
        await self.db.execute(
            "UPDATE users SET total_processed = total_processed + 1 WHERE id = ?",
            (user_id,)
        )
        await self.db.commit()

    async def update_last_activity(self, user_id: int) -> None:
        """Update last activity timestamp."""
        await self.db.execute(
            "UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,)
        )
        await self.db.commit()

    async def get_user_stats(self, user_id: int) -> dict[str, int]:
        """Get user statistics."""
        cursor = await self.db.execute(
            "SELECT (SELECT COUNT(*) FROM history WHERE user_id = ?) as history_count, "
            "(SELECT COUNT(*) FROM favorites WHERE user_id = ?) as favorites_count",
            (user_id, user_id)
        )
        row = await cursor.fetchone()
        return {
            "history_count": row["history_count"],
            "favorites_count": row["favorites_count"]
        }

    async def delete_user_data(self, user_id: int) -> None:
        """Delete all user data."""
        await self.db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await self.db.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
        await self.db.execute("DELETE FROM favorites WHERE user_id = ?", (user_id,))
        await self.db.commit()

    async def get_all_users(self, page: int = 0, limit: int = 10) -> list[User]:
        """Get all users with pagination."""
        offset = page * limit
        cursor = await self.db.execute(
            "SELECT * FROM users ORDER BY id LIMIT ? OFFSET ?",
            (limit, offset)
        )
        rows = await cursor.fetchall()
        return [
            User(
                id=row["id"],
                username=row["username"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                language=row["language"],
                registered_at=datetime.fromisoformat(row["registered_at"]) if row["registered_at"] else datetime.now(),
                total_processed=row["total_processed"],
                notifications_enabled=bool(row["notifications_enabled"]),
                last_activity=datetime.fromisoformat(row["last_activity"]) if row["last_activity"] else None,
            )
            for row in rows
        ]

    async def get_total_users_count(self) -> int:
        """Get total count of users."""
        cursor = await self.db.execute("SELECT COUNT(*) as count FROM users")
        row = await cursor.fetchone()
        return row["count"]


# Keep the old function-based API as well
async def get_or_create_user(user_id: int, username: Optional[str], first_name: Optional[str], last_name: Optional[str] = None) -> User:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()

        if row:
            return User(
                id=row["id"],
                username=row["username"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                language=row["language"],
                registered_at=datetime.fromisoformat(row["registered_at"]) if row["registered_at"] else datetime.now(),
                total_processed=row["total_processed"],
                notifications_enabled=bool(row["notifications_enabled"]),
            )

        await db.execute(
            "INSERT INTO users (id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
            (user_id, username, first_name, last_name)
        )
        await db.commit()

        return User(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language="en",
            registered_at=datetime.now(),
            total_processed=0,
            notifications_enabled=True,
        )
    finally:
        await close_db(db)


async def update_user_language(user_id: int, language: str) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute(
            "UPDATE users SET language = ? WHERE id = ?",
            (language, user_id)
        )
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await close_db(db)


async def update_notifications(user_id: int, enabled: bool) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute(
            "UPDATE users SET notifications_enabled = ? WHERE id = ?",
            (1 if enabled else 0, user_id)
        )
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await close_db(db)


async def increment_processed(user_id: int) -> None:
    db = await get_db()
    try:
        await db.execute(
            "UPDATE users SET total_processed = total_processed + 1 WHERE id = ?",
            (user_id,)
        )
        await db.commit()
    finally:
        await close_db(db)


async def get_user(user_id: int) -> Optional[User]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row:
            return None
        return User(
            id=row["id"],
            username=row["username"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            language=row["language"],
            registered_at=datetime.fromisoformat(row["registered_at"]) if row["registered_at"] else datetime.now(),
            total_processed=row["total_processed"],
            notifications_enabled=bool(row["notifications_enabled"]),
        )
    finally:
        await close_db(db)


async def get_user_count() -> int:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT COUNT(*) as count FROM users")
        row = await cursor.fetchone()
        return row["count"]
    finally:
        await close_db(db)


async def get_active_user_count(since_days: int = 7) -> int:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT COUNT(*) as count FROM users WHERE registered_at >= datetime('now', ?)",
            (f"-{since_days} days",)
        )
        row = await cursor.fetchone()
        return row["count"]
    finally:
        await close_db(db)


async def delete_user_data(user_id: int) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await close_db(db)