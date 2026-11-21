import logging
from typing import Any, Dict

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.texts import get_text
from bot.keyboards.inline import (
    get_admin_panel_keyboard,
    get_admin_users_keyboard,
    get_admin_user_keyboard,
    get_back_keyboard,
)
from bot.keyboards.callbacks import AdminCallback, PaginationCallback, MainMenuCallback
from bot.filters.admin import IsAdmin
from database.repositories.stats import StatsRepository
from database.repositories.users import UserRepository
from core.ai_client import ai_client
from core.media.ffmpeg import check_ffmpeg

logger = logging.getLogger(__name__)

router = Router(name="admin")

# Apply admin filter to all handlers in this router
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


class AdminStates(StatesGroup):
    broadcast_message = State()


@router.message(Command("admin"))
async def cmd_admin(message: Message, user: Any, lang: str, **kwargs) -> None:
    """Handle /admin command."""
    await show_admin_panel(message, user, lang)


@router.callback_query(MainMenuCallback.filter(F.section == "admin"))
async def cb_admin_panel(callback: CallbackQuery, db: Any, user: Any, lang: str, **kwargs) -> None:
    """Show admin panel."""
    await show_admin_panel(callback, user, lang, db=db)


async def show_admin_panel(
    event: Message | CallbackQuery,
    user: Any,
    lang: str,
    db: Any = None
) -> None:
    """Show admin panel with stats."""
    # Get stats
    stats = {}
    if db:
        stats_repo = StatsRepository(db)
        stats = await stats_repo.get_bot_stats()

    # Check AI status
    ai_status = get_text("status_online", lang) if (ai_client and ai_client.is_available()) else get_text("status_offline", lang)

    # Check FFmpeg status
    ffmpeg_available = await check_ffmpeg()
    ffmpeg_status = get_text("status_online", lang) if ffmpeg_available else get_text("status_offline", lang)

    text = get_text("admin_panel", lang).format(
        total_users=stats.get("total_users", 0),
        active_users=stats.get("active_users_24h", 0),
        total_processed=stats.get("total_processed", 0),
        ai_status=ai_status,
        ffmpeg_status=ffmpeg_status,
    )

    keyboard = get_admin_panel_keyboard(
        total_users=stats.get("total_users", 0),
        active_users=stats.get("active_users_24h", 0),
        total_processed=stats.get("total_processed", 0),
        ai_status=ai_status,
        ffmpeg_status=ffmpeg_status,
        lang=lang
    )

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(AdminCallback.filter(F.admin_action == "stats"))
async def cb_admin_stats(callback: CallbackQuery, db: Any, lang: str, **kwargs) -> None:
    """Show detailed bot stats."""
    stats_repo = StatsRepository(db)
    stats = await stats_repo.get_detailed_stats()

    text = get_text("admin_detailed_stats", lang).format(
        total_users=stats.get("total_users", 0),
        active_users_24h=stats.get("active_users_24h", 0),
        active_users_7d=stats.get("active_users_7d", 0),
        total_processed=stats.get("total_processed", 0),
        total_history=stats.get("total_history", 0),
        total_favorites=stats.get("total_favorites", 0),
        by_platform=format_platform_stats(stats.get("by_platform", {}), lang),
        by_media_type=format_media_type_stats(stats.get("by_media_type", {}), lang),
    )

    keyboard = get_back_keyboard("admin", lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(AdminCallback.filter(F.admin_action == "users"))
async def cb_admin_users(callback: CallbackQuery, db: Any, lang: str, **kwargs) -> None:
    """Show users list."""
    await show_admin_users_page(callback, db, page=0, lang=lang)


@router.callback_query(PaginationCallback.filter(F.context == "admin_users"))
async def cb_admin_users_pagination(
    callback: CallbackQuery,
    callback_data: PaginationCallback,
    db: Any,
    lang: str,
    **kwargs
) -> None:
    """Handle users list pagination."""
    await show_admin_users_page(callback, db, page=callback_data.page, lang=lang)


async def show_admin_users_page(
    callback: CallbackQuery,
    db: Any,
    page: int,
    lang: str
) -> None:
    """Show admin users page."""
    user_repo = UserRepository(db)
    users = await user_repo.get_all_users(page=page, limit=20)
    total = await user_repo.get_total_users_count()

    has_next = (page + 1) * 20 < total

    if not users:
        text = get_text("no_users_found", lang)
    else:
        text = format_users_list(users, page, total, lang)

    keyboard = get_admin_users_keyboard(page, has_next, lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(AdminCallback.filter(F.admin_action == "user_info"))
async def cb_admin_user_info(
    callback: CallbackQuery,
    callback_data: AdminCallback,
    db: Any,
    lang: str,
    **kwargs
) -> None:
    """Show user info."""
    user_id = callback_data.user_id
    if not user_id:
        await callback.answer(get_text("error_invalid_user", lang), show_alert=True)
        return

    user_repo = UserRepository(db)
    user = await user_repo.get_user(user_id)
    stats = await user_repo.get_user_stats(user_id)

    if not user:
        await callback.answer(get_text("error_user_not_found", lang), show_alert=True)
        return

    text = get_text("admin_user_info", lang).format(
        user_id=user.id,
        username=user.username or "N/A",
        first_name=user.first_name or "N/A",
        last_name=user.last_name or "N/A",
        language=user.language,
        notifications="ON" if user.notifications_enabled else "OFF",
        total_processed=user.total_processed,
        created_at=user.created_at,
        last_activity=user.last_activity,
        history_count=stats.get("history_count", 0),
        favorites_count=stats.get("favorites_count", 0),
    )

    keyboard = get_admin_user_keyboard(user_id, lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(AdminCallback.filter(F.admin_action == "broadcast"))
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    """Start broadcast message."""
    await state.set_state(AdminStates.broadcast_message)
    text = get_text("admin_broadcast_prompt", lang)
    keyboard = get_back_keyboard("admin", lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.message(AdminStates.broadcast_message, F.text)
async def handle_broadcast_message(message: Message, state: FSMContext, db: Any, lang: str, **kwargs) -> None:
    """Handle broadcast message."""
    await state.clear()

    user_repo = UserRepository(db)
    users = await user_repo.get_all_users(limit=10000)  # Get all users

    sent = 0
    failed = 0
    for user in users:
        try:
            await message.bot.send_message(user.id, message.text, parse_mode="HTML")
            sent += 1
        except Exception as e:
            logger.warning("Failed to send broadcast to user %d: %s", user.id, e)
            failed += 1

    text = get_text("admin_broadcast_done", lang).format(sent=sent, failed=failed)
    keyboard = get_back_keyboard("admin", lang)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(AdminCallback.filter(F.admin_action == "status"))
async def cb_admin_status(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Show system status."""
    # Check AI
    ai_status = get_text("status_online", lang) if (ai_client and ai_client.is_available()) else get_text("status_offline", lang)

    # Check FFmpeg
    ffmpeg_available = await check_ffmpeg()
    ffmpeg_status = get_text("status_online", lang) if ffmpeg_available else get_text("status_offline", lang)

    # Check database
    db_status = get_text("status_online", lang)  # Would need actual check

    text = get_text("admin_system_status", lang).format(
        ai_status=ai_status,
        ffmpeg_status=ffmpeg_status,
        db_status=db_status,
    )

    keyboard = get_back_keyboard("admin", lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


def format_platform_stats(platform_stats: dict, lang: str) -> str:
    """Format platform stats for display."""
    if not platform_stats:
        return get_text("no_data", lang)

    lines = []
    for platform, count in sorted(platform_stats.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"  • {platform.title()}: {count}")
    return "\n".join(lines)


def format_media_type_stats(media_stats: dict, lang: str) -> str:
    """Format media type stats for display."""
    if not media_stats:
        return get_text("no_data", lang)

    lines = []
    for media_type, count in sorted(media_stats.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"  • {media_type}: {count}")
    return "\n".join(lines)


def format_users_list(users: list, page: int, total: int, lang: str) -> str:
    """Format users list for display."""
    lines = [f"<b>{get_text('admin_users_list', lang)}</b> (Page {page + 1}, Total: {total})\n"]

    for i, user in enumerate(users, start=page * 20 + 1):
        username = f"@{user['username']}" if user.get('username') else "N/A"
        lines.append(
            f"{i}. <code>{user['id']}</code> | {username} | {user.get('first_name', '')} | "
            f"Processed: {user.get('total_processed', 0)} | Last: {user.get('last_activity', 'Never')}"
        )

    return "\n".join(lines)