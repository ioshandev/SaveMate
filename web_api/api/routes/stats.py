"""Statistics endpoints for the web API."""

import logging
from datetime import datetime, timedelta
from typing import Optional

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Query, Path

from web_api.api.deps import get_db_dependency, get_current_api_user
from web_api.models.stats import (
    HealthResponse,
    BotStatusResponse,
    PublicStatsResponse,
    AdminStatsResponse,
    UserStats,
    DownloadStats,
    ActivityEntry,
    DailyStats,
    PlatformStat,
    MediaStat,
)

from database.repositories.stats import StatsRepository
from database.repositories.users import UserRepository
from database.repositories.history import HistoryRepository

logger = logging.getLogger(__name__)

stats_router = APIRouter()


def convert_row_to_dict(row: aiosqlite.Row) -> dict:
    """Convert a Row object to a dictionary."""
    return dict(row) if hasattr(row, "keys") else row


@stats_router.get(
    "/stats",
    response_model=PublicStatsResponse,
    summary="Public statistics",
    description="Get anonymized public statistics (no auth required)",
    tags=["Public"],
)
async def public_stats(
    db: aiosqlite.Connection = Depends(get_db_dependency),
) -> PublicStatsResponse:
    """
    Public statistics endpoint - no authentication required.
    Returns anonymized statistics about the bot usage.
    """
    stats_repo = StatsRepository(db)
    stats = await stats_repo.get_bot_stats()

    # Get detailed stats for additional information
    detailed_stats = await stats_repo.get_detailed_stats()

    # Get first user registration date
    cursor = await db.execute(
        "SELECT MIN(created_at) as first_user FROM users WHERE created_at IS NOT NULL"
    )
    row = await cursor.fetchone()
    first_user_str = row["first_user"] if row and row["first_user"] else None
    first_user_registered = (
        datetime.fromisoformat(first_user_str)
        if first_user_str
        else None
    )

    # Format platform stats
    platform_stats = [
        PlatformStat(platform=platform, count=count)
        for platform, count in sorted(
            stats.get("by_platform", {}).items(), key=lambda x: x[1], reverse=True
        )
    ]

    # Format media stats
    media_stats = [
        MediaStat(media_type=media_type, count=count)
        for media_type, count in sorted(
            detailed_stats.get("by_media_type", {}).items(),
            key=lambda x: x[1],
            reverse=True,
        )
    ]

    return PublicStatsResponse(
        total_users=stats.get("total_users", 0),
        active_users_24h=stats.get("active_users_24h", 0),
        active_users_7d=stats.get("active_users_7d", 0),
        total_processed=stats.get("total_processed", 0),
        total_history=detailed_stats.get("total_history", 0),
        total_favorites=detailed_stats.get("total_favorites", 0),
        platform_stats=platform_stats,
        media_stats=media_stats,
        first_user_registered=first_user_registered,
    )


