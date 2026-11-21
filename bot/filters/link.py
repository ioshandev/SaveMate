import logging
import re
from typing import Any, Dict, List, Optional, Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from core.security import extract_urls, is_valid_url, URLValidationError

logger = logging.getLogger(__name__)


class LinkFilter(BaseFilter):
    """
    Filter to detect and validate URLs in messages.
    Extracts URLs and validates them against SSRF protection.
    """

    # URL pattern for extraction (comprehensive)
    URL_PATTERN = re.compile(
        r'(https?://[^\s<>"\'\)\]\}]+)',
        re.IGNORECASE
    )

    def __init__(self, validate: bool = True) -> None:
        self.validate = validate

    async def __call__(
        self,
        event: Union[Message, CallbackQuery],
        **kwargs: Any
    ) -> Union[bool, Dict[str, Any]]:
        # Extract text from message
        text = None
        if isinstance(event, Message):
            text = event.text or event.caption
        elif isinstance(event, CallbackQuery):
            # For callbacks, we might want to check the message text
            if event.message and isinstance(event.message, Message):
                text = event.message.text or event.message.caption

        if not text:
            return False

        # Extract URLs
        urls = extract_urls(text)

        if not urls:
            return False

        # Validate URLs if requested
        valid_urls = []
        for url in urls:
            try:
                if self.validate:
                    is_valid_url(url)
                valid_urls.append(url)
            except URLValidationError as e:
                logger.warning("Invalid URL filtered out: %s - %s", url, e)
                continue

        if not valid_urls:
            return False

        # Return dict with extracted URLs for handler use
        return {"urls": valid_urls}


# Helper function to extract URLs from text
def get_urls_from_text(text: str, validate: bool = True) -> List[str]:
    """Extract and optionally validate URLs from text."""
    urls = extract_urls(text)
    if not validate:
        return urls

    valid = []
    for url in urls:
        try:
            is_valid_url(url)
            valid.append(url)
        except URLValidationError:
            continue
    return valid