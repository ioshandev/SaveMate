import logging
from typing import Optional, List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.texts import get_text
from bot.keyboards.callbacks import (
    MainMenuCallback,
    BackCallback,
    MediaActionCallback,
    ImageToolCallback,
    ImageConvertCallback,
    ImageCompressCallback,
    VideoToolCallback,
    VideoCompressCallback,
    VideoConvertCallback,
    VideoExtractAudioCallback,
    AIChatCallback,
    HistoryCallback,
    FavoritesCallback,
    SettingsCallback,
    LanguageCallback,
    NotificationsCallback,
    DeleteDataCallback,
    AdminCallback,
    PaginationCallback,
)

logger = logging.getLogger(__name__)

# Main Menu
def get_main_menu_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_media_assistant", lang),
            callback_data=MainMenuCallback(action="navigate", section="media").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_image_tools", lang),
            callback_data=MainMenuCallback(action="navigate", section="image_tools").pack()
        ),
        InlineKeyboardButton(
            text=get_text("btn_video_tools", lang),
            callback_data=MainMenuCallback(action="navigate", section="video_tools").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_ai_assistant", lang),
            callback_data=MainMenuCallback(action="navigate", section="ai").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_history", lang),
            callback_data=MainMenuCallback(action="navigate", section="history").pack()
        ),
        InlineKeyboardButton(
            text=get_text("btn_favorites", lang),
            callback_data=MainMenuCallback(action="navigate", section="favorites").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_settings", lang),
            callback_data=MainMenuCallback(action="navigate", section="settings").pack()
        ),
        InlineKeyboardButton(
            text=get_text("btn_help", lang),
            callback_data=MainMenuCallback(action="navigate", section="help").pack()
        )
    )
    return builder.as_markup()


# Back button
def get_back_keyboard(target: str = "main", lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=BackCallback(action="back", target=target).pack()
        )
    )
    return builder.as_markup()


# Media Assistant
def get_media_assistant_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=BackCallback(action="back", target="main").pack()
        )
    )
    return builder.as_markup()


def get_media_result_keyboard(
    platform: str,
    url: str,
    download_allowed: bool,
    lang: str = "en"
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if download_allowed:
        # Add download options based on platform
        builder.row(
            InlineKeyboardButton(
                text="📥 Download",
                callback_data=MediaActionCallback(action="download", platform=platform, url=url).pack()
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=BackCallback(action="back", target="media").pack()
        )
    )
    return builder.as_markup()


# Image Tools
def get_image_tools_keyboard(file_id: str, lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_convert", lang),
            callback_data=ImageToolCallback(action="select_tool", tool="convert", file_id=file_id).pack()
        ),
        InlineKeyboardButton(
            text=get_text("btn_compress", lang),
            callback_data=ImageToolCallback(action="select_tool", tool="compress", file_id=file_id).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_info", lang),
            callback_data=ImageToolCallback(action="select_tool", tool="info", file_id=file_id).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=BackCallback(action="back", target="main").pack()
        )
    )
    return builder.as_markup()


def get_image_convert_keyboard(file_id: str, lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    formats = ["JPEG", "PNG", "WEBP", "GIF", "BMP", "TIFF"]
    for fmt in formats:
        builder.row(
            InlineKeyboardButton(
                text=fmt,
                callback_data=ImageConvertCallback(action="convert", format=fmt, file_id=file_id).pack()
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=ImageToolCallback(action="back", tool="main", file_id=file_id).pack()
        )
    )
    return builder.as_markup()


def get_image_compress_keyboard(file_id: str, lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    presets = [
        ("high", "High (85%)"),
        ("medium", "Medium (65%)"),
        ("low", "Low (40%)"),
        ("minimal", "Minimal (20%)"),
    ]
    for preset, label in presets:
        builder.row(
            InlineKeyboardButton(
                text=label,
                callback_data=ImageCompressCallback(action="compress", preset=preset, file_id=file_id).pack()
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=ImageToolCallback(action="back", tool="main", file_id=file_id).pack()
        )
    )
    return builder.as_markup()


# Video Tools
def get_video_tools_keyboard(file_id: str, lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_video_compress", lang),
            callback_data=VideoToolCallback(action="select_tool", tool="compress", file_id=file_id).pack()
        ),
        InlineKeyboardButton(
            text=get_text("btn_video_convert", lang),
            callback_data=VideoToolCallback(action="select_tool", tool="convert", file_id=file_id).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_extract_audio", lang),
            callback_data=VideoToolCallback(action="select_tool", tool="extract_audio", file_id=file_id).pack()
        ),
        InlineKeyboardButton(
            text=get_text("btn_video_info", lang),
            callback_data=VideoToolCallback(action="select_tool", tool="info", file_id=file_id).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=BackCallback(action="back", target="main").pack()
        )
    )
    return builder.as_markup()


def get_video_compress_keyboard(file_id: str, lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    presets = [
        ("high", "High (CRF 18)"),
        ("medium", "Medium (CRF 23)"),
        ("low", "Low (CRF 28)"),
        ("minimal", "Minimal (CRF 32)"),
    ]
    for preset, label in presets:
        builder.row(
            InlineKeyboardButton(
                text=label,
                callback_data=VideoCompressCallback(action="compress", preset=preset, file_id=file_id).pack()
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=VideoToolCallback(action="back", tool="main", file_id=file_id).pack()
        )
    )
    return builder.as_markup()


def get_video_convert_keyboard(file_id: str, lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    formats = ["mp4", "mov", "mkv", "webm", "avi"]
    for fmt in formats:
        builder.row(
            InlineKeyboardButton(
                text=fmt.upper(),
                callback_data=VideoConvertCallback(action="convert", format=fmt, file_id=file_id).pack()
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=VideoToolCallback(action="back", tool="main", file_id=file_id).pack()
        )
    )
    return builder.as_markup()


def get_video_extract_audio_keyboard(file_id: str, lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    formats = ["mp3", "aac", "ogg", "flac", "wav", "m4a", "opus"]
    for fmt in formats:
        builder.row(
            InlineKeyboardButton(
                text=fmt.upper(),
                callback_data=VideoExtractAudioCallback(action="extract", format=fmt, file_id=file_id).pack()
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=VideoToolCallback(action="back", tool="main", file_id=file_id).pack()
        )
    )
    return builder.as_markup()


# AI Assistant
def get_ai_assistant_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_cancel", lang),
            callback_data=AIChatCallback(action="cancel", chat_action="cancel").pack()
        ),
        InlineKeyboardButton(
            text="🧹 Clear Context",
            callback_data=AIChatCallback(action="clear_context", chat_action="clear_context").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=BackCallback(action="back", target="main").pack()
        )
    )
    return builder.as_markup()


# History
def get_history_keyboard(
    page: int,
    has_next: bool,
    total: int,
    lang: str = "en"
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if total > 0:
        builder.row(
            InlineKeyboardButton(
                text=get_text("btn_clear_history", lang),
                callback_data=HistoryCallback(action="clear", page=page).pack()
            )
        )
    # Pagination
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="◀️ Prev",
                callback_data=PaginationCallback(action="page", page=page - 1, context="history").pack()
            )
        )
    if has_next:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Next ▶️",
                callback_data=PaginationCallback(action="page", page=page + 1, context="history").pack()
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=BackCallback(action="back", target="main").pack()
        )
    )
    return builder.as_markup()


