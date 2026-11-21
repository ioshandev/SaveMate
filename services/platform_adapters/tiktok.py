import logging
import re
from typing import Optional

from services.platform_adapters.base import BaseAdapter, MediaMetadata

logger = logging.getLogger(__name__)


class TikTokAdapter(BaseAdapter):
    PLATFORM_NAME = "tiktok"
    SUPPORTED_DOMAINS = [
        "tiktok.com",
        "www.tiktok.com",
        "vt.tiktok.com",
        "vm.tiktok.com",
        "m.tiktok.com",
    ]

    # TikTok URL patterns
    TIKTOK_REGEX = re.compile(
        r"(?:https?://)?"
        r"(?:www\.)?"
        r"(?:"
        r"tiktok\.com/@([^/]+)/(?:video|photo)/(\d+)"
        r"|vt\.tiktok\.com/([A-Za-z0-9]+)"
        r"|vm\.tiktok\.com/([A-Za-z0-9]+)"
        r")"
    )

    def matches(self, url: str) -> bool:
        return bool(self.TIKTOK_REGEX.search(url))

    def can_handle(self, url: str) -> bool:
        """Alias for matches() method."""
        return self.matches(url)

    def extract_video_id(self, url: str) -> Optional[str]:
        match = self.TIKTOK_REGEX.search(url)
        if match:
            # Group 2 is the video ID for standard URLs, group 3/4 for short URLs
            return match.group(2) or match.group(3) or match.group(4)
        return None

    async def fetch_metadata(self, url: str) -> Optional[MediaMetadata]:
        # Validate URL security first
        is_valid, error = await self.validate_url(url)
        if not is_valid:
            self.logger.warning("TikTok URL validation failed: %s", error)
            return None

        video_id = self.extract_video_id(url)
        if not video_id:
            return None

        # TikTok doesn't have a public oEmbed endpoint
        # We'll provide basic metadata and direct to original
        self.logger.info("TikTok URL detected, providing basic metadata: %s", url)

        return self._create_metadata(
            title=f"TikTok Video ({video_id})",
            author="@unknown",
            file_type="video",
            raw_data={"video_id": video_id, "note": "TikTok metadata requires official API"}
        )

    async def is_authorized(self, url: str) -> bool:
        """
        TikTok downloads are not authorized via public APIs.
        """
        return False


tiktok_adapter = TikTokAdapter()