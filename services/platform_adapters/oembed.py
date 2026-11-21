import aiohttp
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class OEmbedData:
    title: Optional[str] = None
    author_name: Optional[str] = None
    author_url: Optional[str] = None
    provider_name: Optional[str] = None
    provider_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    thumbnail_width: Optional[int] = None
    thumbnail_height: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    html: Optional[str] = None
    version: str = "1.0"
    type: str = "video"


class OEmbedClient:
    def __init__(self, timeout: int = 10):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def fetch(self, url: str, endpoint: str) -> Optional[OEmbedData]:
        """
        Fetch oEmbed data from an endpoint.

        Args:
            url: The content URL to fetch metadata for
            endpoint: The oEmbed endpoint URL (with {url} placeholder)

        Returns:
            OEmbedData if successful, None otherwise
        """
        try:
            session = await self._get_session()
            params = {
                "url": url,
                "format": "json",
            }
            full_endpoint = endpoint.replace("{url}", url)
            async with session.get(full_endpoint, params=params) as resp:
                if resp.status != 200:
                    logger.warning("oEmbed request failed: %s - %s", endpoint, resp.status)
                    return None
                data = await resp.json()
                return OEmbedData(
                    title=data.get("title"),
                    author_name=data.get("author_name"),
                    author_url=data.get("author_url"),
                    provider_name=data.get("provider_name"),
                    provider_url=data.get("provider_url"),
                    thumbnail_url=data.get("thumbnail_url"),
                    thumbnail_width=data.get("thumbnail_width"),
                    thumbnail_height=data.get("thumbnail_height"),
                    width=data.get("width"),
                    height=data.get("height"),
                    duration=data.get("duration"),
                    html=data.get("html"),
                    version=data.get("version", "1.0"),
                    type=data.get("type", "video"),
                )
        except Exception as e:
            logger.warning("oEmbed fetch error for %s: %s", url, e)
            return None


oembed_client = OEmbedClient()