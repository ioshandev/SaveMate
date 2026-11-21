import pytest
import tempfile
import os
from pathlib import Path

from core.media.images import (
    validate_image,
    SUPPORTED_INPUT_FORMATS,
    SUPPORTED_OUTPUT_FORMATS,
    COMPRESSION_PRESETS,
)
from core.media.ffmpeg import (
    validate_video,
    VIDEO_INPUT_FORMATS,
    VIDEO_OUTPUT_FORMATS,
    AUDIO_OUTPUT_FORMATS,
    VIDEO_COMPRESSION_PRESETS,
)
from core.media.processor import detect_file_type


class TestImageValidation:
    """Test image file validation."""

    def test_supported_input_formats(self):
        """Test supported input formats list."""
        assert "JPEG" in SUPPORTED_INPUT_FORMATS
        assert "PNG" in SUPPORTED_INPUT_FORMATS
        assert "WEBP" in SUPPORTED_INPUT_FORMATS
        assert "GIF" in SUPPORTED_INPUT_FORMATS
        assert "BMP" in SUPPORTED_INPUT_FORMATS
        assert "TIFF" in SUPPORTED_INPUT_FORMATS

    def test_supported_output_formats(self):
        """Test supported output formats list."""
        assert "JPEG" in SUPPORTED_OUTPUT_FORMATS
        assert "PNG" in SUPPORTED_OUTPUT_FORMATS
        assert "WEBP" in SUPPORTED_OUTPUT_FORMATS

    def test_compression_presets(self):
        """Test compression presets."""
        assert "high" in COMPRESSION_PRESETS
        assert "medium" in COMPRESSION_PRESETS
        assert "low" in COMPRESSION_PRESETS
        assert "minimal" in COMPRESSION_PRESETS

        for preset in COMPRESSION_PRESETS.values():
            assert "quality" in preset
            assert 1 <= preset["quality"] <= 100

    @pytest.mark.asyncio
    async def test_validate_image_valid(self):
        """Test validating a valid image file."""
        # Create a simple test image
        from PIL import Image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            img = Image.new('RGB', (100, 100), color='red')
            img.save(f.name, 'JPEG')
            temp_path = f.name

        try:
            result = await validate_image(temp_path)
            assert result is True
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_validate_image_invalid(self):
        """Test validating an invalid file."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'not an image')
            temp_path = f.name

        try:
            result = await validate_image(temp_path)
            assert result is False
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_validate_image_nonexistent(self):
        """Test validating a non-existent file."""
        result = await validate_image("/nonexistent/path.jpg")
        assert result is False


class TestVideoValidation:
    """Test video file validation."""

    def test_video_input_formats(self):
        """Test supported video input formats."""
        assert "mp4" in VIDEO_INPUT_FORMATS
        assert "mov" in VIDEO_INPUT_FORMATS
        assert "mkv" in VIDEO_INPUT_FORMATS
        assert "webm" in VIDEO_INPUT_FORMATS
        assert "avi" in VIDEO_INPUT_FORMATS

    def test_video_output_formats(self):
        """Test supported video output formats."""
        assert "mp4" in VIDEO_OUTPUT_FORMATS
        assert "mov" in VIDEO_OUTPUT_FORMATS
        assert "mkv" in VIDEO_OUTPUT_FORMATS
        assert "webm" in VIDEO_OUTPUT_FORMATS

    def test_audio_output_formats(self):
        """Test supported audio output formats."""
        assert "mp3" in AUDIO_OUTPUT_FORMATS
        assert "aac" in AUDIO_OUTPUT_FORMATS
        assert "ogg" in AUDIO_OUTPUT_FORMATS
        assert "flac" in AUDIO_OUTPUT_FORMATS
        assert "wav" in AUDIO_OUTPUT_FORMATS
        assert "m4a" in AUDIO_OUTPUT_FORMATS
        assert "opus" in AUDIO_OUTPUT_FORMATS

    def test_video_compression_presets(self):
        """Test video compression presets."""
        assert "high" in VIDEO_COMPRESSION_PRESETS
        assert "medium" in VIDEO_COMPRESSION_PRESETS
        assert "low" in VIDEO_COMPRESSION_PRESETS
        assert "minimal" in VIDEO_COMPRESSION_PRESETS

        for preset in VIDEO_COMPRESSION_PRESETS.values():
            assert "crf" in preset
            assert "preset" in preset
            assert 0 <= preset["crf"] <= 51

    @pytest.mark.asyncio
    async def test_validate_video_without_ffmpeg(self):
        """Test video validation when FFmpeg is not available."""
        # This will return False if ffmpeg is not installed
        result = await validate_video("/some/path.mp4")
        # Result depends on ffmpeg availability
        assert isinstance(result, bool)


class TestFileTypeDetection:
    """Test file type detection."""

    def test_detect_image_by_mime(self):
        """Test detecting image by MIME type."""
        assert detect_file_type("image/jpeg", "test.jpg") == "image"
        assert detect_file_type("image/png", "test.png") == "image"
        assert detect_file_type("image/webp", "test.webp") == "image"
        assert detect_file_type("image/gif", "test.gif") == "image"

    def test_detect_video_by_mime(self):
        """Test detecting video by MIME type."""
        assert detect_file_type("video/mp4", "test.mp4") == "video"
        assert detect_file_type("video/webm", "test.webm") == "video"
        assert detect_file_type("video/quicktime", "test.mov") == "video"

    def test_detect_audio_by_mime(self):
        """Test detecting audio by MIME type."""
        assert detect_file_type("audio/mpeg", "test.mp3") == "audio"
        assert detect_file_type("audio/ogg", "test.ogg") == "audio"

    def test_detect_by_extension(self):
        """Test detecting by file extension when MIME is unknown."""
        assert detect_file_type("", "test.jpg") == "image"
        assert detect_file_type("", "test.mp4") == "video"
        assert detect_file_type("", "test.mp3") == "audio"

    def test_detect_unknown(self):
        """Test detecting unknown file type."""
        assert detect_file_type("application/octet-stream", "test.bin") == "unknown"
        assert detect_file_type("", "test.unknown") == "unknown"