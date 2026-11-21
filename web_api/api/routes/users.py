"""User endpoints for the web API."""

import logging
from datetime import datetime
from typing import Optional

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Query, Path

from web_api.api.deps import get_db_dependency, get_current_api_user
from web_api.models.users import UserResponse, UserStatsResponse, UserList

from database.repositories.users import UserRepository

logger = logging.getLogger(__name__)

users_router = APIRouter()


def convert_user_to_response(user) -> UserResponse:
    """Convert a User dataclass to a Pydantic response model."""
    return UserResponse(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language=user.language,
        registered_at=(
            user.registered_at
            if isinstance(user.registered_at, datetime)
            else datetime.fromisoformat(user.registered_at)
        ),
        total_processed=user.total_processed,
        notifications_enabled=user.notifications_enabled,
        last_activity=(
            user.last_activity
            if user.last_activity is None
            or isinstance(user.last_activity, datetime)
            else datetime.fromisoformat(user.last_activity)
            if user.last_activity
            else None
        ),
    )


@users_router.get(
    "/users",
    response_model=UserList,
    summary="List users",
    description="Get a paginated list of users (requires API key)",
    tags=["Admin"],
)
async def list_users(
    page: int = Query(0, ge=0, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    api_user: dict = Depends(get_current_api_user),
    db: aiosqlite.Connection = Depends(get_db_dependency),
) -> UserList:
    """
    List users endpoint - requires API key authentication.
    Returns a paginated list of users with basic information.
    """
    user_repo = UserRepository(db)

    users = await user_repo.get_all_users(page=page, limit=limit)
    total = await user_repo.get_total_users_count()

    return UserList(
        users=[convert_user_to_response(u) for u in users],
        total=total,
        page=page,
        limit=limit,
        has_next=(page + 1) * limit < total,
    )


@users_router.get(
    "/users/{user_id}",
    response_model=UserStatsResponse,
    summary="Get user stats",
    description="Get detailed statistics for a specific user (requires API key)",
    tags=["Admin"],
)
async def get_user(
    user_id: int = Path(..., ge=1, description="User ID"),
    api_user: dict = Depends(get_current_api_user),
    db: aiosqlite.Connection = Depends(get_db_dependency),
) -> UserStatsResponse:
    """
    Get user stats endpoint - requires API key authentication.
    Returns detailed statistics for a specific user.
    """
    user_repo = UserRepository(db)
    stats_repo = UserRepository(db)

    user = await user_repo.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_stats = await stats_repo.get_user_stats(user_id)

    return UserStatsResponse(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        language=user.language,
        registered_at=(
            user.registered_at
            if isinstance(user.registered_at, datetime)
            else datetime.fromisoformat(user.registered_at)
        ),
        total_processed=user.total_processed,
        history_count=user_stats.get("history_count", 0),
        favorites_count=user_stats.get("favorites_count", 0),
        last_activity=(
            user.last_activity
            if user.last_activity is None
            or isinstance(user.last_activity, datetime)
            else datetime.fromisoformat(user.last_activity)
            if user.last_activity
            else None
        ),
    )


@users_router.get(
    "/user/search",
    response_model=list[UserResponse],
    summary="Search users",
    description="Search users by username (requires API key)",
    tags=["Admin"],
)
async def search_users(
    query: str = Query(..., min_length=1, max_length=100, description="Search query"),
    api_user: dict = Depends(get_current_api_user),
    db: aiosqlite.Connection = Depends(get_db_dependency),
) -> list[UserResponse]:
    """
    Search users endpoint - requires API key authentication.
    Returns users matching the search query.
    """
    user_repo = UserRepository(db)

    # Get all users and filter (simple approach for SQLite)
    users = await user_repo.get_all_users(page=0, limit=1000)

    matching_users = [
        u
        for u in users
        if u.username and query.lower() in u.username.lower()
    ]

    return [convert_user_to_response(u) for u in matching_users]