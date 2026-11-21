import logging
import os
from typing import Any, Dict

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, Document, PhotoSize
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.texts import get_text
from bot.keyboards.inline import (
    get_image_tools_keyboard,
    get_image_convert_keyboard,
    get_image_compress_keyboard,
    get_video_tools_keyboard,
    get_video_compress_keyboard,
    get_video_convert_keyboard,
    get_video_extract_audio_keyboard,
    get_back_keyboard,
)
from bot.keyboards.callbacks import (
    ImageToolCallback,
    ImageConvertCallback,
    ImageCompressCallback,
    VideoToolCallback,
    VideoCompressCallback,
    VideoConvertCallback,
    VideoExtractAudioCallback,
    MainMenuCallback,
)
from core.media import process_image, process_video, detect_file_type
from utils.tempfiles import temp_file, cleanup_old_temp_files

logger = logging.getLogger(__name__)

router = Router(name="media_tools")


class MediaToolsStates(StatesGroup):
    waiting_for_image = State()
    waiting_for_video = State()


# Image Tools
@router.callback_query(MainMenuCallback.filter(F.section == "image_tools"))
async def cb_image_tools(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Show image tools menu."""
    text = get_text("image_tools_title", lang)
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("main", lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(F.photo | F.document)
async def handle_media_file(message: Message, state: FSMContext, lang: str, user: Any, **kwargs) -> None:
    """Handle incoming media files (images/videos)."""
    # Determine file type
    file_id = None
    file_name = None
    mime_type = None

    if message.photo:
        photo: PhotoSize = message.photo[-1]  # Largest size
        file_id = photo.file_id
        file_name = f"photo_{photo.file_unique_id}.jpg"
        mime_type = "image/jpeg"
    elif message.document:
        doc: Document = message.document
        file_id = doc.file_id
        file_name = doc.file_name
        mime_type = doc.mime_type

    if not file_id:
        return

    # Detect file type
    file_type = detect_file_type(mime_type or "", file_name or "")

    if file_type == "image":
        await handle_image_file(message, file_id, file_name, lang, state)
    elif file_type == "video":
        await handle_video_file(message, file_id, file_name, lang, state)
    else:
        await message.reply(get_text("error_unsupported_file_type", lang))


async def handle_image_file(message: Message, file_id: str, file_name: str, lang: str, state: FSMContext) -> None:
    """Handle image file - show image tools."""
    await state.update_data(image_file_id=file_id, image_file_name=file_name)
    await state.set_state(MediaToolsStates.waiting_for_image)

    text = get_text("image_received", lang).format(filename=file_name)
    await message.reply(text, reply_markup=get_image_tools_keyboard(file_id, lang))


async def handle_video_file(message: Message, file_id: str, file_name: str, lang: str, state: FSMContext) -> None:
    """Handle video file - show video tools."""
    await state.update_data(video_file_id=file_id, video_file_name=file_name)
    await state.set_state(MediaToolsStates.waiting_for_video)

    text = get_text("video_received", lang).format(filename=file_name)
    await message.reply(text, reply_markup=get_video_tools_keyboard(file_id, lang))


# Image Tool Callbacks
@router.callback_query(ImageToolCallback.filter(F.action == "select_tool"))
async def cb_image_tool_select(
    callback: CallbackQuery,
    callback_data: ImageToolCallback,
    lang: str,
    **kwargs
) -> None:
    """Handle image tool selection."""
    tool = callback_data.tool
    file_id = callback_data.file_id

    if tool == "convert":
        text = get_text("select_convert_format", lang)
        keyboard = get_image_convert_keyboard(file_id, lang)
    elif tool == "compress":
        text = get_text("select_compress_preset", lang)
        keyboard = get_image_compress_keyboard(file_id, lang)
    elif tool == "info":
        await cb_image_info(callback, file_id, lang)
        return
    else:
        await callback.answer(get_text("error_unknown_tool", lang), show_alert=True)
        return

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(ImageConvertCallback.filter(F.action == "convert"))
async def cb_image_convert(
    callback: CallbackQuery,
    callback_data: ImageConvertCallback,
    state: FSMContext,
    lang: str,
    bot: Any,
    **kwargs
) -> None:
    """Handle image conversion."""
    file_id = callback_data.file_id
    target_format = callback_data.format
    quality = callback_data.quality

    await callback.message.edit_text(get_text("processing", lang))
    await callback.answer()

    try:
        # Download file
        file = await bot.get_file(file_id)
        file_path = file.file_path

        with temp_file(suffix=f".{target_format.lower()}") as output_path:
            # Download to temp file
            await bot.download_file(file_path, output_path)

            # Process image
            result_path = await process_image(
                input_path=output_path,
                operation="convert",
                format=target_format,
                quality=quality,
            )

            # Send result
            from aiogram.types import FSInputFile
            result_file = FSInputFile(result_path, filename=f"converted.{target_format.lower()}")
            await callback.message.answer_document(
                result_file,
                caption=get_text("conversion_complete", lang).format(format=target_format)
            )

    except Exception as e:
        logger.error("Image conversion error: %s", e)
        await callback.message.answer(get_text("error_processing", lang).format(error=str(e)))


@router.callback_query(ImageCompressCallback.filter(F.action == "compress"))
async def cb_image_compress(
    callback: CallbackQuery,
    callback_data: ImageCompressCallback,
    state: FSMContext,
    lang: str,
    bot: Any,
    **kwargs
) -> None:
    """Handle image compression."""
    file_id = callback_data.file_id
    preset = callback_data.preset

    await callback.message.edit_text(get_text("processing", lang))
    await callback.answer()

    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path

        with temp_file(suffix=".jpg") as output_path:
            await bot.download_file(file_path, output_path)

            result_path = await process_image(
                input_path=output_path,
                operation="compress",
                preset=preset,
            )

            from aiogram.types import FSInputFile
            result_file = FSInputFile(result_path, filename=f"compressed_{preset}.jpg")
            await callback.message.answer_document(
                result_file,
                caption=get_text("compression_complete", lang).format(preset=preset)
            )

    except Exception as e:
        logger.error("Image compression error: %s", e)
        await callback.message.answer(get_text("error_processing", lang).format(error=str(e)))


async def cb_image_info(callback: CallbackQuery, file_id: str, lang: str, bot: Any) -> None:
    """Show image info."""
    await callback.answer()
    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path

        with temp_file() as temp_path:
            await bot.download_file(file_path, temp_path)
            info = await get_image_info_detailed(temp_path)

        text = get_text("image_info", lang).format(
            width=info.get("width", "?"),
            height=info.get("height", "?"),
            format=info.get("format", "?"),
            mode=info.get("mode", "?"),
            size=format_file_size(info.get("size", 0)),
        )
        await callback.message.edit_text(text, reply_markup=get_back_keyboard("main", lang), parse_mode="HTML")

    except Exception as e:
        logger.error("Image info error: %s", e)
        await callback.message.answer(get_text("error_processing", lang).format(error=str(e)))


# Video Tool Callbacks
@router.callback_query(MainMenuCallback.filter(F.section == "video_tools"))
async def cb_video_tools(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Show video tools menu."""
    text = get_text("video_tools_title", lang)
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("main", lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(VideoToolCallback.filter(F.action == "select_tool"))
async def cb_video_tool_select(
    callback: CallbackQuery,
    callback_data: VideoToolCallback,
    lang: str,
    **kwargs
) -> None:
    """Handle video tool selection."""
    tool = callback_data.tool
    file_id = callback_data.file_id

    if tool == "compress":
        text = get_text("select_compress_preset", lang)
        keyboard = get_video_compress_keyboard(file_id, lang)
    elif tool == "convert":
        text = get_text("select_convert_format", lang)
        keyboard = get_video_convert_keyboard(file_id, lang)
    elif tool == "extract_audio":
        text = get_text("select_audio_format", lang)
        keyboard = get_video_extract_audio_keyboard(file_id, lang)
    elif tool == "info":
        await cb_video_info(callback, file_id, lang)
        return
    else:
        await callback.answer(get_text("error_unknown_tool", lang), show_alert=True)
        return

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(VideoCompressCallback.filter(F.action == "compress"))
async def cb_video_compress(
    callback: CallbackQuery,
    callback_data: VideoCompressCallback,
    state: FSMContext,
    lang: str,
    bot: Any,
    **kwargs
) -> None:
    """Handle video compression."""
    file_id = callback_data.file_id
    preset = callback_data.preset

    await callback.message.edit_text(get_text("processing_video", lang))
    await callback.answer()

    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path

        with temp_file(suffix=".mp4") as output_path:
            await bot.download_file(file_path, output_path)

            result_path = await process_video(
                input_path=output_path,
                operation="compress",
                preset=preset,
            )

            from aiogram.types import FSInputFile
            result_file = FSInputFile(result_path, filename=f"compressed_{preset}.mp4")
            await callback.message.answer_video(
                result_file,
                caption=get_text("compression_complete", lang).format(preset=preset)
            )

    except Exception as e:
        logger.error("Video compression error: %s", e)
        await callback.message.answer(get_text("error_processing", lang).format(error=str(e)))


@router.callback_query(VideoConvertCallback.filter(F.action == "convert"))
async def cb_video_convert(
    callback: CallbackQuery,
    callback_data: VideoConvertCallback,
    state: FSMContext,
    lang: str,
    bot: Any,
    **kwargs
) -> None:
    """Handle video conversion."""
    file_id = callback_data.file_id
    target_format = callback_data.format
    preset = callback_data.preset

    await callback.message.edit_text(get_text("processing_video", lang))
    await callback.answer()

    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path

        with temp_file(suffix=f".{target_format}") as output_path:
            await bot.download_file(file_path, output_path)

            result_path = await process_video(
                input_path=output_path,
                operation="convert",
                format=target_format,
                preset=preset,
            )

            from aiogram.types import FSInputFile
            result_file = FSInputFile(result_path, filename=f"converted.{target_format}")
            await callback.message.answer_video(
                result_file,
                caption=get_text("conversion_complete", lang).format(format=target_format)
            )

    except Exception as e:
        logger.error("Video conversion error: %s", e)
        await callback.message.answer(get_text("error_processing", lang).format(error=str(e)))


@router.callback_query(VideoExtractAudioCallback.filter(F.action == "extract"))
async def cb_video_extract_audio(
    callback: CallbackQuery,
    callback_data: VideoExtractAudioCallback,
    state: FSMContext,
    lang: str,
    bot: Any,
    **kwargs
) -> None:
    """Handle audio extraction."""
    file_id = callback_data.file_id
    target_format = callback_data.format
    preset = callback_data.preset

    await callback.message.edit_text(get_text("processing_video", lang))
    await callback.answer()

    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path

        with temp_file(suffix=f".{target_format}") as output_path:
            await bot.download_file(file_path, output_path)

            result_path = await process_video(
                input_path=output_path,
                operation="extract_audio",
                format=target_format,
                preset=preset,
            )

            from aiogram.types import FSInputFile
            result_file = FSInputFile(result_path, filename=f"audio.{target_format}")
            await callback.message.answer_audio(
                result_file,
                caption=get_text("extraction_complete", lang).format(format=target_format)
            )

    except Exception as e:
        logger.error("Audio extraction error: %s", e)
        await callback.message.answer(get_text("error_processing", lang).format(error=str(e)))


async def cb_video_info(callback: CallbackQuery, file_id: str, lang: str, bot: Any) -> None:
    """Show video info."""
    await callback.answer()
    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path

        with temp_file() as temp_path:
            await bot.download_file(file_path, temp_path)
            info = await get_video_info(temp_path)

        text = get_text("video_info", lang).format(
            width=info.get("width", "?"),
            height=info.get("height", "?"),
            duration=format_duration(info.get("duration", 0)),
            format=info.get("format", "?"),
            size=format_file_size(info.get("size", 0)),
            fps=info.get("fps", "?"),
        )
        await callback.message.edit_text(text, reply_markup=get_back_keyboard("main", lang), parse_mode="HTML")

    except Exception as e:
        logger.error("Video info error: %s", e)
        await callback.message.answer(get_text("error_processing", lang).format(error=str(e)))


def format_file_size(bytes_: int) -> str:
    """Format file size in human readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_ < 1024:
            return f"{bytes_:.1f} {unit}"
        bytes_ /= 1024
    return f"{bytes_:.1f} TB"


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


# Import for image info
from core.media import get_image_info_detailed, get_video_info