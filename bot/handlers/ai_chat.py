import logging
from typing import Any, Dict

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.texts import get_text
from bot.keyboards.inline import (
    get_ai_assistant_keyboard,
    get_back_keyboard,
    get_main_menu_keyboard,
)
from bot.keyboards.callbacks import AIChatCallback, MainMenuCallback
from core.ai_client import ai_client

logger = logging.getLogger(__name__)

router = Router(name="ai_chat")


class AIChatStates(StatesGroup):
    chatting = State()


# System prompt for the AI assistant
SYSTEM_PROMPT = """You are SaveMate AI Assistant, a helpful bot that helps users with:
- Downloading media from various platforms (YouTube, TikTok, Instagram, etc.)
- Image processing (conversion, compression, info)
- Video processing (compression, conversion, audio extraction)
- Managing history and favorites

Be concise, helpful, and friendly. Respond in the user's language when possible."""


@router.callback_query(MainMenuCallback.filter(F.section == "ai"))
async def cb_ai_assistant(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    """Show AI assistant menu."""
    await state.set_state(AIChatStates.chatting)
    text = get_text("ai_welcome", lang)
    keyboard = get_ai_assistant_keyboard(lang)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.message(AIChatStates.chatting, F.text)
async def handle_ai_message(message: Message, state: FSMContext, lang: str, user: Any, **kwargs) -> None:
    """Handle AI chat messages."""
    if not ai_client or not ai_client.is_available():
        await message.reply(get_text("ai_not_configured", lang))
        return

    # Show typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        response = await ai_client.chat_completion(
            user_id=user.id,
            message=message.text,
            system_prompt=SYSTEM_PROMPT,
        )

        if response:
            await message.reply(response, parse_mode="HTML")
        else:
            await message.reply(get_text("ai_error", lang))

    except Exception as e:
        logger.error("AI chat error for user %d: %s", user.id, e)
        await message.reply(get_text("ai_error", lang))


@router.callback_query(AIChatCallback.filter(F.chat_action == "clear_context"))
async def cb_ai_clear_context(callback: CallbackQuery, state: FSMContext, lang: str, user: Any, **kwargs) -> None:
    """Clear AI chat context."""
    if ai_client:
        ai_client.clear_context(user.id)
    await callback.answer(get_text("ai_context_cleared", lang), show_alert=True)


@router.callback_query(AIChatCallback.filter(F.chat_action == "cancel"))
async def cb_ai_cancel(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    """Cancel AI chat."""
    await state.clear()
    text = get_text("main_menu_title", lang)
    keyboard = get_main_menu_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()