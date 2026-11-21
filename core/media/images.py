import logging
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image
from config import config

logger = logging.getLogger(__name__)

# Supported formats
SUPPORTED_INPUT_FORMATS = {"JPEG", "JPG", "PNG", "GIF", "WEBP", "BMP", "TIFF", ".JPEG", ".JPG", ".jpeg", ".jpg", "png", "gif", "webp", "bmp", "tiff", "tif", "heic", "avif"}
SUPPORTED_OUTPUT_FORMATS = {"JPEG", "PNG", "WEBP", "GIF", "BMP", "TIFF"}

# Quality presets for compression
COMPRESSION_PRESETS = {
    "high": {"quality": 85},
    "medium": {"quality": 65},
    "low": {"quality": 40},
    "minimal": {"quality": 20},
}

MAX_DIMENSION = 4096


def get_image_info(image_path: Path) -> dict:
    """Get basic information about an image file."""
    try:
        with Image.open(image_path) as img:
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size_bytes": image_path.stat().st_size,
            }
    except Exception as e:
        logger.error("Failed to get image info for %s: %s", image_path, e)
        raise


async def validate_image(image_path: Path | str) -> bool:
    """Validate image file format and size."""
    # Convert string to Path if needed
    image_path = Path(image_path) if isinstance(image_path, str) else image_path

    if not image_path.exists():
        return False

    if image_path.suffix.lower() not in SUPPORTED_INPUT_FORMATS and image_path.suffix[1:].upper() not in SUPPORTED_INPUT_FORMATS:
        return False

    if image_path.stat().st_size > config.max_file_size:
        return False

    try:
        with Image.open(image_path) as img:
            img.verify()
    except Exception:
        return False

    return True


def convert_image(
    input_path: Path,
    output_path: Path,
    output_format: str,
    quality: int = 85,
) -> Tuple[bool, Optional[str]]:
    """
    Convert image to another format.

    Args:
        input_path: Source image path
        output_path: Destination image path
        output_format: Target format (JPEG, PNG, WEBP, etc.)
        quality: Quality for lossy formats (1-100)

    Returns:
        (success, error_message)
    """
    if output_format.upper() not in SUPPORTED_OUTPUT_FORMATS:
        return False, f"Unsupported output format: {output_format}"

    try:
        with Image.open(input_path) as img:
            # Handle transparency for JPEG
            if output_format.upper() == "JPEG" and img.mode in ("RGBA", "LA", "P"):
                # Create white background
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                if img.mode in ("RGBA", "LA"):
                    background.paste(img, mask=img.split()[-1])
                    img = background
                else:
                    img = img.convert("RGB")
            elif output_format.upper() == "JPEG":
                img = img.convert("RGB")

            # Save with appropriate options
            save_kwargs = {"format": output_format.upper()}
            if output_format.upper() in ("JPEG", "WEBP"):
                save_kwargs["quality"] = quality
                save_kwargs["optimize"] = True
            elif output_format.upper() == "PNG":
                save_kwargs["optimize"] = True

            img.save(output_path, **save_kwargs)

        logger.info("Converted %s to %s (%s)", input_path, output_path, output_format)
        return True, None

    except Exception as e:
        logger.error("Image conversion failed: %s", e)
        return False, str(e)


def compress_image(
    input_path: Path,
    output_path: Path,
    quality_preset: str = "medium",
    max_dimension: int = MAX_DIMENSION,
) -> Tuple[bool, Optional[str]]:
    """
    Compress image by reducing quality and/or dimensions.

    Args:
        input_path: Source image path
        output_path: Destination image path
        quality_preset: One of 'high', 'medium', 'low', 'minimal'
        max_dimension: Maximum width/height

    Returns:
        (success, error_message)
    """
    preset = COMPRESSION_PRESETS.get(quality_preset.lower(), {"quality": 65})
    quality = preset["quality"] if isinstance(preset, dict) else preset

    try:
        with Image.open(input_path) as img:
            # Resize if needed
            if img.width > max_dimension or img.height > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                logger.debug("Resized image to %dx%d", img.width, img.height)

            # Handle format-specific compression
            output_format = input_path.suffix[1:].upper()
            if output_format == "JPG":
                output_format = "JPEG"

            if output_format not in SUPPORTED_OUTPUT_FORMATS:
                output_format = "JPEG"

            # Handle transparency for JPEG
            if output_format == "JPEG" and img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                if img.mode in ("RGBA", "LA"):
                    background.paste(img, mask=img.split()[-1])
                    img = background
                else:
                    img = img.convert("RGB")
            elif output_format == "JPEG":
                img = img.convert("RGB")

            save_kwargs = {"format": output_format, "optimize": True}
            if output_format in ("JPEG", "WEBP"):
                save_kwargs["quality"] = quality

            img.save(output_path, **save_kwargs)

        logger.info("Compressed %s to %s (quality=%d)", input_path, output_path, quality)
        return True, None

    except Exception as e:
        logger.error("Image compression failed: %s", e)
        return False, str(e)


def get_image_info_detailed(image_path: Path) -> dict:
    """Get detailed information about an image file."""
    try:
        with Image.open(image_path) as img:
            info = {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size_bytes": image_path.stat().st_size,
                "aspect_ratio": round(img.width / img.height, 2) if img.height > 0 else 0,
                "megapixels": round((img.width * img.height) / 1_000_000, 2),
            }

            # EXIF data
            if hasattr(img, "_getexif") and img._getexif():
                info["has_exif"] = True
            else:
                info["has_exif"] = False

            return info
    except Exception as e:
        logger.error("Failed to get detailed image info for %s: %s", image_path, e)
        raise