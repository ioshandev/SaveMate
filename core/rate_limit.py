import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, Optional

from config import config

logger = logging.getLogger(__name__)


@dataclass
class RateLimitBucket:
    """Sliding window rate limit bucket."""
    requests: deque = field(default_factory=deque)
    limit: int = 30
    window: int = 60  # seconds

    def add_request(self) -> None:
        now = time.time()
        self.requests.append(now)
        self._cleanup(now)

    def _cleanup(self, now: float) -> None:
        """Remove requests older than the window."""
        cutoff = now - self.window
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()

    def get_count(self) -> int:
        now = time.time()
        self._cleanup(now)
        return len(self.requests)

    def is_limited(self) -> bool:
        return self.get_count() >= self.limit

    def time_until_reset(self) -> float:
        """Seconds until the oldest request expires."""
        if not self.requests:
            return 0
        return max(0, self.requests[0] + self.window - time.time())


class RateLimiter:
    """
    In-memory sliding window rate limiter.
    Supports per-user, per-action limits.
    """

    def __init__(
        self,
        default_limit: int = 30,
        default_window: int = 60,
    ):
        self.default_limit = default_limit
        self.default_window = default_window
        self._buckets: Dict[str, RateLimitBucket] = {}
        self._lock = asyncio.Lock()

    def _get_key(self, user_id: int, action: str = "default") -> str:
        return f"{user_id}:{action}"

    def _get_bucket(self, key: str) -> RateLimitBucket:
        if key not in self._buckets:
            self._buckets[key] = RateLimitBucket(
                limit=self.default_limit,
                window=self.default_window,
            )
        return self._buckets[key]

    async def check_rate_limit(
        self,
        user_id: int,
        action: str = "default",
        limit: Optional[int] = None,
        window: Optional[int] = None,
    ) -> tuple[bool, float]:
        """
        Check if user is rate limited for an action.

        Returns:
            (allowed, retry_after_seconds)
        """
        key = self._get_key(user_id, action)
        async with self._lock:
            bucket = self._buckets.get(key)
            if not bucket:
                bucket = RateLimitBucket(
                    limit=limit or self.default_limit,
                    window=window or self.default_window,
                )
                self._buckets[key] = bucket
            elif limit is not None or window is not None:
                # Update limits if provided
                if limit is not None:
                    bucket.limit = limit
                if window is not None:
                    bucket.window = window

            if bucket.is_limited():
                retry_after = bucket.time_until_reset()
                return False, retry_after

            bucket.add_request()
            return True, 0

    async def get_remaining(self, user_id: int, action: str = "default") -> int:
        """Get remaining requests in current window."""
        key = self._get_key(user_id, action)
        async with self._lock:
            bucket = self._buckets.get(key)
            if not bucket:
                return self.default_limit
            return max(0, bucket.limit - bucket.get_count())

    async def reset(self, user_id: int, action: Optional[str] = None) -> None:
        """Reset rate limit for user (and optionally specific action)."""
        async with self._lock:
            if action:
                key = self._get_key(user_id, action)
                self._buckets.pop(key, None)
            else:
                # Reset all actions for user
                keys_to_remove = [k for k in self._buckets if k.startswith(f"{user_id}:")]
                for key in keys_to_remove:
                    self._buckets.pop(key, None)

    async def cleanup_expired(self) -> int:
        """Remove buckets with no recent requests. Returns count removed."""
        now = time.time()
        async with self._lock:
            keys_to_remove = []
            for key, bucket in self._buckets.items():
                bucket._cleanup(now)
                if not bucket.requests:
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                self._buckets.pop(key, None)
            return len(keys_to_remove)


# Global rate limiter instance
rate_limiter = RateLimiter(
    default_limit=config.rate_limit_messages,
    default_window=config.rate_limit_window,
)


async def rate_limit_middleware(
    user_id: int,
    action: str = "default",
    limit: Optional[int] = None,
    window: Optional[int] = None,
) -> tuple[bool, float]:
    """
    Convenience function for middleware use.
    """
    return await rate_limiter.check_rate_limit(user_id, action, limit, window)