import asyncio
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List

from config import config

logger = logging.getLogger(__name__)

# Check if ffmpeg is available
FFMPEG_PATH = shutil.which("ffmpeg")
FFPROBE_PATH = shutil.which("ffprobe")

if not FFMPEG_PATH:
    logger.warning("FFmpeg not found in PATH. Video processing will be unavailable.")
if not FFPROBE_PATH:
    logger.warning("FFprobe not found in PATH. Video metadata extraction will be unavailable.")

# Supported formats
VIDEO_INPUT_FORMATS = {"mp4", "mov", ".mp4", ".mov", "avi", ".avi", "mkv", ".mkv", "webm", ".webm", "flv", ".flv", "wmv", ".wmv", "m4v", ".m4v", "3gp", ".3gp", "ogv", ".ogv", "ts", ".ts", "mts", ".mts"}
VIDEO_OUTPUT_FORMATS = {"mp4", "mov", "mkv", "webm", "avi"}
VIDEO_INPUT_FORMATS_LOWER = {f".{f}" for f in VIDEO_OUTPUT_FORMATS}
AUDIO_OUTPUT_FORMATS = {"mp3", "aac", "ogg", "flac", "wav", "m4a", "opus"}

# Compression presets (CRF values - lower = better quality)
VIDEO_COMPRESSION_PRESETS = {
    "high": {"crf": 18, "preset": "medium"},      # Near lossless
    "medium": {"crf": 23, "preset": "medium"},    # Default/good balance
    "low": {"crf": 28, "preset": "medium"},       # Smaller file, visible quality loss
    "minimal": {"crf": 32, "preset": "medium"},   # Maximum compression
}

# Alias for test compatibility
COMPRESSION_PRESETS = VIDEO_COMPRESSION_PRESETS

# Audio bitrates for extraction
AUDIO_BITRATES = {
    "high": "320k",
    "medium": "192k",
    "low": "128k",
    "minimal": "96k",
}


