import logging
from typing import Optional, List

from services.platform_adapters.base import BaseAdapter, MediaMetadata
from services.platform_adapters.youtube import youtube_adapter
from services.platform_adapters.tiktok import tiktok_adapter
from services.platform_adapters.instagram import instagram_adapter
from services.platform_adapters.facebook import facebook_adapter
from services.platform_adapters.pinterest import pinterest_adapter
from services.platform_adapters.direct import direct_adapter

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """
    Registry for platform adapters.
    Manages adapter detection and metadata fetching.
    """

    def __init__(self):
        # Order matters - more specific adapters should come first
        # Direct adapter should be last as it matches by extension
        self._adapters: List[BaseAdapter] = [
            youtube_adapter,
            tiktok_adapter,
            instagram_adapter,
            facebook_adapter,
            pinterest_adapter,
            direct_adapter,
        ]

    def get_adapter(self, url: str) -> Optional[BaseAdapter]:
        """Find the first adapter that matches the URL."""
        for adapter in self._adapters:
            if adapter.matches(url):
                logger.debug("Adapter matched: %s for URL: %s", adapter.PLATFORM_NAME, url)
                return adapter
        logger.debug("No adapter matched for URL: %s", url)
        return None

    def detect_platform(self, url: str) -> Optional[str]:
        """Detect platform name from URL."""
        adapter = self.get_adapter(url)
        return adapter.PLATFORM_NAME if adapter else None

    async def fetch_metadata(self, url: str) -> Optional[MediaMetadata]:
        """
        Fetch metadata using the appropriate adapter.
        """
        adapter = self.get_adapter(url)
        if not adapter:
            logger.warning("No adapter found for URL: %s", url)
            return None

        try:
            return await adapter.fetch_metadata(url)
        except Exception as e:
            logger.error("Error fetching metadata with %s: %s", adapter.PLATFORM_NAME, e)
            return None

    def get_all_adapters(self) -> List[BaseAdapter]:
        """Get all registered adapters."""
        return self._adapters.copy()

    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platform names."""
        return [adapter.PLATFORM_NAME for adapter in self._adapters]


# Global registry instance
adapter_registry = AdapterRegistry()