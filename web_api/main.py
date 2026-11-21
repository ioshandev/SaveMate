#!/usr/bin/env python3
"""SaveMate Web API - FastAPI application entry point."""

import os
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

import aiosqlite
from fastapi import FastAPI, Depends, HTTPException, Query, Request, status as http_status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from database.db import get_db, close_db, init_db
from database.repositories.stats import StatsRepository
from database.repositories.users import UserRepository
from database.repositories.history import HistoryRepository
from core.config import web_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


# Rate limiting storage (simple in-memory)
class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = {}
        self._lock = None

    def check(self, client_id: str) -> tuple[bool, float]:
        """Check if request is allowed. Returns (allowed, retry_after)."""
        now = time.time()

        if client_id not in self._requests:
            self._requests[client_id] = []

        # Clean old requests
        self._requests[client_id] = [
            t for t in self._requests[client_id]
            if now - t < self.window_seconds
        ]

        if len(self._requests[client_id]) >= self.max_requests:
            retry_after = self.window_seconds - (now - self._requests[client_id][0])
            return False, retry_after

        self._requests[client_id].append(now)
        return True, 0


rate_limiter = RateLimiter(
    web_config.rate_limit_requests,
    web_config.rate_limit_window,
)


# Pydantic Models for API responses
class UserStats(BaseModel):
    """User statistics model."""
    id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: str = "en"
    registered_at: datetime
    total_processed: int = 0
    notifications_enabled: bool = True
    history_count: int = 0
    favorites_count: int = 0


class UserList(BaseModel):
    """Paginated user list."""
    users: List[UserStats]
    total: int
    page: int
    limit: int


class DailyStats(BaseModel):
    """Daily statistics model."""
    date: str
    user_count: int
    processed_count: int
    history_count: int
    favorites_count: int


class PlatformStats(BaseModel):
    """Platform statistics model."""
    platform: str
    count: int


class DetailedStats(BaseModel):
    """Detailed bot statistics."""
    total_users: int = 0
    active_users_24h: int = 0
    active_users_7d: int = 0
    total_processed: int = 0
    total_history: int = 0
    total_favorites: int = 0
    by_platform: Dict[str, int] = Field(default_factory=dict)
    by_media_type: Dict[str, int] = Field(default_factory=dict)


class RecentActivity(BaseModel):
    """Recent activity entry."""
    id: int
    user_id: int
    username: Optional[str] = None
    action_type: str
    platform: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    result_status: str
    error_message: Optional[str] = None
    created_at: datetime


class HistoryEntry(BaseModel):
    """Single history entry."""
    id: int
    user_id: int
    action_type: str
    platform: Optional[str]
    original_url: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    media_type: Optional[str]
    thumbnail_url: Optional[str]
    result_status: str
    error_message: Optional[str]
    created_at: datetime


class SystemStatus(BaseModel):
    """System status response."""
    status: str
    database: str
    api_key_configured: bool
    checked_at: datetime


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str = "1.0.0"


# Authentication
bearer_scheme = HTTPBearer(auto_error=False)


async def verify_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> bool:
    """Verify API key from Authorization header."""
    if not web_config.is_configured:
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication not configured",
        )

    if not credentials:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    if token != web_config.api_key:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True


def get_db_connection() -> aiosqlite.Connection:
    """Get database connection."""
    return get_db()


def get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance."""
    return rate_limiter


# FastAPI App
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting SaveMate Web API...")

    # Initialize database
    original_config = None

    await init_db()
    logger.info("Database initialized")

    # Override config database path for web if needed
    from database import db as db_module
    if os.getenv("DATABASE_PATH") or os.getenv("WEB_API_DB_PATH"):
        original_config = db_module.config
        from config import Config as BotConfig
        new_config = BotConfig(
            bot_token=os.getenv("BOT_TOKEN", ""),
            admin_ids=[],
            ai_api_key=os.getenv("AI_API_KEY", "") or None,
            ai_base_url=os.getenv("AI_BASE_URL", "https://api.openai.com/v1"),
            ai_model=os.getenv("AI_MODEL", "gpt-4o-mini"),
            database_path=web_config.database_path,
            max_file_size=int(os.getenv("MAX_FILE_SIZE", "52428800")),
            max_download_size=int(os.getenv("MAX_DOWNLOAD_SIZE", "104857600")),
            rate_limit_messages=int(os.getenv("RATE_LIMIT_MESSAGES", "30")),
            rate_limit_window=int(os.getenv("RATE_LIMIT_WINDOW", "60")),
            temp_file_ttl=int(os.getenv("TEMP_FILE_TTL", "3600")),
            default_language=os.getenv("DEFAULT_LANGUAGE", "en"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
        db_module.config = new_config

    yield

    logger.info("Shutting down SaveMate Web API...")

    # Restore original config if we changed it
    if original_config:
        db_module.config = original_config

    await close_db()
    logger.info("Database closed")


app = FastAPI(
    title="SaveMate Web API",
    description="Web API for SaveMate Telegram Bot Admin Dashboard",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=web_config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Public"])
async def health_check():
    """Health check endpoint - no authentication required."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
    )


