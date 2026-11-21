import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from core.security import (
    is_valid_url,
    URLValidationError,
    resolve_hostname,
    is_private_ip,
    is_blocked_port,
    SSRFProtection,
)


class TestSSRFProtection:
    """Test SSRF protection mechanisms."""

    @pytest.mark.asyncio
    async def test_block_localhost(self):
        """Test that localhost URLs are blocked."""
        with pytest.raises(URLValidationError, match="(?i)localhost|local|loopback"):
            await SSRFProtection.validate("http://localhost:8080")

        with pytest.raises(URLValidationError):
            await SSRFProtection.validate("http://127.0.0.1")

    @pytest.mark.asyncio
    async def test_block_private_ips(self):
        """Test that private IP URLs are blocked."""
        private_urls = [
            "http://192.168.1.1",
            "http://10.0.0.1",
            "http://172.16.0.1",
            "http://172.31.255.255",
            "http://169.254.1.1",
        ]
        for url in private_urls:
            with pytest.raises(URLValidationError):
                await SSRFProtection.validate(url)

    @pytest.mark.asyncio
    async def test_block_blocked_ports(self):
        """Test that URLs with blocked ports are blocked."""
        blocked_urls = [
            "http://example.com:22",    # SSH
            "http://example.com:3306",  # MySQL
            "http://example.com:5432",  # PostgreSQL
            "http://example.com:6379",  # Redis
            "http://example.com:27017", # MongoDB
        ]
        for url in blocked_urls:
            with pytest.raises(URLValidationError, match="port|blocked"):
                await SSRFProtection.validate(url)

    @pytest.mark.asyncio
    async def test_allow_public_urls(self):
        """Test that public URLs are allowed (with mocked DNS resolution)."""
        # Mock DNS resolution to return public IP for testing
        with patch('core._security_impl.resolve_host') as mock_resolve:
            mock_resolve.return_value = ["93.184.216.34"]  # Public IP

            public_urls = [
                "https://youtube.com/watch?v=abc",
                "https://example.com/video.mp4",
                "https://cdn.example.com/image.jpg",
            ]
            for url in public_urls:
                # Should not raise
                result = await SSRFProtection.validate(url)
                assert result is True

    @pytest.mark.asyncio
    async def test_dns_rebinding_protection(self):
        """Test DNS rebinding protection via IP resolution."""
        # Mock DNS resolution to return private IP
        with patch('core._security_impl.resolve_host') as mock_resolve:
            mock_resolve.return_value = ["192.168.1.100"]

            with pytest.raises(URLValidationError, match="private|resolved|internal"):
                await SSRFProtection.validate("http://evil.com")

    @pytest.mark.asyncio
    async def test_allowed_ports(self):
        """Test that standard web ports are allowed."""
        with patch('core._security_impl.resolve_host') as mock_resolve:
            mock_resolve.return_value = ["93.184.216.34"]  # Public IP

            allowed_urls = [
                "http://example.com:80",
                "https://example.com:443",
                "http://example.com:8080",
                "https://example.com:8443",
            ]
            for url in allowed_urls:
                result = await SSRFProtection.validate(url)
                assert result is True


class TestIPValidation:
    """Test IP address validation."""

    def test_ipv4_private_ranges(self):
        """Test IPv4 private range detection."""
        private = [
            "10.0.0.0",
            "10.255.255.255",
            "172.16.0.0",
            "172.31.255.255",
            "192.168.0.0",
            "192.168.255.255",
            "127.0.0.1",
            "169.254.0.0",
            "169.254.255.255",
            "0.0.0.0",
        ]
        for ip in private:
            assert is_private_ip(ip) is True, f"{ip} should be private"

    def test_ipv4_public_ranges(self):
        """Test IPv4 public range detection."""
        public = [
            "1.1.1.1",
            "8.8.8.8",
            "203.0.113.1",
            "198.51.100.1",
        ]
        for ip in public:
            assert is_private_ip(ip) is False, f"{ip} should be public"

    def test_ipv6_private_ranges(self):
        """Test IPv6 private range detection."""
        private = [
            "::1",
            "fe80::1",
            "fc00::1",
            "fd00::1",
        ]
        for ip in private:
            assert is_private_ip(ip) is True, f"{ip} should be private"

    def test_ipv6_public_ranges(self):
        """Test IPv6 public range detection."""
        public = [
            "2001:4860:4860::8888",
            "2606:4700:4700::1111",
        ]
        for ip in public:
            assert is_private_ip(ip) is False, f"{ip} should be public"


class TestPortValidation:
    """Test port validation."""

    def test_blocked_ports(self):
        """Test blocked port detection."""
        blocked = [22, 23, 25, 53, 110, 143, 465, 587, 993, 995, 3306, 5432, 6379, 27017]
        for port in blocked:
            assert is_blocked_port(port) is True, f"Port {port} should be blocked"

    def test_allowed_ports(self):
        """Test allowed port detection."""
        allowed = [80, 443, 8080, 8443, 3000, 8000, 8888, 9000]
        for port in allowed:
            assert is_blocked_port(port) is False, f"Port {port} should be allowed"