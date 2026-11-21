import logging
from typing import Any, Dict, List

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from core.security import is_valid_url, URLValidationError
from services.platform_adapters.registry import adapter_registry
from utils.texts import get_text
from bot.keyboards.inline import (
    get_media_assistant_keyboard,
    get_media_result_keyboard,
    get_back_keyboard,
)
from bot.keyboards.callbacks import MediaActionCallback
from database.repositories.history import HistoryRepository

logger = logging.getLogger(__name__)

router = Router(name="links")


@router.message(F.text)
async def handle_text_message(message: Message, urls: List[str], db: Any, user: Any, lang: str, **kwargs) -> None:
    """Handle messages containing URLs."""
    if not urls:
        return

    # Process each URL
    for url in urls:
        await process_url(message, url, db, user, lang)


async def process_url(message: Message, url: str, db: Any, user: Any, lang: str) -> None:
    """Process a single URL through platform adapters."""
    try:
        # Validate URL
        is_valid_url(url)
    except URLValidationError as e:
        await message.reply(get_text("error_invalid_url", lang).format(error=str(e)))
        logger.warning("Invalid URL from user %d: %s - %s", user.id, url, e)
        return

    # Show processing message
    processing_msg = await message.reply(get_text("processing_url", lang))

    try:
        # Get metadata from platform adapter
        metadata = await adapter_registry.fetch_metadata(url)

        if not metadata:
            await processing_msg.edit_text(
                get_text("error_unsupported_platform", lang),
                reply_markup=get_back_keyboard("media", lang)
            )
            return

        # Save to history
        history_repo = HistoryRepository(db)
        await history_repo.add(
            user_id=user.id,
            platform=metadata.platform,
            url=url,
            title=metadata.title,
            media_type=metadata.media_type,
            thumbnail_url=metadata.thumbnail_url,
        )

        # Format response
        response = format_metadata(metadata, lang)
        keyboard = get_media_result_keyboard(
            platform=metadata.platform,
            url=url,
            download_allowed=metadata.download_allowed,
            lang=lang
        )

        await processing_msg.edit_text(response, reply_markup=keyboard, parse_mode="HTML")

    except Exception as e:
        logger.error("Error processing URL %s for user %d: %s", url, user.id, e)
        await processing_msg.edit_text(
            get_text("error_processing", lang).format(error=str(e)),
            reply_markup=get_back_keyboard("media", lang)
        )


def format_metadata(metadata: Any, lang: str) -> str:
    """Format metadata for display."""
    lines = [
        f"<b>{get_text('media_found', lang)}</b>",
        f"🌐 <b>Platform:</b> {metadata.platform.title()}",
    ]

    if metadata.title:
        lines.append(f"📝 <b>Title:</b> {metadata.title[:100]}")

    if metadata.author:
        lines.append(f"👤 <b>Author:</b> {metadata.author}")

    if metadata.duration:
        lines.append(f"⏱ <b>Duration:</b> {format_duration(metadata.duration)}")

    if metadata.media_type:
        lines.append(f"📎 <b>Type:</b> {metadata.media_type}")

    return "\n".join(lines)


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


@router.callback_query(MediaActionCallback.filter(F.action == "download"))
async def cb_media_download(callback: CallbackQuery, callback_data: MediaActionCallback, lang: str, **kwargs) -> None:
    """Handle media download request."""
    # This would trigger the download process
    # For now, show a message that download is not yet implemented
    await callback.answer(get_text("feature_coming_soon", lang), show_alert=True)