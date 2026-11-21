import logging
import re
from typing import Optional

from services.platform_adapters.base import BaseAdapter, MediaMetadata
from services.platform_adapters.oembed import oembed_client, OEmbedData

logger = logging.getLogger(__name__)


class FacebookAdapter(BaseAdapter):
    PLATFORM_NAME = "facebook"
    SUPPORTED_DOMAINS = [
        "facebook.com",
        "www.facebook.com",
        "fb.watch",
        "m.facebook.com",
        "mbasic.facebook.com",
    ]

    # Facebook oEmbed endpoint
    OEMBED_ENDPOINT = "https://www.facebook.com/plugins/video/oembed.json/?url={url}"

    # URL patterns
    FACEBOOK_REGEX = re.compile(
        r"(?:https?://)?"
        r"(?:www\.)?"
        r"(?:"
        r"facebook\.com/(?:[^/]+/)?(?:videos|reel|video\.php\?v=)/?(\d+)"
        r"|facebook\.com/watch\?v=(\d+)"
        r"|fb\.watch/([A-Za-z0-9_-]+)"
        r")"
    )

    def matches(self, url: str) -> bool:
        return bool(self.FACEBOOK_REGEX.search(url))

    def can_handle(self, url: str) -> bool:
        """Alias for matches() method."""
        return self.matches(url)

    def extract_video_id(self, url: str) -> Optional[str]:
        match = self.FACEBOOK_REGEX.search(url)
        if match:
            # Group 1: videos/reel/video.php, Group 2: watch?v=, Group 3: fb.watch
            return match.group(1) or match.group(2) or match.group(3)
        return None

    async def fetch_metadata(self, url: str) -> Optional[MediaMetadata]:
        # Validate URL security first
        is_valid, error = await self.validate_url(url)
        if not is_valid:
            self.logger.warning("Facebook URL validation failed: %s", error)
            return None

        video_id = self.extract_video_id(url)
        if not video_id:
            return None

        # Try to fetch oEmbed data
        oembed_data: Optional[OEmbedData] = await oembed_client.fetch(url, self.OEMBED_ENDPOINT)

        if oembed_data:
            return self._create_metadata(
                title=oembed_data.title or f"Facebook Video ({video_id})",
                author=oembed_data.author_name,
                author_url=oembed_data.author_url,
                thumbnail_url=oembed_data.thumbnail_url,
                width=oembed_data.width,
                height=oembed_data.height,
                duration=oembed_data.duration,
                file_type="video",
                raw_data={
                    "video_id": video_id,
                    "oembed": {
                        "provider_name": oembed_data.provider_name,
                        "provider_url": oembed_data.provider_url,
                        "type": oembed_data.type,
                        "version": oembed_data.version,
                    }
                }
            )

        # Fallback
        self.logger.info("Facebook oEmbed fetch failed, using fallback: %s", url)
        return self._create_metadata(
            title=f"Facebook Video ({video_id})",
            file_type="video",
            raw_data={"video_id": video_id, "note": "Facebook metadata requires oEmbed endpoint"}
        )

    async def is_authorized(self, url: str) -> bool:
        """
        Facebook downloads are not authorized via public oEmbed.
        """
        return False


facebook_adapter = FacebookAdapter()