import logging
from typing import Any, Dict

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from utils.texts import get_text
from bot.keyboards.inline import (
    get_main_menu_keyboard,
    get_help_keyboard,
)
from bot.keyboards.callbacks import MainMenuCallback

logger = logging.getLogger(__name__)

router = Router(name="help")


@router.message(Command("help"))
async def cmd_help(message: Message, lang: str, **kwargs) -> None:
    """Handle /help command."""
    text = get_text("help", lang)
    keyboard = get_help_keyboard(lang)

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(MainMenuCallback.filter(F.section == "help"))
async def cb_help(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Handle help menu callback."""
    text = get_text("help", lang)
    keyboard = get_help_keyboard(lang)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(MainMenuCallback.filter(F.section == "main"))
async def cb_main_menu(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Handle back to main menu callback."""
    text = get_text("main_menu", lang)
    keyboard = get_main_menu_keyboard(lang)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()