import logging
import mimetypes
from typing import Optional

import aiohttp

from services.platform_adapters.base import BaseAdapter, MediaMetadata

logger = logging.getLogger(__name__)

# Media file extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".svg", ".heic", ".avif"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv", ".m4v", ".3gp", ".ogv"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac", ".opus", ".wma"}


class DirectAdapter(BaseAdapter):
    PLATFORM_NAME = "direct"
    SUPPORTED_DOMAINS = []  # Matches any URL with media extension

    def __init__(self, timeout: int = 10, max_size: int = 100_000_000):
        super().__init__()
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_size = max_size
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    def matches(self, url: str) -> bool:
        """Check if URL has a media file extension."""
        if not url:
            return False

        # Parse URL and check path extension
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            for ext in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS | AUDIO_EXTENSIONS:
                if path.endswith(ext):
                    return True
        except Exception:
            pass
        return False

    def can_handle(self, url: str) -> bool:
        """Alias for matches() method."""
        return self.matches(url)

    def _detect_file_type(self, url: str, content_type: Optional[str] = None) -> Optional[str]:
        """Detect file type from URL extension or Content-Type header."""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()

            # Check extension first
            for ext in IMAGE_EXTENSIONS:
                if path.endswith(ext):
                    return "image"
            for ext in VIDEO_EXTENSIONS:
                if path.endswith(ext):
                    return "video"
            for ext in AUDIO_EXTENSIONS:
                if path.endswith(ext):
                    return "audio"

            # Fallback to Content-Type
            if content_type:
                if content_type.startswith("image/"):
                    return "image"
                elif content_type.startswith("video/"):
                    return "video"
                elif content_type.startswith("audio/"):
                    return "audio"
        except Exception:
            pass
        return None

    async def fetch_metadata(self, url: str) -> Optional[MediaMetadata]:
        # Validate URL security first
        is_valid, error = await self.validate_url(url)
        if not is_valid:
            self.logger.warning("Direct URL validation failed: %s", error)
            return None

        try:
            session = await self._get_session()
            # Use HEAD request to get metadata without downloading
            async with session.head(url, allow_redirects=True) as resp:
                if resp.status != 200:
                    self.logger.warning("Direct URL HEAD request failed: %s - %s", url, resp.status)
                    return None

                content_type = resp.headers.get("Content-Type", "")
                content_length = resp.headers.get("Content-Length")
                file_size = int(content_length) if content_length and content_length.isdigit() else None

                # Check size limit
                if file_size and file_size > self.max_size:
                    self.logger.warning("Direct URL file too large: %s bytes", file_size)
                    return None

                file_type = self._detect_file_type(url, content_type)
                if not file_type:
                    self.logger.warning("Could not detect file type for: %s", url)
                    return None

                # Extract filename from URL
                from urllib.parse import urlparse
                parsed = urlparse(url)
                file_name = parsed.path.split("/")[-1] if parsed.path else "media"

                return self._create_metadata(
                    title=file_name,
                    file_type=file_type,
                    file_size=file_size,
                    download_allowed=True,
                    download_urls=[url],
                    raw_data={
                        "content_type": content_type,
                        "content_length": file_size,
                    }
                )

        except Exception as e:
            self.logger.warning("Direct URL fetch error for %s: %s", url, e)
            return None

    async def is_authorized(self, url: str) -> bool:
        """
        Direct URLs are authorized if they pass security validation and size checks.
        The actual check happens in fetch_metadata.
        """
        return True


direct_adapter = DirectAdapter()

# Alias for test compatibility
DirectMediaAdapter = DirectAdapter