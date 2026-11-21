import json
from dataclasses import dataclass
from typing import Optional, Any, List, Type, Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery
from aiogram import F as AiogramF
from aiogram.utils.magic_filter import MagicFilter

# Registry of all CallbackData subclasses for unpack_callback
_CALLBACK_REGISTRY: List[Type['CallbackData']] = []


def _register_callback(cls: Type['CallbackData']) -> Type['CallbackData']:
    """Decorator to register callback subclasses."""
    _CALLBACK_REGISTRY.append(cls)
    return cls


@dataclass
@_register_callback
class CallbackData:
    """Base class for callback data."""
    action: str

    def pack(self) -> str:
        """Serialize to JSON string."""
        data = {"a": self.action}
        # Add all non-None fields
        for key, value in self.__dict__.items():
            if key != "action" and value is not None:
                data[key] = value
        return json.dumps(data, separators=(",", ":"))

    @classmethod
    def unpack(cls, data: str) -> Optional["CallbackData"]:
        """Deserialize from JSON string."""
        try:
            parsed = json.loads(data)
            action = parsed.pop("a", None)
            if not action:
                return None
            return cls(action=action, **parsed)
        except (json.JSONDecodeError, TypeError):
            return None

    @classmethod
    def filter(
        cls,
        condition: Optional[MagicFilter] = None,
        **kwargs
    ) -> Union["CallbackDataFilter", MagicFilter]:
        """Create a filter for this callback data type.

        This supports two modes:
        1. Using MagicFilter directly: MyCallback.filter(F.field == value)
        2. Using keyword arguments: MyCallback.filter(field=value)

        Usage in aiogram 3.x router:
            @router.callback_query(MyCallback.filter(F.field == value))
            @router.callback_query(MyCallback.filter(field=value))
        """
        if condition is not None:
            # MagicFilter mode - wrap it
            return CallbackDataFilter(cls, magic_filter=condition)
        elif kwargs:
            # Keyword argument mode - convert to MagicFilter checks
            magic_filter = AiogramF
            for field, value in kwargs.items():
                magic_filter = magic_filter.__getattr__(field) == value
            return CallbackDataFilter(cls, magic_filter=magic_filter)
        else:
            # No conditions - accept any callback data of this type
            return CallbackDataFilter(cls)


# Main Menu Callbacks
@_register_callback
@dataclass
class MainMenuCallback(CallbackData):
    """Main menu navigation."""
    section: str  # media, image_tools, video_tools, ai, history, favorites, settings, help


@_register_callback
@dataclass
class BackCallback(CallbackData):
    """Go back to previous menu."""
    target: str = "main"  # main, media, image_tools, video_tools, ai, history, favorites, settings


# Media Assistant Callbacks
@_register_callback
@dataclass
class MediaActionCallback(CallbackData):
    """Media assistant actions."""
    platform: Optional[str] = None
    url: Optional[str] = None


# Image Tools Callbacks
@_register_callback
@dataclass
class ImageToolCallback(CallbackData):
    """Image tool selection."""
    tool: str  # convert, compress, info
    file_id: Optional[str] = None


@_register_callback
@dataclass
class ImageConvertCallback(CallbackData):
    """Image format conversion."""
    format: str  # JPEG, PNG, WEBP, etc.
    file_id: Optional[str] = None
    quality: int = 85


@_register_callback
@dataclass
class ImageCompressCallback(CallbackData):
    """Image compression."""
    preset: str  # high, medium, low, minimal
    file_id: Optional[str] = None


# Video Tools Callbacks
@_register_callback
@dataclass
class VideoToolCallback(CallbackData):
    """Video tool selection."""
    tool: str  # compress, convert, extract_audio, info
    file_id: Optional[str] = None


@_register_callback
@dataclass
class VideoCompressCallback(CallbackData):
    """Video compression."""
    preset: str  # high, medium, low, minimal
    file_id: Optional[str] = None


@_register_callback
@dataclass
class VideoConvertCallback(CallbackData):
    """Video format conversion."""
    format: str  # mp4, mov, mkv, webm, avi
    file_id: Optional[str] = None
    preset: str = "medium"


