"""Dependencies for web API routes."""

import logging
import time
from collections import defaultdict
from typing import AsyncGenerator, Dict, List

import aiosqlite
from fastapi import Depends, HTTPException, Request, status as http_status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from web_api.core.config import config
from database.db import get_db, close_db

logger = logging.getLogger(__name__)

# API key security scheme for protected routes
bearer_scheme = HTTPBearer(auto_error=False)

# Rate limiter storage
_rate_limit_storage: Dict[str, List[float]] = defaultdict(list)


async def get_db_dependency() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Dependency that provides a database connection."""
    db = await get_db()
    try:
        yield db
    finally:
        await close_db(db)


def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> bool:
    """
    Verify API key from Authorization header.

    Args:
        credentials: The Bearer token from the Authorization header.

    Returns:
        True if authentication is successful.

    Raises:
        HTTPException: If authentication fails.
    """
    if not config.api_key:
        logger.warning("WEB_API_KEY not configured")
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
    if token != config.api_key:
        logger.warning("Invalid API key attempt")
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True


def get_current_api_user(
    verified: bool = Depends(verify_api_key),
) -> dict:
    """
    Get the current authenticated API user.

    Since this is an API key-based authentication,
    we return a simple user object with the API key as identity.

    Args:
        verified: Whether the API key has been verified.

    Returns:
        A dictionary representing the API user.
    """
    return {
        "auth_type": "api_key",
        "id": "api",
    }


async def check_rate_limit(
    request: Request,
) -> None:
    """
    Middleware-style rate limiting for API requests.
    Uses in-memory rate limiting based on client IP.
    """
    global _rate_limit_storage

    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()
    window = config.rate_limit_window

    # Clean old requests
    _rate_limit_storage[client_ip] = [
        t for t in _rate_limit_storage[client_ip]
        if current_time - t < window
    ]

    requests_in_window = len(_rate_limit_storage[client_ip])

    if requests_in_window >= config.rate_limit_requests:
        raise HTTPException(
            status_code=http_status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {window - (current_time - _rate_limit_storage[client_ip][0]):.0f} seconds.",
        )

    # Record this request
    _rate_limit_storage[client_ip].append(current_time)