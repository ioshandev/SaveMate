import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from core.rate_limit import rate_limit_middleware

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    """
    Rate limiting middleware using sliding window algorithm.
    Applies different limits based on action type.
    """

    # Default limits per action (requests per window)
    ACTION_LIMITS: Dict[str, Dict[str, int]] = {
        "default": {"limit": 30, "window": 60},
        "media_download": {"limit": 10, "window": 60},
        "media_process": {"limit": 5, "window": 60},
        "ai_chat": {"limit": 20, "window": 60},
        "history": {"limit": 30, "window": 60},
        "favorites": {"limit": 30, "window": 60},
        "settings": {"limit": 30, "window": 60},
        "admin": {"limit": 100, "window": 60},
    }

    def __init__(self):
        super().__init__()

    def _get_action_from_event(self, event: TelegramObject) -> str:
        """Determine action type from event."""
        if isinstance(event, CallbackQuery):
            data = event.data or ""
            if data.startswith('{"a":"'):
                import json
                try:
                    parsed = json.loads(data)
                    action = parsed.get("a", "")
                    # Map callback actions to rate limit actions
                    if action in ("download", "media_action"):
                        return "media_download"
                    elif action in ("convert", "compress", "extract", "select_tool"):
                        return "media_process"
                    elif action in ("chat", "clear_context", "cancel"):
                        return "ai_chat"
                    elif action in ("history", "clear", "confirm_clear", "cancel_clear"):
                        return "history"
                    elif action in ("favorites", "remove", "list", "view"):
                        return "favorites"
                    elif action in ("setting", "language", "notifications", "delete_data"):
                        return "settings"
                    elif action in ("admin", "stats", "users", "broadcast", "status"):
                        return "admin"
                except json.JSONDecodeError:
                    pass
        elif isinstance(event, Message):
            # Check for commands
            if event.text and event.text.startswith("/"):
                cmd = event.text.split()[0].lower()
                if cmd in ("/start", "/help", "/settings", "/history", "/favorites"):
                    return "default"
                elif cmd in ("/admin", "/stats", "/broadcast", "/users"):
                    return "admin"
        return "default"

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Get user ID
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None

        if user_id is None:
            return await handler(event, data)

        # Determine action and limits
        action = self._get_action_from_event(event)
        limits = self.ACTION_LIMITS.get(action, self.ACTION_LIMITS["default"])
        limit = limits["limit"]
        window = limits["window"]

        # Check rate limit
        allowed, retry_after = await rate_limit_middleware(
            user_id=user_id,
            action=action,
            limit=limit,
            window=window,
        )

        if not allowed:
            # Rate limited - notify user
            wait_time = int(retry_after) + 1
            if isinstance(event, CallbackQuery):
                await event.answer(
                    f"⏳ Rate limited. Please wait {wait_time} seconds.",
                    show_alert=True
                )
            elif isinstance(event, Message):
                await event.reply(
                    f"⏳ Rate limited. Please wait {wait_time} seconds before trying again."
                )
            logger.warning("Rate limited user %d for action %s", user_id, action)
            return

        # Add rate limit info to data for handler access
        data["rate_limit_action"] = action
        data["rate_limit_remaining"] = await rate_limiter.get_remaining(user_id, action)

        return await handler(event, data)


# Global rate limiter reference (avoid circular import)
from core.rate_limit import rate_limiter