@_register_callback
@dataclass
class VideoExtractAudioCallback(CallbackData):
    """Audio extraction."""
    format: str  # mp3, aac, ogg, flac, wav, m4a, opus
    file_id: Optional[str] = None
    preset: str = "medium"


# AI Assistant Callbacks
@_register_callback
@dataclass
class AIChatCallback(CallbackData):
    """AI chat actions."""
    chat_action: str  # clear_context, cancel


# History Callbacks
@_register_callback
@dataclass
class HistoryCallback(CallbackData):
    """History navigation."""
    page: int = 0
    action: Optional[str] = None  # clear, view


# Favorites Callbacks
@_register_callback
@dataclass
class FavoritesCallback(CallbackData):
    """Favorites actions."""
    fav_action: str  # list, remove, view
    favorite_id: Optional[int] = None
    page: int = 0


# Settings Callbacks
@_register_callback
@dataclass
class SettingsCallback(CallbackData):
    """Settings actions."""
    setting: str  # language, notifications, delete_data
    value: Optional[str] = None


@_register_callback
@dataclass
class LanguageCallback(CallbackData):
    """Language selection."""
    lang: str  # en, si


@_register_callback
@dataclass
class NotificationsCallback(CallbackData):
    """Notifications toggle."""
    enabled: bool


@_register_callback
@dataclass
class DeleteDataCallback(CallbackData):
    """Delete data confirmation."""
    confirm: bool


# Admin Callbacks
@_register_callback
@dataclass
class AdminCallback(CallbackData):
    """Admin panel actions."""
    admin_action: str  # stats, users, broadcast, status
    user_id: Optional[int] = None
    page: int = 0


# Generic Pagination
@_register_callback
@dataclass
class PaginationCallback(CallbackData):
    """Generic pagination."""
    page: int
    context: str  # history, favorites, admin_users, etc.


class CallbackDataFilter(BaseFilter):
    """Filter for aiogram 3.x routers that matches callback data against a CallbackData subclass.

    Example usage:
        @router.callback_query(MyCallback.filter(F.field == value))
        async def handler(callback: CallbackQuery, ...):
            ...
    """

    def __init__(
        self,
        callback_class: Type[CallbackData],
        magic_filter: Optional[MagicFilter] = None
    ):
        self.callback_class = callback_class
        self.magic_filter = magic_filter

    async def __call__(self, callback: CallbackQuery) -> Union[bool, MagicFilter]:
        """Check if callback data matches the filter conditions."""
        parsed = unpack_callback(callback.data)
        if parsed is None:
            return False
        if not isinstance(parsed, self.callback_class):
            return False

        # If we have a magic filter, evaluate it on the parsed data
        if self.magic_filter is not None:
            # Create a mock object that has the parsed data as attributes
            class ParsedCallbackData:
                def __init__(self, data):
                    self.__dict__.update(data.__dict__)

            mock_data = ParsedCallbackData(parsed)
            # MagicFilter expects a TelegramObject, so we need to work with it
            result = await self.magic_filter(mock_data)
            return result

        return True


# Utility functions
def pack_callback(callback: CallbackData) -> str:
    """Pack callback data for use in inline keyboard."""
    return callback.pack()


def unpack_callback(data: str) -> Optional[CallbackData]:
    """Unpack callback data from inline keyboard.

    Tries each registered callback subclass to find a match.
    """
    try:
        parsed = json.loads(data)
        if "a" not in parsed:
            return None

        # Map "a" key to "action" parameter
        unpacked_data = {"action": parsed["a"]}

        # Copy remaining fields (they use different names than "a")
        for key, value in parsed.items():
            if key != "a":
                unpacked_data[key] = value

        # Try each registered subclass
        for cls in _CALLBACK_REGISTRY:
            try:
                instance = cls(**unpacked_data)
                return instance
            except (TypeError, ValueError):
                continue

        return None
    except (json.JSONDecodeError, TypeError):
        return None


def get_action_from_callback(data: str) -> Optional[str]:
    """Extract action from callback data without full parsing."""
    try:
        parsed = json.loads(data)
        return parsed.get("a")
    except (json.JSONDecodeError, TypeError):
        return None