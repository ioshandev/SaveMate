import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, User as TgUser

from database.repositories.users import UserRepository

logger = logging.getLogger(__name__)


class UserMiddleware(BaseMiddleware):
    """
    Middleware to handle user registration and settings.
    - Auto-registers new users
    - Provides user language to handlers
    - Updates last_activity timestamp
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Extract Telegram user
        tg_user: TgUser | None = None
        if isinstance(event, Message):
            tg_user = event.from_user
        elif isinstance(event, CallbackQuery):
            tg_user = event.from_user

        if tg_user is None:
            return await handler(event, data)

        # Get database from data (injected by DatabaseMiddleware)
        db = data.get("db")
        if db is None:
            logger.warning("Database not available in UserMiddleware")
            return await handler(event, data)

        # Get or create user
        user_repo = UserRepository(db)
        user = await user_repo.get_or_create(
            user_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
            language_code=tg_user.language_code,
        )

        # Update last activity
        await user_repo.update_last_activity(tg_user.id)

        # Add user and language to handler data
        data["user"] = user
        data["lang"] = user.language

        return await handler(event, data)