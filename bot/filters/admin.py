import logging
from typing import Any, Dict, Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from config import config

logger = logging.getLogger(__name__)


class IsAdmin(BaseFilter):
    """
    Filter to check if user is an admin.
    Checks against ADMIN_IDS from config.
    """

    def __init__(self) -> None:
        self.admin_ids = config.admin_ids

    async def __call__(
        self,
        event: Union[Message, CallbackQuery],
        **kwargs: Any
    ) -> bool:
        user_id = event.from_user.id if event.from_user else None
        if user_id is None:
            return False

        is_admin = user_id in self.admin_ids
        if is_admin:
            logger.debug("Admin access granted for user %d", user_id)
        else:
            logger.debug("Admin access denied for user %d", user_id)
        return is_admin


# Alias for convenience
AdminFilter = IsAdmin