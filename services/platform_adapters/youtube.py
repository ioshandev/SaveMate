import logging
import re
from typing import Optional

from services.platform_adapters.base import BaseAdapter, MediaMetadata
from services.platform_adapters.oembed import oembed_client, OEmbedData

logger = logging.getLogger(__name__)


class YouTubeAdapter(BaseAdapter):
    PLATFORM_NAME = "youtube"
    SUPPORTED_DOMAINS = [
        "youtube.com",
        "www.youtube.com",
        "youtu.be",
        "m.youtube.com",
        "music.youtube.com",
    ]

    # YouTube oEmbed endpoint
    OEMBED_ENDPOINT = "https://www.youtube.com/oembed?url={url}&format=json"

    # URL patterns
    YOUTUBE_REGEX = re.compile(
        r"(?:https?://)?"
        r"(?:www\.)?"
        r"(?:"
        r"youtube\.com/(?:watch\?v=|embed/|v/|shorts/|live/)"
        r"|youtu\.be/"
        r"|music\.youtube\.com/(?:watch\?v=|playlist\?list=)"
        r")"
        r"([a-zA-Z0-9_-]+)"
    )

    def matches(self, url: str) -> bool:
        return bool(self.YOUTUBE_REGEX.search(url))

    def can_handle(self, url: str) -> bool:
        """Alias for matches() method."""
        return self.matches(url)

    def extract_video_id(self, url: str) -> Optional[str]:
        match = self.YOUTUBE_REGEX.search(url)
        if match:
            return match.group(1)
        return None

    async def fetch_metadata(self, url: str) -> Optional[MediaMetadata]:
        # Validate URL security first
        is_valid, error = await self.validate_url(url)
        if not is_valid:
            self.logger.warning("YouTube URL validation failed: %s", error)
            return None

        video_id = self.extract_video_id(url)
        if not video_id:
            return None

        # Fetch oEmbed data
        oembed_data: Optional[OEmbedData] = await oembed_client.fetch(url, self.OEMBED_ENDPOINT)

        if oembed_data:
            # Extract thumbnail - YouTube provides multiple thumbnail sizes
            thumbnail_url = oembed_data.thumbnail_url
            if thumbnail_url and "i.ytimg.com" in thumbnail_url:
                # Try to get maxres thumbnail
                thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"

            return self._create_metadata(
                title=oembed_data.title,
                author=oembed_data.author_name,
                author_url=oembed_data.author_url,
                thumbnail_url=thumbnail_url,
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

        # Fallback: create minimal metadata with just video ID
        self.logger.info("oEmbed fetch failed for YouTube URL, using fallback: %s", url)
        return self._create_metadata(
            title=f"YouTube Video ({video_id})",
            thumbnail_url=f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            file_type="video",
            raw_data={"video_id": video_id}
        )

    async def is_authorized(self, url: str) -> bool:
        """
        YouTube downloads are generally not authorized via official APIs.
        Returns False - users should be directed to the original content.
        """
        return False


youtube_adapter = YouTubeAdapter()