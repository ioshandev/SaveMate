"""User models for the web API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """User response model."""

    id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: str = "en"
    registered_at: datetime
    total_processed: int = 0
    notifications_enabled: bool = True
    last_activity: Optional[datetime] = None


class UserStatsResponse(BaseModel):
    """User statistics response model."""

    id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    language: str = "en"
    registered_at: datetime
    total_processed: int
    history_count: int = 0
    favorites_count: int = 0
    last_activity: Optional[datetime] = None


class UserList(BaseModel):
    """Paginated user list."""

    users: list[UserResponse]
    total: int
    page: int
    limit: int
    has_next: bool