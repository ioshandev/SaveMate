import json
from dataclasses import dataclass
from typing import Optional, Any, List, Type


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