@app.get("/bot-status", response_model=SystemStatus, tags=["Public"])
async def bot_status():
    """Get bot status - public endpoint."""
    db = await get_db()
    try:
        # Check database connectivity
        cursor = await db.execute("SELECT 1")
        await cursor.fetchone()
        db_status = "connected"
    except Exception as e:
        logger.error("Database status check failed: %s", e)
        db_status = "disconnected"
    finally:
        await close_db(db)

    return SystemStatus(
        status="operational" if db_status == "connected" else "degraded",
        database=db_status,
        api_key_configured=web_config.is_configured,
        checked_at=datetime.utcnow(),
    )


# Protected API Endpoints
@app.get("/stats", response_model=DetailedStats, summary="Get detailed bot statistics", tags=["Admin"])
async def get_detailed_stats(
    verified: bool = Depends(verify_api_key),
):
    """Get detailed bot statistics (admin only)."""
    db = await get_db()
    try:
        repo = StatsRepository(db)
        stats = await repo.get_detailed_stats()

        return DetailedStats(
            total_users=stats.get("total_users", 0),
            active_users_24h=stats.get("active_users_24h", 0),
            active_users_7d=stats.get("active_users_7d", 0),
            total_processed=stats.get("total_processed", 0),
            total_history=stats.get("total_history", 0),
            total_favorites=stats.get("total_favorites", 0),
            by_platform=stats.get("by_platform", {}),
            by_media_type=stats.get("by_media_type", {}),
        )
    finally:
        await close_db(db)


@app.get("/users", response_model=UserList, summary="Get paginated list of users", tags=["Admin"])
async def get_users(
    page: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    verified: bool = Depends(verify_api_key),
):
    """Get paginated list of users (admin only)."""
    db = await get_db()
    try:
        repo = UserRepository(db)
        users = await repo.get_all_users(page=page, limit=limit)
        total = await repo.get_total_users_count()

        user_repos = UserRepository(db)
        user_stats = []
        for u in users:
            # Get additional stats for each user
            u_stats = await user_repos.get_user_stats(u.id) if u else {"history_count": 0, "favorites_count": 0}
            user_stats.append(UserStats(
                id=u.id,
                username=u.username,
                first_name=u.first_name,
                last_name=u.last_name,
                language=u.language,
                registered_at=u.registered_at,
                total_processed=u.total_processed,
                notifications_enabled=u.notifications_enabled,
                history_count=u_stats.get("history_count", 0),
                favorites_count=u_stats.get("favorites_count", 0),
            ))

        return UserList(
            users=user_stats,
            total=total,
            page=page,
            limit=limit,
        )
    finally:
        await close_db(db)


@app.get("/users/{user_id}", response_model=UserStats, summary="Get user by ID", tags=["Admin"])
async def get_user(
    user_id: int,
    verified: bool = Depends(verify_api_key),
):
    """Get user details by ID (admin only)."""
    db = await get_db()
    try:
        user_repo = UserRepository(db)
        user = await user_repo.get_user(user_id)
        stats = await user_repo.get_user_stats(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserStats(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language=user.language,
            registered_at=user.registered_at,
            total_processed=user.total_processed,
            notifications_enabled=user.notifications_enabled,
            history_count=stats.get("history_count", 0),
            favorites_count=stats.get("favorites_count", 0),
        )
    finally:
        await close_db(db)


@app.get("/activity", response_model=List[RecentActivity], summary="Get recent activity", tags=["Admin"])
async def get_recent_activity(
    limit: int = Query(100, ge=1, le=500),
    hours: int = Query(24, ge=1, le=168),
    verified: bool = Depends(verify_api_key),
):
    """Get recent activity (admin only)."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT h.*, u.username
               FROM history h
               LEFT JOIN users u ON h.user_id = u.id
               WHERE h.created_at >= datetime('now', ?)
               ORDER BY h.created_at DESC
               LIMIT ?""",
            (f"-{hours} hours", limit)
        )
        rows = await cursor.fetchall()

        activities = []
        for row in rows:
            activities.append(RecentActivity(
                id=row["id"],
                user_id=row["user_id"],
                username=row["username"],
                action_type=row["action_type"],
                platform=row["platform"],
                file_name=row["file_name"],
                file_size=row["file_size"],
                result_status=row["result_status"],
                error_message=row["error_message"],
                created_at=datetime.fromisoformat(row["created_at"]) if isinstance(row["created_at"], str) else row["created_at"],
            ))

        return activities
    finally:
        await close_db(db)