@stats_router.get(
    "/admin/stats",
    response_model=AdminStatsResponse,
    summary="Detailed admin statistics",
    description="Get detailed statistics for admin use (requires API key)",
    tags=["Admin"],
)
async def admin_stats(
    api_user: dict = Depends(get_current_api_user),
    db: aiosqlite.Connection = Depends(get_db_dependency),
) -> AdminStatsResponse:
    """
    Admin statistics endpoint - requires API key authentication.
    Returns detailed statistics including user stats, download stats, and recent activity.
    """
    stats_repo = StatsRepository(db)
    user_repo = UserRepository(db)
    history_repo = HistoryRepository(db)

    # Get core statistics
    bot_stats = await stats_repo.get_bot_stats()
    detailed_stats = await stats_repo.get_detailed_stats()

    # Calculate user statistics
    total_users = await user_repo.get_total_users_count()

    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM users WHERE registered_at >= datetime('now', '-1 day')"
    )
    row = await cursor.fetchone()
    new_users_today = row["count"] if row else 0

    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM users WHERE last_activity >= datetime('now', '-1 day')"
    )
    row = await cursor.fetchone()
    active_users_today = row["count"] if row else 0

    user_stats = UserStats(
        total_users=total_users,
        new_users_today=new_users_today,
        active_users=active_users_today,
        average_processed_per_user=(
            bot_stats.get("total_processed", 0) / total_users if total_users > 0 else 0.0
        ),
    )

    # Calculate download statistics
    cursor = await db.execute("SELECT COUNT(*) as count FROM history")
    row = await cursor.fetchone()
    total_downloads = row["count"] if row else 0

    # Downloads by status
    cursor = await db.execute(
        "SELECT result_status, COUNT(*) as count FROM history GROUP BY result_status"
    )
    rows = await cursor.fetchall()
    downloads_by_status = {
        row["result_status"]: row["count"] for row in rows
    }

    # Downloads today
    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM history WHERE created_at >= datetime('now', '-1 day')"
    )
    row = await cursor.fetchone()
    downloads_today = row["count"] if row else 0

    download_stats = DownloadStats(
        total_downloads=total_downloads,
        downloads_today=downloads_today,
        downloads_by_status=downloads_by_status,
        downloads_by_platform=bot_stats.get("by_platform", {}),
    )

    # Get recent activity (last 50 entries)
    cursor = await db.execute(
        """SELECT * FROM history
        ORDER BY created_at DESC
        LIMIT 50"""
    )
    rows = await cursor.fetchall()

    recent_activity = [
        ActivityEntry(
            id=row["id"],
            user_id=row["user_id"],
            action_type=row["action_type"],
            platform=row["platform"],
            original_url=row["original_url"],
            file_name=row["file_name"],
            file_size=row["file_size"],
            result_status=row["result_status"],
            error_message=row["error_message"],
            created_at=datetime.fromisoformat(row["created_at"])
            if row["created_at"]
            else datetime.utcnow(),
        )
        for row in rows
    ]

    # Get daily statistics for the last 30 days
    daily_stats = await get_daily_stats(db, days=30)

    return AdminStatsResponse(
        user_stats=user_stats,
        download_stats=download_stats,
        recent_activity=recent_activity,
        daily_stats=daily_stats,
        platform_breakdown=bot_stats.get("by_platform", {}),
        media_breakdown=detailed_stats.get("by_media_type", {}),
    )


async def get_daily_stats(db: aiosqlite.Connection, days: int = 30) -> list[DailyStats]:
    """Get daily statistics for the last N days."""
    cursor = await db.execute(
        """SELECT
            date(created_at) as stat_date,
            COUNT(*) as downloads,
            AVG(CASE WHEN result_status = 'success' THEN 1 ELSE 0 END) as success_rate
            FROM history
            WHERE created_at >= datetime('now', ?)
            GROUP BY date(created_at)
            ORDER BY stat_date DESC
            LIMIT ?""",
        (f"-{days} days", days),
    )
    rows = await cursor.fetchall()

    # Get new users per day
    daily_stats = []
    for row in rows:
        stat_date = datetime.strptime(row["stat_date"], "%Y-%m-%d").date()

        # Count favorites for that day
        cursor2 = await db.execute(
            "SELECT COUNT(*) as count FROM favorites WHERE date(created_at) = ?",
            (row["stat_date"],),
        )
        fav_row = await cursor2.fetchone()
        favorites_count = fav_row["count"] if fav_row else 0

        # Count new users
        cursor3 = await db.execute(
            "SELECT COUNT(*) as count FROM users WHERE date(created_at) = ?",
            (row["stat_date"],),
        )
        user_row = await cursor3.fetchone()
        new_users = user_row["count"] if user_row else 0

        daily_stats.append(
            DailyStats(
                date=stat_date,
                downloads=row["downloads"],
                favorites=favorites_count,
                new_users=new_users,
                active_users=row["downloads"],  # Use downloads as proxy
            )
        )

    return daily_stats