import pytest

from core.security import (
    is_valid_url,
    extract_urls,
    resolve_hostname,
    is_private_ip,
    is_blocked_port,
    validate_url_security,
)


def test_extract_urls():
    """Test URL extraction from text."""
    text = "Check out https://youtube.com/watch?v=abc and https://tiktok.com/@user/video/123"
    urls = extract_urls(text)
    assert len(urls) == 2
    assert "https://youtube.com/watch?v=abc" in urls
    assert "https://tiktok.com/@user/video/123" in urls


def test_extract_urls_none():
    """Test URL extraction from text without URLs."""
    text = "Hello world, no links here!"
    urls = extract_urls(text)
    assert len(urls) == 0


def test_is_valid_url_valid():
    """Test valid URLs pass validation."""
    valid_urls = [
        "https://youtube.com/watch?v=abc",
        "https://www.tiktok.com/@user/video/123",
        "https://instagram.com/p/abc123",
        "https://facebook.com/watch?v=123",
        "https://pinterest.com/pin/123",
        "https://example.com/video.mp4",
        "http://example.com/image.jpg",
    ]
    for url in valid_urls:
        assert is_valid_url(url) is True


def test_is_valid_url_invalid_scheme():
    """Test URLs with invalid schemes are rejected."""
    invalid_urls = [
        "ftp://example.com/file",
        "file:///etc/passwd",
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
    ]
    for url in invalid_urls:
        assert is_valid_url(url) is False


def test_is_valid_url_localhost():
    """Test localhost URLs - format is valid but SSRF protection blocks them."""
    # These URLs are valid format but SSRF protection would block them
    localhost_urls = [
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://[::1]",
        "http://localhost",
    ]
    for url in localhost_urls:
        # The format is valid (http/https), SSRF protection catches these separately
        assert is_valid_url(url) is True


def test_is_valid_url_private_ips():
    """Test private IP URLs - format is valid but SSRF protection blocks them."""
    # These URLs are valid format but SSRF protection would block them
    private_urls = [
        "http://192.168.1.1",
        "http://10.0.0.1",
        "http://172.16.0.1",
        "http://172.31.255.255",
        "http://169.254.1.1",
    ]
    for url in private_urls:
        # The format is valid, SSRF protection catches these separately
        assert is_valid_url(url) is True


def test_is_valid_url_blocked_ports():
    """Test URLs with blocked ports - format is valid."""
    # URLs with blocked ports are valid format
    blocked_url_ports = [
        "http://example.com:22",
        "http://example.com:3306",
        "http://example.com:5432",
        "http://example.com:6379",
        "http://example.com:27017",
    ]
    for url in blocked_url_ports:
        assert is_valid_url(url) is True


def test_is_valid_url_allowed_ports():
    """Test URLs with allowed ports pass format validation."""
    valid_urls = [
        "http://example.com:80",
        "https://example.com:443",
        "http://example.com:8080",
        "https://example.com:8443",
    ]
    for url in valid_urls:
        assert is_valid_url(url) is True


def test_resolve_hostname():
    """Test hostname resolution function exists."""
    assert callable(resolve_hostname)


def test_is_private_ip():
    """Test private IP detection."""
    private_ips = [
        "192.168.1.1",
        "10.0.0.1",
        "172.16.0.1",
        "172.31.255.255",
        "127.0.0.1",
        "169.254.1.1",
        "::1",
        "fe80::1",
    ]
    for ip in private_ips:
        assert is_private_ip(ip) is True

    public_ips = [
        "8.8.8.8",
        "1.1.1.1",
        "203.0.113.1",
    ]
    for ip in public_ips:
        assert is_private_ip(ip) is False


def test_is_blocked_port():
    """Test blocked port detection."""
    blocked_ports = [22, 23, 25, 53, 110, 143, 993, 995, 3306, 5432, 6379, 27017]
    for port in blocked_ports:
        assert is_blocked_port(port) is True

    allowed_ports = [80, 443, 8080, 8443, 3000, 8000]
    for port in allowed_ports:
        assert is_blocked_port(port) is False