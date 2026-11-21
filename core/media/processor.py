import logging
from pathlib import Path
from typing import Optional, Tuple

from config import config
from core.media import images, ffmpeg
from utils.tempfiles import temp_file

logger = logging.getLogger(__name__)

# File type detection
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".tif", ".heic", ".avif"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv", ".m4v", ".3gp", ".ogv", ".ts", ".mts"}


def detect_file_type(mime_type_or_path: str | Path | None = None, file_path: str | Path | None = None) -> str:
    """Detect if file is image, video, or audio based on MIME type or extension.

    Supports two calling conventions for backward compatibility:
    - detect_file_type(mime_type, file_path) - new API with MIME type and path
    - detect_file_type(file_path) - old API with just a path

    Args:
        mime_type_or_path: MIME type string (new API) or file path (old API)
        file_path: File path as Path object or string (only when using new API)

    Returns:
        "image", "video", "audio", or "unknown"
    """
    # Handle old API: detect_file_type(file_path)
    if file_path is None and mime_type_or_path is not None:
        # Could be a single Path argument (old API)
        input_path = Path(mime_type_or_path) if not isinstance(mime_type_or_path, Path) else mime_type_or_path
        if input_path.suffix:
            suffix = input_path.suffix.lower()
            if suffix in IMAGE_EXTENSIONS:
                return "image"
            if suffix in VIDEO_EXTENSIONS:
                return "video"
            AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a", ".opus"}
            if suffix in AUDIO_EXTENSIONS:
                return "audio"
        return "unknown"

    # New API: detect_file_type(mime_type, file_path)
    mime_type = mime_type_or_path if isinstance(mime_type_or_path, str) else None
    path_str = str(file_path) if file_path else ""

    # First check MIME type if provided
    if mime_type:
        if mime_type.startswith("image/"):
            return "image"
        if mime_type.startswith("video/"):
            return "video"
        if mime_type.startswith("audio/"):
            return "audio"

    # Fall back to extension detection
    if path_str:
        suffix = Path(path_str).suffix.lower()
        if suffix in IMAGE_EXTENSIONS:
            return "image"
        if suffix in VIDEO_EXTENSIONS:
            return "video"
        AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a", ".opus"}
        if suffix in AUDIO_EXTENSIONS:
            return "audio"

    return "unknown"


async def process_image(
    input_path: Path,
    operation: str,
    **kwargs
) -> Tuple[bool, Optional[Path], Optional[str]]:
    """
    Process an image file.

    Args:
        input_path: Source image path
        operation: One of 'convert', 'compress', 'info'
        **kwargs: Operation-specific arguments

    Returns:
        (success, output_path, error_message)
    """
    valid = await images.validate_image(input_path)
    if not valid:
        return False, None, "Invalid image file"

    if operation == "info":
        info = images.get_image_info_detailed(input_path)
        return True, None, None  # Info returned via logger or separate method

    # Create temp output file
    suffix = f".{kwargs.get('output_format', 'jpg').lower()}"
    if operation == "compress":
        suffix = input_path.suffix

    async with temp_file(suffix=suffix) as output_path:
        if operation == "convert":
            output_format = kwargs.get("output_format", "JPEG").upper()
            quality = kwargs.get("quality", 85)
            success, error = images.convert_image(input_path, output_path, output_format, quality)
        elif operation == "compress":
            quality_preset = kwargs.get("quality_preset", "medium")
            max_dimension = kwargs.get("max_dimension", images.MAX_DIMENSION)
            success, error = images.compress_image(input_path, output_path, quality_preset, max_dimension)
        else:
            return False, None, f"Unknown image operation: {operation}"

        if success:
            return True, output_path, None
        return False, None, error


async def process_video(
    input_path: Path,
    operation: str,
    **kwargs
) -> Tuple[bool, Optional[Path], Optional[str]]:
    """
    Process a video file.

    Args:
        input_path: Source video path
        operation: One of 'compress', 'convert', 'extract_audio', 'info'
        **kwargs: Operation-specific arguments

    Returns:
        (success, output_path, error_message)
    """
    valid = await ffmpeg.validate_video(input_path)
    if not valid:
        return False, None, "Invalid video file"

    if operation == "info":
        info = await ffmpeg.get_video_info(input_path)
        return True, None, None

    # Check FFmpeg availability
    ffmpeg_ok, msg = await ffmpeg.check_ffmpeg()
    if not ffmpeg_ok:
        return False, None, msg

    # Determine output suffix
    if operation == "convert":
        suffix = f".{kwargs.get('output_format', 'mp4').lower()}"
    elif operation == "extract_audio":
        suffix = f".{kwargs.get('output_format', 'mp3').lower()}"
    else:  # compress
        suffix = input_path.suffix

    async with temp_file(suffix=suffix) as output_path:
        if operation == "compress":
            quality_preset = kwargs.get("quality_preset", "medium")
            max_dimension = kwargs.get("max_dimension")
            success, error = await ffmpeg.compress_video(input_path, output_path, quality_preset, max_dimension)
        elif operation == "convert":
            output_format = kwargs.get("output_format", "mp4").lower()
            quality_preset = kwargs.get("quality_preset", "medium")
            success, error = await ffmpeg.convert_video(input_path, output_path, output_format, quality_preset)
        elif operation == "extract_audio":
            output_format = kwargs.get("output_format", "mp3").lower()
            quality_preset = kwargs.get("quality_preset", "medium")
            success, error = await ffmpeg.extract_audio(input_path, output_path, output_format, quality_preset)
        else:
            return False, None, f"Unknown video operation: {operation}"

        if success:
            return True, output_path, None
        return False, None, error


async def process_media(
    input_path: Path,
    operation: str,
    **kwargs
) -> Tuple[bool, Optional[Path], Optional[str]]:
    """
    Main entry point for media processing.

    Args:
        input_path: Source file path
        operation: Operation to perform
        **kwargs: Operation-specific arguments

    Returns:
        (success, output_path, error_message)
    """
    file_type = detect_file_type(input_path)

    if file_type == "image":
        return await process_image(input_path, operation, **kwargs)
    elif file_type == "video":
        return await process_video(input_path, operation, **kwargs)
    else:
        return False, None, f"Unsupported file type: {input_path.suffix}"