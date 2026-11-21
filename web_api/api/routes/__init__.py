"""Web API routes module."""

from web_api.api.routes.health import health_router
from web_api.api.routes.stats import stats_router
from web_api.api.routes.users import users_router
from web_api.api.routes.activity import activity_router

__all__ = ["health_router", "stats_router", "users_router", "activity_router"]