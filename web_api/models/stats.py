"""Statistics models for the web API."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database: str = Field(..., description="Database connection status")


class BotStatusResponse(BaseModel):
    """Bot status response (public)."""

    status: str = Field(..., description="Overall bot status")
    ai_available: bool = Field(..., description="AI service availability")
    database_connected: bool = Field(..., description="Database connection status")
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class PlatformStat(BaseModel):
    """Single platform statistics."""

    platform: str
    count: int


class MediaStat(BaseModel):
    """Single media type statistics."""

    media_type: str
    count: int


class UserStats(BaseModel):
    """User statistics model."""

    total_users: int = Field(..., description="Total number of users")
    new_users_today: int = Field(..., description="New users today")
    active_users: int = Field(..., description="Active users")
    average_processed_per_user: float = Field(..., description="Average processed per user")


class DownloadStats(BaseModel):
    """Download statistics model."""

    total_downloads: int = Field(..., description="Total downloads")
    downloads_today: int = Field(..., description="Downloads today")
    downloads_by_status: dict[str, int] = Field(..., description="Downloads by status")
    downloads_by_platform: dict[str, int] = Field(..., description="Downloads by platform")


class ActivityEntry(BaseModel):
    """Single activity entry."""

    id: int
    user_id: int
    action_type: str
    platform: Optional[str] = None
    original_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    result_status: str = "success"
    error_message: Optional[str] = None
    created_at: datetime


class DailyStats(BaseModel):
    """Daily statistics model."""

    date: date
    downloads: int
    favorites: int
    new_users: int
    active_users: int


class PublicStatsResponse(BaseModel):
    """Public statistics response (anonymized)."""

    total_users: int = Field(..., description="Total number of users")
    active_users_24h: int = Field(..., description="Users active in last 24 hours")
    active_users_7d: int = Field(..., description="Users active in last 7 days")
    total_processed: int = Field(..., description="Total downloads/processed files")
    total_history: int = Field(..., description="Total history entries")
    total_favorites: int = Field(..., description="Total favorites")
    platform_stats: list[PlatformStat] = Field(
        default_factory=list, description="Downloads by platform"
    )
    media_stats: list[MediaStat] = Field(
        default_factory=list, description="Downloads by media type"
    )
    first_user_registered: Optional[datetime] = Field(
        None, description="Date of first user registration"
    )


class AdminStatsResponse(BaseModel):
    """Admin statistics response."""

    user_stats: UserStats
    download_stats: DownloadStats
    recent_activity: list[ActivityEntry]
    daily_stats: list[DailyStats]
    platform_breakdown: dict[str, int]
    media_breakdown: dict[str, int]
    generated_at: datetime = Field(default_factory=datetime.utcnow)