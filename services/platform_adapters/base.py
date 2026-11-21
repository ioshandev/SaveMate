import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from core.security import validate_url_security

logger = logging.getLogger(__name__)


@dataclass
class MediaMetadata:
    """Standardized media metadata returned by all adapters."""
    platform: str
    title: Optional[str] = None
    author: Optional[str] = None
    author_url: Optional[str] = None
    duration: Optional[float] = None
    thumbnail_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    download_allowed: bool = False
    download_urls: Optional[list[str]] = None
    file_type: Optional[str] = None  # 'image', 'video', 'audio'
    file_size: Optional[int] = None
    raw_data: Optional[dict] = None


class BaseAdapter(ABC):
    """
    Abstract base class for platform adapters.

    Each adapter handles a specific platform (YouTube, TikTok, etc.) and provides
    metadata extraction via official endpoints (oEmbed, Graph API, etc.).
    """

    PLATFORM_NAME: str = "unknown"
    SUPPORTED_DOMAINS: list[str] = []

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.PLATFORM_NAME}")

    @abstractmethod
    def matches(self, url: str) -> bool:
        """Check if this adapter handles the given URL."""
        pass

    @abstractmethod
    async def fetch_metadata(self, url: str) -> Optional[MediaMetadata]:
        """
        Fetch metadata for the given URL.

        Returns None if the URL is not valid for this platform or if metadata
        cannot be fetched.
        """
        pass

    async def validate_url(self, url: str) -> tuple[bool, str | None]:
        """
        Validate URL for security (SSRF protection).

        Returns (is_valid, error_message).
        """
        return await validate_url_security(url)

    async def is_authorized(self, url: str) -> bool:
        """
        Check if download is authorized for this URL.

        Default implementation returns False. Override in subclasses that
        support authorized downloads.
        """
        return False

    def _create_metadata(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        author_url: Optional[str] = None,
        duration: Optional[float] = None,
        thumbnail_url: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        download_allowed: bool = False,
        download_urls: Optional[list[str]] = None,
        file_type: Optional[str] = None,
        file_size: Optional[int] = None,
        raw_data: Optional[dict] = None,
    ) -> MediaMetadata:
        """Helper to create MediaMetadata with platform name pre-filled."""
        return MediaMetadata(
            platform=self.PLATFORM_NAME,
            title=title,
            author=author,
            author_url=author_url,
            duration=duration,
            thumbnail_url=thumbnail_url,
            width=width,
            height=height,
            download_allowed=download_allowed,
            download_urls=download_urls,
            file_type=file_type,
            file_size=file_size,
            raw_data=raw_data,
        )