@app.get("/history", response_model=List[HistoryEntry], summary="Get history entries", tags=["Admin"])
async def get_history(
    user_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    verified: bool = Depends(verify_api_key),
):
    """Get history entries (admin only)."""
    db = await get_db()
    try:
        if user_id:
            repo = HistoryRepository(db)
            entries = await repo.get_user_history(user_id=user_id, page=offset // limit, limit=limit)
        else:
            cursor = await db.execute(
                """SELECT * FROM history
                   ORDER BY created_at DESC
                   LIMIT ? OFFSET ?""",
                (limit, offset)
            )
            rows = await cursor.fetchall()
            entries = [
                {
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "action_type": row["action_type"],
                    "platform": row["platform"],
                    "original_url": row["original_url"],
                    "file_name": row["file_name"],
                    "file_size": row["file_size"],
                    "media_type": row.get("media_type"),
                    "thumbnail_url": row.get("thumbnail_url"),
                    "result_status": row["result_status"],
                    "error_message": row["error_message"],
                    "created_at": row["created_at"],
                }
                for row in rows
            ]

        history_entries = []
        for entry in entries:
            history_entries.append(HistoryEntry(
                id=entry["id"],
                user_id=entry["user_id"],
                action_type=entry["action_type"],
                platform=entry.get("platform"),
                original_url=entry.get("original_url"),
                file_name=entry.get("file_name"),
                file_size=entry.get("file_size"),
                media_type=entry.get("media_type"),
                thumbnail_url=entry.get("thumbnail_url"),
                result_status=entry["result_status"],
                error_message=entry.get("error_message"),
                created_at=datetime.fromisoformat(entry["created_at"]) if isinstance(entry.get("created_at"), str) else entry.get("created_at") or datetime.utcnow(),
            ))

        return history_entries
    finally:
        await close_db(db)


@app.get("/daily-stats", response_model=List[DailyStats], summary="Get daily statistics", tags=["Admin"])
async def get_daily_stats(
    days: int = Query(30, ge=1, le=365),
    verified: bool = Depends(verify_api_key),
):
    """Get daily statistics for the last N days (admin only)."""
    db = await get_db()
    try:
        # Get user counts per day
        cursor = await db.execute(
            f"""SELECT DATE(created_at) as day, COUNT(*) as count
                FROM users
                WHERE created_at >= datetime('now', '-{days} days')
                GROUP BY DATE(created_at)
                ORDER BY day"""
        )
        user_rows = {row["day"]: row["count"] for row in await cursor.fetchall()}

        # Get processed counts per day from history
        cursor = await db.execute(
            f"""SELECT DATE(created_at) as day, COUNT(*) as count
                FROM history
                WHERE created_at >= datetime('now', '-{days} days')
                GROUP BY DATE(created_at)
                ORDER BY day"""
        )
        history_rows = {row["day"]: row["count"] for row in await cursor.fetchall()}

        # Get favorites counts per day
        cursor = await db.execute(
            f"""SELECT DATE(created_at) as day, COUNT(*) as count
                FROM favorites
                WHERE created_at >= datetime('now', '-{days} days')
                GROUP BY DATE(created_at)
                ORDER BY day"""
        )
        favorites_rows = {row["day"]: row["count"] for row in await cursor.fetchall()}

        # Build daily stats
        daily_stats = []
        today = datetime.utcnow().date()
        for i in range(days):
            date = today - timedelta(days=days - 1 - i)
            date_str = date.isoformat()
            daily_stats.append(DailyStats(
                date=date_str,
                user_count=user_rows.get(date_str, 0),
                processed_count=history_rows.get(date_str, 0),
                history_count=history_rows.get(date_str, 0),
                favorites_count=favorites_rows.get(date_str, 0),
            ))

        return daily_stats
    finally:
        await close_db(db)


@app.get("/platforms", response_model=List[PlatformStats], summary="Get platform statistics", tags=["Admin"])
async def get_platform_stats(
    verified: bool = Depends(verify_api_key),
):
    """Get statistics by platform (admin only)."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT platform, COUNT(*) as count FROM history WHERE platform IS NOT NULL GROUP BY platform ORDER BY count DESC LIMIT 20"
        )
        rows = await cursor.fetchall()

        return [
            PlatformStats(platform=row["platform"], count=row["count"])
            for row in rows
        ]
    finally:
        await close_db(db)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_api.main:app", host="0.0.0.0", port=8080, reload=True)