async def check_ffmpeg() -> Tuple[bool, str]:
    """Check if FFmpeg is available and working."""
    if not FFMPEG_PATH:
        return False, "FFmpeg not installed"
    if not FFPROBE_PATH:
        return False, "FFprobe not installed"

    try:
        proc = await asyncio.create_subprocess_exec(
            FFMPEG_PATH, "-version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            version_line = stdout.decode().split("\n")[0]
            return True, version_line
        return False, f"FFmpeg error: {stderr.decode()}"
    except Exception as e:
        return False, f"FFmpeg check failed: {e}"


async def get_video_info(video_path: Path) -> dict:
    """Get detailed video information using ffprobe."""
    if not FFPROBE_PATH:
        raise RuntimeError("FFprobe not available")

    try:
        cmd = [
            FFPROBE_PATH,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(video_path),
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(f"ffprobe failed: {stderr.decode()}")

        import json
        data = json.loads(stdout.decode())

        # Extract relevant info
        format_info = data.get("format", {})
        streams = data.get("streams", [])

        video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

        info = {
            "duration": float(format_info.get("duration", 0)),
            "size_bytes": int(format_info.get("size", 0)),
            "bitrate": int(format_info.get("bit_rate", 0)),
            "format_name": format_info.get("format_name", ""),
            "format_long_name": format_info.get("format_long_name", ""),
        }

        if video_stream:
            info.update({
                "width": video_stream.get("width", 0),
                "height": video_stream.get("height", 0),
                "codec": video_stream.get("codec_name", ""),
                "codec_long": video_stream.get("codec_long_name", ""),
                "fps": eval(video_stream.get("r_frame_rate", "0/1")) if video_stream.get("r_frame_rate") else 0,
                "has_video": True,
            })
        else:
            info["has_video"] = False

        if audio_stream:
            info.update({
                "audio_codec": audio_stream.get("codec_name", ""),
                "audio_channels": audio_stream.get("channels", 0),
                "audio_sample_rate": audio_stream.get("sample_rate", 0),
                "has_audio": True,
            })
        else:
            info["has_audio"] = False

        return info

    except Exception as e:
        logger.error("Failed to get video info for %s: %s", video_path, e)
        raise


async def compress_video(
    input_path: Path,
    output_path: Path,
    quality_preset: str = "medium",
    max_dimension: Optional[int] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Compress video using FFmpeg.

    Args:
        input_path: Source video path
        output_path: Destination video path
        quality_preset: One of 'high', 'medium', 'low', 'minimal'
        max_dimension: Maximum width/height (optional)

    Returns:
        (success, error_message)
    """
    if not FFMPEG_PATH:
        return False, "FFmpeg not available"

    preset = VIDEO_COMPRESSION_PRESETS.get(quality_preset.lower(), {"crf": 23, "preset": "medium"})
    crf = preset["crf"] if isinstance(preset, dict) else preset
    video_preset = preset.get("preset", "medium") if isinstance(preset, dict) else "medium"

    try:
        # Build filter chain
        filters = []
        if max_dimension:
            filters.append(f"scale='if(gt(iw,ih),{max_dimension},-2)':'if(gt(iw,ih),-2,{max_dimension})'")

        filter_str = ",".join(filters) if filters else None

        cmd = [
            FFMPEG_PATH,
            "-y",  # Overwrite output
            "-i", str(input_path),
            "-c:v", "libx264",
            "-preset", video_preset,
            "-crf", str(crf),
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",  # Web optimization
        ]

        if filter_str:
            cmd.extend(["-vf", filter_str])

        cmd.append(str(output_path))

        logger.debug("Running FFmpeg compress: %s", " ".join(cmd))

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error = stderr.decode()
            logger.error("FFmpeg compress failed: %s", error)
            return False, error

        logger.info("Compressed %s to %s (CRF=%d)", input_path, output_path, crf)
        return True, None

    except Exception as e:
        logger.error("Video compression exception: %s", e)
        return False, str(e)


async def convert_video(
    input_path: Path,
    output_path: Path,
    output_format: str,
    quality_preset: str = "medium",
) -> Tuple[bool, Optional[str]]:
    """
    Convert video to another format.

    Args:
        input_path: Source video path
        output_path: Destination video path
        output_format: Target format (mp4, mov, mkv, webm, avi)
        quality_preset: Quality preset for re-encoding

    Returns:
        (success, error_message)
    """
    if not FFMPEG_PATH:
        return False, "FFmpeg not available"

    output_format = output_format.lower()
    if output_format not in VIDEO_OUTPUT_FORMATS:
        return False, f"Unsupported output format: {output_format}"

    preset = VIDEO_COMPRESSION_PRESETS.get(quality_preset.lower(), {"crf": 23, "preset": "medium"})
    crf = preset["crf"] if isinstance(preset, dict) else preset
    video_preset = preset.get("preset", "medium") if isinstance(preset, dict) else "medium"

    # Codec selection based on format
    video_codec = "libx264"
    if output_format == "webm":
        video_codec = "libvpx-vp9"
    elif output_format == "mkv":
        video_codec = "libx264"  # MKV supports H.264

    try:
        cmd = [
            FFMPEG_PATH,
            "-y",
            "-i", str(input_path),
            "-c:v", video_codec,
            "-preset", video_preset,
            "-crf", str(crf),
            "-c:a", "aac" if output_format != "webm" else "libopus",
            "-b:a", "128k",
            "-movflags", "+faststart",
            str(output_path),
        ]

        logger.debug("Running FFmpeg convert: %s", " ".join(cmd))

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error = stderr.decode()
            logger.error("FFmpeg convert failed: %s", error)
            return False, error

        logger.info("Converted %s to %s (%s)", input_path, output_path, output_format)
        return True, None

    except Exception as e:
        logger.error("Video conversion exception: %s", e)
        return False, str(e)


async def extract_audio(
    input_path: Path,
    output_path: Path,
    output_format: str = "mp3",
    quality_preset: str = "medium",
) -> Tuple[bool, Optional[str]]:
    """
    Extract audio from video.

    Args:
        input_path: Source video path
        output_path: Destination audio path
        output_format: Target audio format (mp3, aac, ogg, flac, wav, m4a, opus)
        quality_preset: Audio quality preset

    Returns:
        (success, error_message)
    """
    if not FFMPEG_PATH:
        return False, "FFmpeg not available"

    output_format = output_format.lower()
    if output_format not in AUDIO_OUTPUT_FORMATS:
        return False, f"Unsupported audio output format: {output_format}"

    bitrate = AUDIO_BITRATES.get(quality_preset.lower(), "192k")

    # Codec selection
    codec_map = {
        "mp3": "libmp3lame",
        "aac": "aac",
        "ogg": "libvorbis",
        "flac": "flac",
        "wav": "pcm_s16le",
        "m4a": "aac",
        "opus": "libopus",
    }
    codec = codec_map.get(output_format, "libmp3lame")

    try:
        cmd = [
            FFMPEG_PATH,
            "-y",
            "-i", str(input_path),
            "-vn",  # No video
            "-c:a", codec,
        ]

        if output_format in ("mp3", "aac", "ogg", "opus", "m4a"):
            cmd.extend(["-b:a", bitrate])

        cmd.append(str(output_path))

        logger.debug("Running FFmpeg extract audio: %s", " ".join(cmd))

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error = stderr.decode()
            logger.error("FFmpeg audio extraction failed: %s", error)
            return False, error

        logger.info("Extracted audio from %s to %s (%s)", input_path, output_path, output_format)
        return True, None

    except Exception as e:
        logger.error("Audio extraction exception: %s", e)
        return False, str(e)


async def validate_video(video_path: Path | str) -> bool:
    """Validate video file format and size."""
    # Convert string to Path if needed
    video_path = Path(video_path) if isinstance(video_path, str) else video_path

    if not video_path.exists():
        return False

    if video_path.suffix.lower() not in VIDEO_INPUT_FORMATS and video_path.suffix[1:].lower() not in VIDEO_INPUT_FORMATS:
        return False

    if video_path.stat().st_size > config.max_file_size:
        return False

    return True