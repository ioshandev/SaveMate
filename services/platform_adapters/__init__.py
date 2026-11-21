"""
Platform Adapters Package

Provides adapters for extracting metadata from various platforms:
- YouTube
- TikTok
- Instagram
- Facebook
- Pinterest
- Direct media URLs
"""

from services.platform_adapters.base import BaseAdapter, MediaMetadata
from services.platform_adapters.registry import adapter_registry, AdapterRegistry
from services.platform_adapters.youtube import youtube_adapter
from services.platform_adapters.tiktok import tiktok_adapter
from services.platform_adapters.instagram import instagram_adapter
from services.platform_adapters.facebook import facebook_adapter
from services.platform_adapters.pinterest import pinterest_adapter
from services.platform_adapters.direct import direct_adapter
from services.platform_adapters.oembed import OEmbedClient, OEmbedData, oembed_client

__all__ = [
    "BaseAdapter",
    "MediaMetadata",
    "adapter_registry",
    "AdapterRegistry",
    "youtube_adapter",
    "tiktok_adapter",
    "instagram_adapter",
    "facebook_adapter",
    "pinterest_adapter",
    "direct_adapter",
    "OEmbedClient",
    "OEmbedData",
    "oembed_client",
]