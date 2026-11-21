import logging
from typing import Any, Dict

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from utils.texts import get_text
from bot.keyboards.inline import (
    get_settings_keyboard,
    get_language_keyboard,
    get_notifications_keyboard,
    get_delete_data_confirm_keyboard,
    get_back_keyboard,
    get_main_menu_keyboard,
)
from bot.keyboards.callbacks import (
    SettingsCallback,
    LanguageCallback,
    NotificationsCallback,
    DeleteDataCallback,
    MainMenuCallback,
)
from database.repositories.users import UserRepository

logger = logging.getLogger(__name__)

router = Router(name="settings")


@router.callback_query(MainMenuCallback.filter(F.section == "settings"))
async def cb_settings(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Show settings menu."""
    text = get_text("settings_title", lang)
    keyboard = get_settings_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(SettingsCallback.filter(F.setting == "language"))
async def cb_settings_language(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Show language selection."""
    text = get_text("select_language", lang)
    keyboard = get_language_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(LanguageCallback.filter())
async def cb_language_select(
    callback: CallbackQuery,
    callback_data: LanguageCallback,
    db: Any,
    user: Any,
    lang: str,
    **kwargs
) -> None:
    """Handle language selection."""
    new_lang = callback_data.lang
    user_repo = UserRepository(db)
    await user_repo.update_language(user.id, new_lang)

    # Update lang in callback data for response
    new_text = get_text("language_changed", new_lang).format(language=new_lang.upper())
    keyboard = get_back_keyboard("settings", new_lang)

    await callback.message.edit_text(new_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer(get_text("language_changed", new_lang).format(language=new_lang.upper()), show_alert=True)


@router.callback_query(SettingsCallback.filter(F.setting == "notifications"))
async def cb_settings_notifications(callback: CallbackQuery, user: Any, lang: str, **kwargs) -> None:
    """Show notifications toggle."""
    current = user.notifications_enabled
    text = get_text("notifications_settings", lang).format(
        status=get_text("enabled", lang) if current else get_text("disabled", lang)
    )
    keyboard = get_notifications_keyboard(current, lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(NotificationsCallback.filter())
async def cb_notifications_toggle(
    callback: CallbackQuery,
    callback_data: NotificationsCallback,
    db: Any,
    user: Any,
    lang: str,
    **kwargs
) -> None:
    """Toggle notifications."""
    enabled = callback_data.enabled
    user_repo = UserRepository(db)
    await user_repo.update_notifications(user.id, enabled)

    new_text = get_text("notifications_changed", lang).format(
        status=get_text("enabled", lang) if enabled else get_text("disabled", lang)
    )
    keyboard = get_notifications_keyboard(enabled, lang)

    await callback.message.edit_text(new_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer(new_text, show_alert=True)


@router.callback_query(SettingsCallback.filter(F.setting == "file_prefs"))
async def cb_settings_file_prefs(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Show file preferences (placeholder)."""
    text = get_text("file_prefs_coming_soon", lang)
    keyboard = get_back_keyboard("settings", lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(SettingsCallback.filter(F.setting == "delete_data"))
async def cb_settings_delete_data(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Show delete data confirmation."""
    text = get_text("confirm_delete_data", lang)
    keyboard = get_delete_data_confirm_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(DeleteDataCallback.filter(F.confirm == True))
async def cb_delete_data_confirm(
    callback: CallbackQuery,
    db: Any,
    user: Any,
    lang: str,
    **kwargs
) -> None:
    """Confirm delete all user data."""
    user_repo = UserRepository(db)
    await user_repo.delete_user_data(user.id)

    text = get_text("data_deleted", lang)
    keyboard = get_main_menu_keyboard(lang)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer(get_text("data_deleted", lang), show_alert=True)


@router.callback_query(DeleteDataCallback.filter(F.confirm == False))
async def cb_delete_data_cancel(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Cancel delete data."""
    await callback.answer(get_text("cancelled", lang), show_alert=True)
    text = get_text("settings_title", lang)
    keyboard = get_settings_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()