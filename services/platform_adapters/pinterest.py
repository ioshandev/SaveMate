import logging
import re
from typing import Optional

from services.platform_adapters.base import BaseAdapter, MediaMetadata
from services.platform_adapters.oembed import oembed_client, OEmbedData

logger = logging.getLogger(__name__)


class PinterestAdapter(BaseAdapter):
    PLATFORM_NAME = "pinterest"
    SUPPORTED_DOMAINS = [
        "pinterest.com",
        "www.pinterest.com",
        "pin.it",
        "br.pinterest.com",
    ]

    # Pinterest oEmbed endpoint
    OEMBED_ENDPOINT = "https://www.pinterest.com/oembed.json?url={url}"

    # URL patterns
    PINTEREST_REGEX = re.compile(
        r"(?:https?://)?"
        r"(?:www\.)?"
        r"(?:"
        r"pinterest\.com/pin/(\d+)"
        r"|pin\.it/([A-Za-z0-9]+)"
        r")"
    )

    def matches(self, url: str) -> bool:
        return bool(self.PINTEREST_REGEX.search(url))

    def can_handle(self, url: str) -> bool:
        """Alias for matches() method."""
        return self.matches(url)

    def extract_pin_id(self, url: str) -> Optional[str]:
        match = self.PINTEREST_REGEX.search(url)
        if match:
            return match.group(1) or match.group(2)
        return None

    async def fetch_metadata(self, url: str) -> Optional[MediaMetadata]:
        # Validate URL security first
        is_valid, error = await self.validate_url(url)
        if not is_valid:
            self.logger.warning("Pinterest URL validation failed: %s", error)
            return None

        pin_id = self.extract_pin_id(url)
        if not pin_id:
            return None

        # Try to fetch oEmbed data
        oembed_data: Optional[OEmbedData] = await oembed_client.fetch(url, self.OEMBED_ENDPOINT)

        if oembed_data:
            # Pinterest is primarily images
            file_type = "video" if oembed_data.type == "video" else "image"

            return self._create_metadata(
                title=oembed_data.title or f"Pinterest Pin ({pin_id})",
                author=oembed_data.author_name,
                author_url=oembed_data.author_url,
                thumbnail_url=oembed_data.thumbnail_url,
                width=oembed_data.width,
                height=oembed_data.height,
                file_type=file_type,
                raw_data={
                    "pin_id": pin_id,
                    "oembed": {
                        "provider_name": oembed_data.provider_name,
                        "provider_url": oembed_data.provider_url,
                        "type": oembed_data.type,
                        "version": oembed_data.version,
                    }
                }
            )

        # Fallback
        self.logger.info("Pinterest oEmbed fetch failed, using fallback: %s", url)
        return self._create_metadata(
            title=f"Pinterest Pin ({pin_id})",
            file_type="image",
            raw_data={"pin_id": pin_id, "note": "Pinterest metadata requires oEmbed endpoint"}
        )

    async def is_authorized(self, url: str) -> bool:
        """
        Pinterest downloads are not authorized via public oEmbed.
        """
        return False


pinterest_adapter = PinterestAdapter()