import logging
from typing import Any, Dict

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from utils.texts import get_text
from bot.keyboards.inline import (
    get_favorites_keyboard,
    get_favorite_item_keyboard,
    get_back_keyboard,
)
from bot.keyboards.callbacks import FavoritesCallback, PaginationCallback, MainMenuCallback
from database.repositories.favorites import FavoritesRepository

logger = logging.getLogger(__name__)

router = Router(name="favorites")

ITEMS_PER_PAGE = 10


@router.callback_query(MainMenuCallback.filter(F.section == "favorites"))
async def cb_favorites(callback: CallbackQuery, db: Any, user: Any, lang: str, **kwargs) -> None:
    """Show favorites first page."""
    await show_favorites_page(callback, db, user, page=0, lang=lang)


@router.callback_query(PaginationCallback.filter(F.context == "favorites"))
async def cb_favorites_pagination(
    callback: CallbackQuery,
    callback_data: PaginationCallback,
    db: Any,
    user: Any,
    lang: str,
    **kwargs
) -> None:
    """Handle favorites pagination."""
    await show_favorites_page(callback, db, user, page=callback_data.page, lang=lang)


async def show_favorites_page(
    callback: CallbackQuery,
    db: Any,
    user: Any,
    page: int,
    lang: str
) -> None:
    """Show favorites page."""
    fav_repo = FavoritesRepository(db)
    items = await fav_repo.get_user_favorites(user.id, page=page, limit=ITEMS_PER_PAGE)
    total = await fav_repo.get_user_favorites_count(user.id)

    has_next = (page + 1) * ITEMS_PER_PAGE < total

    if not items:
        text = get_text("favorites_empty", lang)
        keyboard = get_back_keyboard("main", lang)
    else:
        text = format_favorites_page(items, page, total, lang)
        keyboard = get_favorites_keyboard(page, has_next, total, lang)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


def format_favorites_page(items: list, page: int, total: int, lang: str) -> str:
    """Format favorites page for display."""
    lines = [f"<b>{get_text('favorites_title', lang)}</b> (Page {page + 1}, Total: {total})\n"]

    for i, item in enumerate(items, start=page * ITEMS_PER_PAGE + 1):
        platform = item.get("platform", "unknown").title()
        title = item.get("title", "Untitled")[:50]
        media_type = item.get("media_type", "unknown")
        created_at = item.get("created_at", "")

        lines.append(
            f"{i}. <b>{platform}</b> | {title} | {media_type} | {created_at}"
        )

    return "\n".join(lines)


@router.callback_query(FavoritesCallback.filter(F.fav_action == "remove"))
async def cb_favorite_remove(
    callback: CallbackQuery,
    callback_data: FavoritesCallback,
    db: Any,
    user: Any,
    lang: str,
    **kwargs
) -> None:
    """Remove favorite."""
    favorite_id = callback_data.favorite_id
    if favorite_id is None:
        await callback.answer(get_text("error_invalid_favorite", lang), show_alert=True)
        return

    fav_repo = FavoritesRepository(db)
    await fav_repo.remove_favorite(user.id, favorite_id)

    await callback.answer(get_text("favorite_removed", lang), show_alert=True)

    # Refresh current page
    page = callback_data.page
    await show_favorites_page(callback, db, user, page=page, lang=lang)


@router.callback_query(FavoritesCallback.filter(F.fav_action == "view"))
async def cb_favorite_view(
    callback: CallbackQuery,
    callback_data: FavoritesCallback,
    db: Any,
    user: Any,
    lang: str,
    **kwargs
) -> None:
    """View favorite details."""
    favorite_id = callback_data.favorite_id
    if favorite_id is None:
        await callback.answer(get_text("error_invalid_favorite", lang), show_alert=True)
        return

    fav_repo = FavoritesRepository(db)
    favorite = await fav_repo.get_favorite(user.id, favorite_id)

    if not favorite:
        await callback.answer(get_text("error_favorite_not_found", lang), show_alert=True)
        return

    text = format_favorite_detail(favorite, lang)
    keyboard = get_favorite_item_keyboard(favorite_id, lang)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


def format_favorite_detail(favorite: dict, lang: str) -> str:
    """Format favorite detail for display."""
    lines = [
        f"<b>{get_text('favorite_details', lang)}</b>",
        f"🌐 <b>Platform:</b> {favorite.get('platform', 'unknown').title()}",
        f"📝 <b>Title:</b> {favorite.get('title', 'Untitled')}",
        f"📎 <b>Type:</b> {favorite.get('media_type', 'unknown')}",
        f"🔗 <b>URL:</b> {favorite.get('url', 'N/A')}",
        f"📅 <b>Added:</b> {favorite.get('created_at', 'Unknown')}",
    ]

    if favorite.get("thumbnail_url"):
        lines.append(f"🖼 <b>Thumbnail:</b> {favorite['thumbnail_url']}")

    return "\n".join(lines)