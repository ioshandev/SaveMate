from typing import List, Optional
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from utils.texts import get_text


def get_main_reply_keyboard(lang: str = "en", include_cancel: bool = False) -> ReplyKeyboardMarkup:
    """Get main reply keyboard with common actions."""
    builder = ReplyKeyboardBuilder()

    # First row - main actions
    builder.row(
        KeyboardButton(text=get_text("btn_media_assistant", lang)),
        KeyboardButton(text=get_text("btn_image_tools", lang)),
    )
    builder.row(
        KeyboardButton(text=get_text("btn_video_tools", lang)),
        KeyboardButton(text=get_text("btn_ai_assistant", lang)),
    )
    builder.row(
        KeyboardButton(text=get_text("btn_history", lang)),
        KeyboardButton(text=get_text("btn_favorites", lang)),
    )
    builder.row(
        KeyboardButton(text=get_text("btn_settings", lang)),
        KeyboardButton(text=get_text("btn_help", lang)),
    )

    if include_cancel:
        builder.row(KeyboardButton(text=get_text("btn_cancel", lang)))

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def get_media_assistant_reply_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Reply keyboard for media assistant."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=get_text("btn_back", lang)),
        KeyboardButton(text=get_text("btn_cancel", lang)),
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def get_image_tools_reply_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Reply keyboard for image tools."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=get_text("btn_convert", lang)),
        KeyboardButton(text=get_text("btn_compress", lang)),
    )
    builder.row(
        KeyboardButton(text=get_text("btn_info", lang)),
        KeyboardButton(text=get_text("btn_back", lang)),
    )
    builder.row(
        KeyboardButton(text=get_text("btn_cancel", lang)),
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def get_video_tools_reply_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Reply keyboard for video tools."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=get_text("btn_video_compress", lang)),
        KeyboardButton(text=get_text("btn_video_convert", lang)),
    )
    builder.row(
        KeyboardButton(text=get_text("btn_extract_audio", lang)),
        KeyboardButton(text=get_text("btn_video_info", lang)),
    )
    builder.row(
        KeyboardButton(text=get_text("btn_back", lang)),
        KeyboardButton(text=get_text("btn_cancel", lang)),
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def get_ai_chat_reply_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Reply keyboard for AI chat."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🧹 Clear Context"),
        KeyboardButton(text=get_text("btn_cancel", lang)),
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def get_cancel_reply_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Reply keyboard with just cancel button."""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=get_text("btn_cancel", lang)))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def get_confirm_reply_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Reply keyboard with confirm/cancel buttons."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=get_text("btn_confirm", lang)),
        KeyboardButton(text=get_text("btn_cancel", lang)),
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def get_back_cancel_reply_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Reply keyboard with back and cancel buttons."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=get_text("btn_back", lang)),
        KeyboardButton(text=get_text("btn_cancel", lang)),
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def get_settings_reply_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Reply keyboard for settings."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=get_text("btn_language", lang)),
        KeyboardButton(text=get_text("btn_notifications", lang)),
    )
    builder.row(
        KeyboardButton(text=get_text("btn_file_prefs", lang)),
        KeyboardButton(text=get_text("btn_delete_data", lang)),
    )
    builder.row(
        KeyboardButton(text=get_text("btn_back", lang)),
        KeyboardButton(text=get_text("btn_cancel", lang)),
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def get_language_reply_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Reply keyboard for language selection."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🇺🇸 English"),
        KeyboardButton(text="🇱🇰 සිංහල"),
    )
    builder.row(
        KeyboardButton(text=get_text("btn_back", lang)),
        KeyboardButton(text=get_text("btn_cancel", lang)),
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def get_notifications_reply_keyboard(current: bool, lang: str = "en") -> ReplyKeyboardMarkup:
    """Reply keyboard for notifications toggle."""
    builder = ReplyKeyboardBuilder()
    if current:
        builder.row(KeyboardButton(text=get_text("notifications_off", lang)))
    else:
        builder.row(KeyboardButton(text=get_text("notifications_on", lang)))
    builder.row(
        KeyboardButton(text=get_text("btn_back", lang)),
        KeyboardButton(text=get_text("btn_cancel", lang)),
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def get_admin_reply_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Reply keyboard for admin panel."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=get_text("btn_admin_stats", lang)),
        KeyboardButton(text=get_text("btn_admin_users", lang)),
    )
    builder.row(
        KeyboardButton(text=get_text("btn_admin_broadcast", lang)),
        KeyboardButton(text=get_text("btn_admin_status", lang)),
    )
    builder.row(
        KeyboardButton(text=get_text("btn_back", lang)),
        KeyboardButton(text=get_text("btn_cancel", lang)),
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def get_remove_keyboard() -> ReplyKeyboardRemove:
    """Remove reply keyboard."""
    return ReplyKeyboardRemove()