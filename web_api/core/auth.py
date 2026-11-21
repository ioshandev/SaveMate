"""API key authentication for web routes."""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from web_api.core.config import config

logger = logging.getLogger(__name__)

# API key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyAuthError(HTTPException):
    """Exception for API key authentication errors."""

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "ApiKey"},
        )


def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Verify the API key from the request header.

    Args:
        api_key: The API key from the X-API-Key header.

    Returns:
        The verified API key (for potential logging/auditing).

    Raises:
        APIKeyAuthError: If the API key is missing or invalid.
    """
    if not api_key:
        logger.warning("API key not provided in request")
        raise APIKeyAuthError("API key not provided. Send X-API-Key header.")

    if api_key != config.api_key:
        logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
        raise APIKeyAuthError("Invalid API key.")

    return api_key


async def get_current_api_user(
    api_key: str = Depends(verify_api_key),
) -> dict:
    """
    Get the current authenticated API user.

    Since this is an API key-based authentication,
    we return a simple user object with the API key as identity.

    Args:
        api_key: The verified API key.

    Returns:
        A dictionary representing the API user.
    """
    return {
        "auth_type": "api_key",
        "id": "api",
        "api_key_hash": api_key[:8] + "..." if len(api_key) > 8 else "***",
    }