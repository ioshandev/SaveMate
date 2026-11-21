import ipaddress
import logging
import re
import socket
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

PRIVATE_IP_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("0.0.0.0/8"),  # "0.0.0.0" is a special address, treat as private
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

BLOCKED_PORTS = {
    22, 23, 25, 53, 110, 135, 139, 143, 445, 993, 995, 1723, 3306, 3389,
    5432, 5900, 6379, 27017, 465, 587  # Added 465 (IMAPS) and 587 (SMTPS)
}

URL_REGEX = re.compile(
    r"^(?:http|https)://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
    r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


class URLValidationError(Exception):
    """Raised when URL validation fails due to SSRF protection."""
    pass


def is_valid_url(url: str) -> bool:
    """Check if URL is valid format (http/https only)."""
    if not url or not isinstance(url, str):
        return False
    if len(url) > 2048:
        return False
    return bool(URL_REGEX.match(url.strip()))


def parse_url(url: str) -> tuple[str, int] | None:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return None
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        return host, port
    except Exception:
        return None


async def resolve_host(host: str) -> list[str]:
    """Resolve hostname to list of IP addresses."""
    try:
        loop = __import__("asyncio").get_event_loop()
        infos = await loop.getaddrinfo(host, None, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM)
        return [info[4][0] for info in infos]
    except Exception as e:
        logger.warning("DNS resolution failed for %s: %s", host, e)
        return []


# Alias for backwards compatibility
resolve_hostname = resolve_host


def is_private_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
        return any(ip in network for network in PRIVATE_IP_RANGES)
    except ValueError:
        return True


def is_blocked_port(port: int) -> bool:
    return port in BLOCKED_PORTS


class SSRFProtection:
    """SSRF protection class for URL validation."""

    @classmethod
    async def validate(cls, url: str) -> bool:
        """
        Validate URL for SSRF protection.
        Raises URLValidationError if validation fails.
        Returns True if URL is safe.
        """
        if not url or not isinstance(url, str):
            raise URLValidationError("Invalid URL: empty or not a string")

        if len(url) > 2048:
            raise URLValidationError("Invalid URL: too long")

        # Check URL scheme
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                raise URLValidationError("Invalid URL scheme (only http/https allowed)")
        except Exception as e:
            raise URLValidationError(f"Invalid URL: {e}")

        # Check for localhost/private hostnames
        host = parsed.hostname or ""
        if host.lower() == "localhost" or host.lower().startswith("local"):
            raise URLValidationError("Localhost URLs are not allowed")

        # Parse host and port
        result = parse_url(url)
        if not result:
            raise URLValidationError("Could not parse URL")
        host, port = result

        # Check for localhost in host
        if host.lower() == "localhost" or host.startswith("127.") or host.startswith("10.") or host.startswith("192.168.") or host.startswith("172.") or host.startswith("169.254."):
            raise URLValidationError(f"Access to private/internal addresses is not allowed")

        # Check blocked ports
        if is_blocked_port(port):
            raise URLValidationError(f"Port {port} is blocked for security reasons")

        # Resolve DNS and check for private IPs
        ips = await resolve_host(host)
        if not ips:
            raise URLValidationError("Could not resolve host")

        for ip in ips:
            if is_private_ip(ip):
                logger.warning("SSRF attempt blocked: %s resolves to private IP %s", host, ip)
                raise URLValidationError("Resolved to private or internal IP address")

        return True

    @classmethod
    async def validate_url_security(url: str) -> tuple[bool, str | None]:
        """
        Validate URL for SSRF protection.
        Returns (is_safe, error_message).
        """
        try:
            await cls.validate(url)
            return True, None
        except URLValidationError as e:
            return False, str(e)


async def validate_url_security(url: str) -> tuple[bool, str | None]:
    """
    Validate URL for SSRF protection.
    Returns (is_safe, error_message).
    """
    return await SSRFProtection.validate_url_security(url)


def extract_urls(text: str) -> list[str]:
    url_pattern = re.compile(
        r"(https?://[^\s<>{}|\\^`\[\]]+)",
        re.IGNORECASE,
    )
    return url_pattern.findall(text)