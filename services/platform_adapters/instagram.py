import logging
import re
from typing import Optional

from services.platform_adapters.base import BaseAdapter, MediaMetadata
from services.platform_adapters.oembed import oembed_client, OEmbedData

logger = logging.getLogger(__name__)


class InstagramAdapter(BaseAdapter):
    PLATFORM_NAME = "instagram"
    SUPPORTED_DOMAINS = [
        "instagram.com",
        "www.instagram.com",
    ]

    # Instagram oEmbed endpoint (via Facebook)
    OEMBED_ENDPOINT = "https://graph.facebook.com/v18.0/instagram_oembed?url={url}&format=json"

    # URL patterns
    INSTAGRAM_REGEX = re.compile(
        r"(?:https?://)?"
        r"(?:www\.)?"
        r"instagram\.com/"
        r"(?:"
        r"p/([A-Za-z0-9_-]+)"  # posts
        r"|reel/([A-Za-z0-9_-]+)"  # reels
        r"|tv/([A-Za-z0-9_-]+)"  # IGTV
        r"|stories/[^/]+/(\d+)"  # stories
        r")"
    )

    def matches(self, url: str) -> bool:
        return bool(self.INSTAGRAM_REGEX.search(url))

    def can_handle(self, url: str) -> bool:
        """Alias for matches() method."""
        return self.matches(url)

    def extract_media_id(self, url: str) -> Optional[str]:
        match = self.INSTAGRAM_REGEX.search(url)
        if match:
            # Return first non-None group
            for group in match.groups():
                if group:
                    return group
        return None

    async def fetch_metadata(self, url: str) -> Optional[MediaMetadata]:
        # Validate URL security first
        is_valid, error = await self.validate_url(url)
        if not is_valid:
            self.logger.warning("Instagram URL validation failed: %s", error)
            return None

        media_id = self.extract_media_id(url)
        if not media_id:
            return None

        # Try to fetch oEmbed data
        oembed_data: Optional[OEmbedData] = await oembed_client.fetch(url, self.OEMBED_ENDPOINT)

        if oembed_data:
            # Determine file type from oEmbed
            file_type = "image"
            if oembed_data.type == "video":
                file_type = "video"

            return self._create_metadata(
                title=oembed_data.title or f"Instagram Post ({media_id})",
                author=oembed_data.author_name,
                author_url=oembed_data.author_url,
                thumbnail_url=oembed_data.thumbnail_url,
                width=oembed_data.width,
                height=oembed_data.height,
                duration=oembed_data.duration,
                file_type=file_type,
                raw_data={
                    "media_id": media_id,
                    "oembed": {
                        "provider_name": oembed_data.provider_name,
                        "provider_url": oembed_data.provider_url,
                        "type": oembed_data.type,
                        "version": oembed_data.version,
                    }
                }
            )

        # Fallback
        self.logger.info("Instagram oEmbed fetch failed, using fallback: %s", url)
        return self._create_metadata(
            title=f"Instagram Post ({media_id})",
            file_type="image",
            raw_data={"media_id": media_id, "note": "Instagram metadata requires oEmbed endpoint"}
        )

    async def is_authorized(self, url: str) -> bool:
        """
        Instagram downloads are not authorized via public oEmbed.
        """
        return False


instagram_adapter = InstagramAdapter()