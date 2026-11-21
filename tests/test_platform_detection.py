import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from services.platform_adapters.registry import adapter_registry
from services.platform_adapters.youtube import YouTubeAdapter
from services.platform_adapters.tiktok import TikTokAdapter
from services.platform_adapters.instagram import InstagramAdapter
from services.platform_adapters.facebook import FacebookAdapter
from services.platform_adapters.pinterest import PinterestAdapter
from services.platform_adapters.direct import DirectMediaAdapter


class TestPlatformDetection:
    """Test platform adapter detection."""

    @pytest.mark.asyncio
    async def test_youtube_detection(self):
        """Test YouTube URL detection."""
        adapter = adapter_registry.get_adapter("https://youtube.com/watch?v=abc123")
        assert isinstance(adapter, YouTubeAdapter)

        adapter = adapter_registry.get_adapter("https://youtu.be/abc123")
        assert isinstance(adapter, YouTubeAdapter)

        adapter = adapter_registry.get_adapter("https://www.youtube.com/shorts/abc123")
        assert isinstance(adapter, YouTubeAdapter)

    @pytest.mark.asyncio
    async def test_tiktok_detection(self):
        """Test TikTok URL detection."""
        adapter = adapter_registry.get_adapter("https://tiktok.com/@user/video/123")
        assert isinstance(adapter, TikTokAdapter)

        adapter = adapter_registry.get_adapter("https://www.tiktok.com/@user/video/123")
        assert isinstance(adapter, TikTokAdapter)

        adapter = adapter_registry.get_adapter("https://vm.tiktok.com/abc123")
        assert isinstance(adapter, TikTokAdapter)

    @pytest.mark.asyncio
    async def test_instagram_detection(self):
        """Test Instagram URL detection."""
        adapter = adapter_registry.get_adapter("https://instagram.com/p/abc123")
        assert isinstance(adapter, InstagramAdapter)

        adapter = adapter_registry.get_adapter("https://www.instagram.com/reel/abc123")
        assert isinstance(adapter, InstagramAdapter)

        adapter = adapter_registry.get_adapter("https://instagram.com/tv/abc123")
        assert isinstance(adapter, InstagramAdapter)

    @pytest.mark.asyncio
    async def test_facebook_detection(self):
        """Test Facebook URL detection."""
        adapter = adapter_registry.get_adapter("https://facebook.com/watch?v=123")
        assert isinstance(adapter, FacebookAdapter)

        adapter = adapter_registry.get_adapter("https://www.facebook.com/reel/123")
        assert isinstance(adapter, FacebookAdapter)

        adapter = adapter_registry.get_adapter("https://fb.watch/abc123")
        assert isinstance(adapter, FacebookAdapter)

    @pytest.mark.asyncio
    async def test_pinterest_detection(self):
        """Test Pinterest URL detection."""
        adapter = adapter_registry.get_adapter("https://pinterest.com/pin/123")
        assert isinstance(adapter, PinterestAdapter)

        adapter = adapter_registry.get_adapter("https://www.pinterest.com/pin/123")
        assert isinstance(adapter, PinterestAdapter)

        adapter = adapter_registry.get_adapter("https://pin.it/abc123")
        assert isinstance(adapter, PinterestAdapter)

    @pytest.mark.asyncio
    async def test_direct_media_detection(self):
        """Test direct media URL detection."""
        adapter = adapter_registry.get_adapter("https://example.com/video.mp4")
        assert isinstance(adapter, DirectMediaAdapter)

        adapter = adapter_registry.get_adapter("https://example.com/image.jpg")
        assert isinstance(adapter, DirectMediaAdapter)

        adapter = adapter_registry.get_adapter("https://cdn.example.com/audio.mp3")
        assert isinstance(adapter, DirectMediaAdapter)


class TestAdapterPatterns:
    """Test adapter URL patterns."""

    def test_youtube_patterns(self):
        """Test YouTube URL patterns."""
        adapter = YouTubeAdapter()
        urls = [
            "https://youtube.com/watch?v=abc",
            "https://youtu.be/abc",
            "https://www.youtube.com/shorts/abc",
            "https://youtube.com/embed/abc",
        ]
        for url in urls:
            assert adapter.can_handle(url) is True

    def test_tiktok_patterns(self):
        """Test TikTok URL patterns."""
        adapter = TikTokAdapter()
        urls = [
            "https://tiktok.com/@user/video/123",
            "https://www.tiktok.com/@user/video/123",
            "https://vm.tiktok.com/abc",
            "https://vt.tiktok.com/abc",
        ]
        for url in urls:
            assert adapter.can_handle(url) is True

    def test_instagram_patterns(self):
        """Test Instagram URL patterns."""
        adapter = InstagramAdapter()
        urls = [
            "https://instagram.com/p/abc",
            "https://www.instagram.com/reel/abc",
            "https://instagram.com/tv/abc",
            "https://instagram.com/stories/user/123",
        ]
        for url in urls:
            assert adapter.can_handle(url) is True

    def test_facebook_patterns(self):
        """Test Facebook URL patterns."""
        adapter = FacebookAdapter()
        urls = [
            "https://facebook.com/watch?v=123",
            "https://www.facebook.com/reel/123",
            "https://fb.watch/abc",
        ]
        for url in urls:
            assert adapter.can_handle(url) is True

    def test_pinterest_patterns(self):
        """Test Pinterest URL patterns."""
        adapter = PinterestAdapter()
        urls = [
            "https://pinterest.com/pin/123",
            "https://www.pinterest.com/pin/123",
            "https://pin.it/abc",
        ]
        for url in urls:
            assert adapter.can_handle(url) is True


class TestVideoIdExtraction:
    """Test video ID extraction."""

    def test_youtube_video_id(self):
        """Test YouTube video ID extraction."""
        adapter = YouTubeAdapter()
        assert adapter.extract_video_id("https://youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        assert adapter.extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        assert adapter.extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_tiktok_video_id(self):
        """Test TikTok video ID extraction."""
        adapter = TikTokAdapter()
        assert adapter.extract_video_id("https://tiktok.com/@user/video/7123456789012345678") == "7123456789012345678"
        assert adapter.extract_video_id("https://vm.tiktok.com/ZMMeX") == "ZMMeX"