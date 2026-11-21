"""Activity endpoints for the web API."""

import logging
from datetime import datetime, timedelta
from typing import Optional

import aiosqlite
from fastapi import APIRouter, Depends, Query, Path

from web_api.api.deps import get_db_dependency, get_current_api_user
from web_api.models.stats import ActivityEntry

from database.repositories.history import HistoryRepository

logger = logging.getLogger(__name__)

activity_router = APIRouter()


def convert_history_to_entry(row: aiosqlite.Row) -> ActivityEntry:
    """Convert a history row to an ActivityEntry."""
    return ActivityEntry(
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


@activity_router.get(
    "/activity",
    response_model=list[ActivityEntry],
    summary="Recent activity",
    description="Get recent activity entries (requires API key)",
    tags=["Admin"],
)
async def recent_activity(
    limit: int = Query(50, ge=1, le=100, description="Number of entries to return"),
    hours: Optional[int] = Query(
        None, ge=1, description="Filter to entries from last N hours"
    ),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    api_user: dict = Depends(get_current_api_user),
    db: aiosqlite.Connection = Depends(get_db_dependency),
) -> list[ActivityEntry]:
    """
    Recent activity endpoint - requires API key authentication.
    Returns recent history/activity entries with optional filtering.
    """
    history_repo = HistoryRepository(db)

    # Build query with optional filters
    where_clauses = []
    params = []

    if hours is not None:
        where_clauses.append("created_at >= datetime('now', ?)")
        params.append(f"-{hours} hours")

    if platform is not None:
        where_clauses.append("platform = ?")
        params.append(platform)

    where_clause = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    query = f"""
        SELECT * FROM history
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ?
    """

    params.append(limit)

    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()

    return [convert_history_to_entry(row) for row in rows]


@activity_router.get(
    "/activity/user/{user_id}",
    response_model=list[ActivityEntry],
    summary="User activity",
    description="Get activity entries for a specific user (requires API key)",
    tags=["Admin"],
)
async def user_activity(
    user_id: int = Path(..., ge=1, description="User ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of entries to return"),
    api_user: dict = Depends(get_current_api_user),
    db: aiosqlite.Connection = Depends(get_db_dependency),
) -> list[ActivityEntry]:
    """
    User activity endpoint - requires API key authentication.
    Returns activity entries for a specific user.
    """
    history_repo = HistoryRepository(db)

    history = await history_repo.get_user_history(user_id=user_id, page=0, limit=limit)

    return [
        ActivityEntry(
            id=h["id"],
            user_id=h["user_id"],
            action_type=h["action_type"],
            platform=h["platform"],
            original_url=h["original_url"],
            file_name=h["file_name"],
            file_size=h["file_size"],
            result_status=h["result_status"],
            error_message=h["error_message"],
            created_at=datetime.fromisoformat(h["created_at"])
            if h["created_at"]
            else datetime.utcnow(),
        )
        for h in history
    ]


@activity_router.get(
    "/activity/errors",
    response_model=list[ActivityEntry],
    summary="Error entries",
    description="Get activity entries with errors (requires API key)",
    tags=["Admin"],
)
async def error_activity(
    limit: int = Query(50, ge=1, le=100, description="Number of entries to return"),
    api_user: dict = Depends(get_current_api_user),
    db: aiosqlite.Connection = Depends(get_db_dependency),
) -> list[ActivityEntry]:
    """
    Error activity endpoint - requires API key authentication.
    Returns activity entries that contain errors.
    """
    query = """
        SELECT * FROM history
        WHERE result_status != 'success' OR error_message IS NOT NULL
        ORDER BY created_at DESC
        LIMIT ?
    """

    cursor = await db.execute(query, (limit,))
    rows = await cursor.fetchall()

    return [convert_history_to_entry(row) for row in rows]


@activity_router.get(
    "/activity/daily",
    summary="Daily statistics",
    description="Get daily activity statistics (requires API key)",
    tags=["Admin"],
)
async def daily_statistics(
    days: int = Query(30, ge=1, le=90, description="Number of days to include"),
    api_user: dict = Depends(get_current_api_user),
    db: aiosqlite.Connection = Depends(get_db_dependency),
) -> dict:
    """
    Daily statistics endpoint - requires API key authentication.
    Returns activity grouped by day.
    """
    query = """
        SELECT
            DATE(created_at) as day,
            COUNT(*) as count,
            SUM(CASE WHEN result_status = 'success' THEN 1 ELSE 0 END) as success_count,
            SUM(CASE WHEN result_status != 'success' THEN 1 ELSE 0 END) as error_count
        FROM history
        WHERE created_at >= datetime('now', ?)
        GROUP BY DATE(created_at)
        ORDER BY day DESC
    """

    cursor = await db.execute(query, (f"-{days} days",))
    rows = await cursor.fetchall()

    daily_data = [
        {
            "date": row["day"],
            "total": row["count"],
            "success": row["success_count"],
            "errors": row["error_count"],
        }
        for row in rows
    ]

    return {"daily": daily_data, "start_date": (datetime.utcnow() - timedelta(days=days)).isoformat(), "end_date": datetime.utcnow().isoformat()}