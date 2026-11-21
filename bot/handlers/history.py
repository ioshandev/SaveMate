import logging
from typing import Any, Dict

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from utils.texts import get_text
from bot.keyboards.inline import (
    get_history_keyboard,
    get_history_clear_confirm_keyboard,
    get_back_keyboard,
)
from bot.keyboards.callbacks import HistoryCallback, PaginationCallback, MainMenuCallback
from database.repositories.history import HistoryRepository

logger = logging.getLogger(__name__)

router = Router(name="history")

ITEMS_PER_PAGE = 10


@router.callback_query(MainMenuCallback.filter(F.section == "history"))
async def cb_history(callback: CallbackQuery, db: Any, user: Any, lang: str, **kwargs) -> None:
    """Show history first page."""
    await show_history_page(callback, db, user, page=0, lang=lang)


@router.callback_query(PaginationCallback.filter(F.context == "history"))
async def cb_history_pagination(
    callback: CallbackQuery,
    callback_data: PaginationCallback,
    db: Any,
    user: Any,
    lang: str,
    **kwargs
) -> None:
    """Handle history pagination."""
    await show_history_page(callback, db, user, page=callback_data.page, lang=lang)


async def show_history_page(
    callback: CallbackQuery,
    db: Any,
    user: Any,
    page: int,
    lang: str
) -> None:
    """Show history page."""
    history_repo = HistoryRepository(db)
    items = await history_repo.get_user_history(user.id, page=page, limit=ITEMS_PER_PAGE)
    total = await history_repo.get_user_history_count(user.id)

    has_next = (page + 1) * ITEMS_PER_PAGE < total

    if not items:
        text = get_text("history_empty", lang)
        keyboard = get_back_keyboard("main", lang)
    else:
        text = format_history_page(items, page, total, lang)
        keyboard = get_history_keyboard(page, has_next, total, lang)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


def format_history_page(items: list, page: int, total: int, lang: str) -> str:
    """Format history page for display."""
    lines = [f"<b>{get_text('history_title', lang)}</b> (Page {page + 1}, Total: {total})\n"]

    for i, item in enumerate(items, start=page * ITEMS_PER_PAGE + 1):
        platform = item.get("platform", "unknown").title()
        title = item.get("title", "Untitled")[:50]
        media_type = item.get("media_type", "unknown")
        created_at = item.get("created_at", "")

        lines.append(
            f"{i}. <b>{platform}</b> | {title} | {media_type} | {created_at}"
        )

    return "\n".join(lines)


@router.callback_query(HistoryCallback.filter(F.action == "clear"))
async def cb_history_clear(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Show history clear confirmation."""
    text = get_text("confirm_clear_history", lang)
    keyboard = get_history_clear_confirm_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(HistoryCallback.filter(F.action == "confirm_clear"))
async def cb_history_confirm_clear(callback: CallbackQuery, db: Any, user: Any, lang: str, **kwargs) -> None:
    """Confirm clear history."""
    history_repo = HistoryRepository(db)
    await history_repo.clear_user_history(user.id)
    await callback.answer(get_text("history_cleared", lang), show_alert=True)

    # Refresh history view
    await show_history_page(callback, db, user, page=0, lang=lang)


@router.callback_query(HistoryCallback.filter(F.action == "cancel_clear"))
async def cb_history_cancel_clear(callback: CallbackQuery, db: Any, user: Any, lang: str, **kwargs) -> None:
    """Cancel clear history."""
    await callback.answer(get_text("cancelled", lang), show_alert=True)
    await show_history_page(callback, db, user, page=0, lang=lang)