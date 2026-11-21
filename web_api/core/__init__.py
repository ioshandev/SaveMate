"""Web API core module."""

from web_api.core.config import config, WebConfig
from web_api.core.auth import (
    verify_api_key,
    get_current_api_user,
    APIKeyHeader,
)

__all__ = [
    "config",
    "WebConfig",
    "verify_api_key",
    "get_current_api_user",
    "APIKeyHeader",
]