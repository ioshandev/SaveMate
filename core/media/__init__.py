"""
Core Media Processing Package

Provides image and video processing capabilities using Pillow and FFmpeg.
"""

from core.media.images import (
    convert_image,
    compress_image,
    get_image_info,
    get_image_info_detailed,
    validate_image,
    SUPPORTED_INPUT_FORMATS,
    SUPPORTED_OUTPUT_FORMATS,
    COMPRESSION_PRESETS,
)
from core.media.ffmpeg import (
    compress_video,
    convert_video,
    extract_audio,
    get_video_info,
    validate_video,
    check_ffmpeg,
    VIDEO_INPUT_FORMATS,
    VIDEO_OUTPUT_FORMATS,
    AUDIO_OUTPUT_FORMATS,
    COMPRESSION_PRESETS as VIDEO_COMPRESSION_PRESETS,
)
from core.media.processor import (
    process_media,
    process_image,
    process_video,
    detect_file_type,
)

__all__ = [
    # Images
    "convert_image",
    "compress_image",
    "get_image_info",
    "get_image_info_detailed",
    "validate_image",
    "SUPPORTED_INPUT_FORMATS",
    "SUPPORTED_OUTPUT_FORMATS",
    "COMPRESSION_PRESETS",
    # FFmpeg
    "compress_video",
    "convert_video",
    "extract_audio",
    "get_video_info",
    "validate_video",
    "check_ffmpeg",
    "VIDEO_INPUT_FORMATS",
    "VIDEO_OUTPUT_FORMATS",
    "AUDIO_OUTPUT_FORMATS",
    "VIDEO_COMPRESSION_PRESETS",
    # Processor
    "process_media",
    "process_image",
    "process_video",
    "detect_file_type",
]