def get_history_clear_confirm_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_confirm", lang),
            callback_data=HistoryCallback(action="confirm_clear", page=0).pack()
        ),
        InlineKeyboardButton(
            text=get_text("btn_cancel", lang),
            callback_data=HistoryCallback(action="cancel_clear", page=0).pack()
        )
    )
    return builder.as_markup()


# Favorites
def get_favorites_keyboard(
    page: int,
    has_next: bool,
    total: int,
    lang: str = "en"
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Pagination
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="◀️ Prev",
                callback_data=PaginationCallback(action="page", page=page - 1, context="favorites").pack()
            )
        )
    if has_next:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Next ▶️",
                callback_data=PaginationCallback(action="page", page=page + 1, context="favorites").pack()
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=BackCallback(action="back", target="main").pack()
        )
    )
    return builder.as_markup()


def get_favorite_item_keyboard(favorite_id: int, lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_remove_favorite", lang),
            callback_data=FavoritesCallback(action="remove", fav_action="remove", favorite_id=favorite_id).pack()
        ),
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=BackCallback(action="back", target="favorites").pack()
        )
    )
    return builder.as_markup()


# Settings
def get_settings_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_language", lang),
            callback_data=SettingsCallback(action="setting", setting="language").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_notifications", lang),
            callback_data=SettingsCallback(action="setting", setting="notifications").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_file_prefs", lang),
            callback_data=SettingsCallback(action="setting", setting="file_prefs").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_delete_data", lang),
            callback_data=SettingsCallback(action="setting", setting="delete_data").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=BackCallback(action="back", target="main").pack()
        )
    )
    return builder.as_markup()


def get_language_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🇺🇸 English",
            callback_data=LanguageCallback(action="language", lang="en").pack()
        ),
        InlineKeyboardButton(
            text="🇱🇰 සිංහල",
            callback_data=LanguageCallback(action="language", lang="si").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=BackCallback(action="back", target="settings").pack()
        )
    )
    return builder.as_markup()


def get_notifications_keyboard(current: bool, lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=("🔔 " if current else "") + get_text("notifications_on", lang) if current else get_text("notifications_off", lang),
            callback_data=NotificationsCallback(action="notifications", enabled=not current).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=BackCallback(action="back", target="settings").pack()
        )
    )
    return builder.as_markup()


def get_delete_data_confirm_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_confirm", lang),
            callback_data=DeleteDataCallback(action="delete_data", confirm=True).pack()
        ),
        InlineKeyboardButton(
            text=get_text("btn_cancel", lang),
            callback_data=DeleteDataCallback(action="delete_data", confirm=False).pack()
        )
    )
    return builder.as_markup()


# Help
def get_help_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return get_back_keyboard("main", lang)


# Admin
def get_admin_panel_keyboard(
    total_users: int,
    active_users: int,
    total_processed: int,
    ai_status: str,
    ffmpeg_status: str,
    lang: str = "en"
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_admin_stats", lang),
            callback_data=AdminCallback(action="admin", admin_action="stats").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_admin_users", lang),
            callback_data=AdminCallback(action="admin", admin_action="users", page=0).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_admin_broadcast", lang),
            callback_data=AdminCallback(action="admin", admin_action="broadcast").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_admin_status", lang),
            callback_data=AdminCallback(action="admin", admin_action="status").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=BackCallback(action="back", target="main").pack()
        )
    )
    return builder.as_markup()


def get_admin_users_keyboard(page: int, has_next: bool, lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="◀️ Prev",
                callback_data=PaginationCallback(action="page", page=page - 1, context="admin_users").pack()
            )
        )
    if has_next:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Next ▶️",
                callback_data=PaginationCallback(action="page", page=page + 1, context="admin_users").pack()
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=BackCallback(action="back", target="admin").pack()
        )
    )
    return builder.as_markup()


def get_admin_user_keyboard(user_id: int, lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data=BackCallback(action="back", target="admin_users").pack()
        )
    )
    return builder.as_markup()


# Cancel keyboard
def get_cancel_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_cancel", lang),
            callback_data=BackCallback(action="cancel").pack()
        )
    )
    return builder.as_markup()