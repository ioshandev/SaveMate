import pytest
import json

from bot.keyboards.callbacks import (
    CallbackData,
    MainMenuCallback,
    BackCallback,
    MediaActionCallback,
    ImageToolCallback,
    ImageConvertCallback,
    ImageCompressCallback,
    VideoToolCallback,
    VideoCompressCallback,
    VideoConvertCallback,
    VideoExtractAudioCallback,
    AIChatCallback,
    HistoryCallback,
    FavoritesCallback,
    SettingsCallback,
    LanguageCallback,
    NotificationsCallback,
    DeleteDataCallback,
    AdminCallback,
    PaginationCallback,
    pack_callback,
    unpack_callback,
    get_action_from_callback,
)


class TestCallbackDataBase:
    """Test base CallbackData class."""

    def test_pack_unpack_simple(self):
        """Test packing and unpacking simple callback."""
        callback = CallbackData(action="test")
        packed = callback.pack()
        assert packed == '{"a":"test"}'

        unpacked = CallbackData.unpack(packed)
        assert unpacked is not None
        assert unpacked.action == "test"

    def test_pack_unpack_with_fields(self):
        """Test packing and unpacking with additional fields."""
        callback = MainMenuCallback(action="navigate", section="media")
        packed = callback.pack()
        assert '{"a":"navigate","section":"media"}' == packed

        unpacked = MainMenuCallback.unpack(packed)
        assert unpacked is not None
        assert unpacked.action == "navigate"
        assert unpacked.section == "media"

    def test_unpack_invalid_json(self):
        """Test unpacking invalid JSON returns None."""
        result = CallbackData.unpack("not valid json")
        assert result is None

    def test_unpack_missing_action(self):
        """Test unpacking JSON without action returns None."""
        result = CallbackData.unpack('{"section":"media"}')
        assert result is None

    def test_pack_excludes_none_values(self):
        """Test that None values are excluded from packed data."""
        callback = MediaActionCallback(action="download", platform="youtube", url=None)
        packed = callback.pack()
        data = json.loads(packed)
        assert "url" not in data
        assert data["platform"] == "youtube"


class TestMainMenuCallback:
    """Test MainMenuCallback."""

    def test_navigation(self):
        """Test main menu navigation callbacks."""
        sections = ["media", "image_tools", "video_tools", "ai", "history", "favorites", "settings", "help"]
        for section in sections:
            callback = MainMenuCallback(action="navigate", section=section)
            packed = callback.pack()
            unpacked = MainMenuCallback.unpack(packed)
            assert unpacked.section == section


class TestBackCallback:
    """Test BackCallback."""

    def test_back_targets(self):
        """Test back button targets."""
        targets = ["main", "media", "image_tools", "video_tools", "ai", "history", "favorites", "settings"]
        for target in targets:
            callback = BackCallback(action="back", target=target)
            packed = callback.pack()
            unpacked = BackCallback.unpack(packed)
            assert unpacked.target == target

    def test_default_target(self):
        """Test default target is main."""
        callback = BackCallback(action="back")
        assert callback.target == "main"


class TestMediaActionCallback:
    """Test MediaActionCallback."""

    def test_download(self):
        """Test media download callback."""
        callback = MediaActionCallback(action="download", platform="youtube", url="https://youtube.com/watch?v=abc")
        packed = callback.pack()
        unpacked = MediaActionCallback.unpack(packed)
        assert unpacked.action == "download"
        assert unpacked.platform == "youtube"
        assert unpacked.url == "https://youtube.com/watch?v=abc"


class TestImageCallbacks:
    """Test image-related callbacks."""

    def test_image_tool_callback(self):
        """Test ImageToolCallback."""
        callback = ImageToolCallback(action="select_tool", tool="convert", file_id="file_123")
        packed = callback.pack()
        unpacked = ImageToolCallback.unpack(packed)
        assert unpacked.tool == "convert"
        assert unpacked.file_id == "file_123"

    def test_image_convert_callback(self):
        """Test ImageConvertCallback."""
        callback = ImageConvertCallback(action="convert", format="PNG", file_id="file_123", quality=90)
        packed = callback.pack()
        unpacked = ImageConvertCallback.unpack(packed)
        assert unpacked.format == "PNG"
        assert unpacked.file_id == "file_123"
        assert unpacked.quality == 90

    def test_image_compress_callback(self):
        """Test ImageCompressCallback."""
        callback = ImageCompressCallback(action="compress", preset="high", file_id="file_123")
        packed = callback.pack()
        unpacked = ImageCompressCallback.unpack(packed)
        assert unpacked.preset == "high"
        assert unpacked.file_id == "file_123"


class TestVideoCallbacks:
    """Test video-related callbacks."""

    def test_video_tool_callback(self):
        """Test VideoToolCallback."""
        callback = VideoToolCallback(action="select_tool", tool="compress", file_id="file_123")
        packed = callback.pack()
        unpacked = VideoToolCallback.unpack(packed)
        assert unpacked.tool == "compress"
        assert unpacked.file_id == "file_123"

    def test_video_compress_callback(self):
        """Test VideoCompressCallback."""
        callback = VideoCompressCallback(action="compress", preset="medium", file_id="file_123")
        packed = callback.pack()
        unpacked = VideoCompressCallback.unpack(packed)
        assert unpacked.preset == "medium"
        assert unpacked.file_id == "file_123"

    def test_video_convert_callback(self):
        """Test VideoConvertCallback."""
        callback = VideoConvertCallback(action="convert", format="webm", file_id="file_123", preset="high")
        packed = callback.pack()
        unpacked = VideoConvertCallback.unpack(packed)
        assert unpacked.format == "webm"
        assert unpacked.file_id == "file_123"
        assert unpacked.preset == "high"

    def test_video_extract_audio_callback(self):
        """Test VideoExtractAudioCallback."""
        callback = VideoExtractAudioCallback(action="extract", format="mp3", file_id="file_123", preset="medium")
        packed = callback.pack()
        unpacked = VideoExtractAudioCallback.unpack(packed)
        assert unpacked.format == "mp3"
        assert unpacked.file_id == "file_123"
        assert unpacked.preset == "medium"


class TestAIChatCallback:
    """Test AIChatCallback."""

    def test_clear_context(self):
        """Test clear context action."""
        callback = AIChatCallback(action="clear_context", chat_action="clear_context")
        packed = callback.pack()
        unpacked = AIChatCallback.unpack(packed)
        assert unpacked.chat_action == "clear_context"

    def test_cancel(self):
        """Test cancel action."""
        callback = AIChatCallback(action="cancel", chat_action="cancel")
        packed = callback.pack()
        unpacked = AIChatCallback.unpack(packed)
        assert unpacked.chat_action == "cancel"


class TestHistoryCallback:
    """Test HistoryCallback."""

    def test_pagination(self):
        """Test history pagination."""
        callback = HistoryCallback(action="view", page=2)
        packed = callback.pack()
        unpacked = HistoryCallback.unpack(packed)
        assert unpacked.page == 2
        assert unpacked.action == "view"

    def test_clear(self):
        """Test clear history."""
        callback = HistoryCallback(action="clear", page=0)
        packed = callback.pack()
        unpacked = HistoryCallback.unpack(packed)
        assert unpacked.action == "clear"


class TestFavoritesCallback:
    """Test FavoritesCallback."""

    def test_remove(self):
        """Test remove favorite."""
        callback = FavoritesCallback(action="remove", fav_action="remove", favorite_id=42, page=0)
        packed = callback.pack()
        unpacked = FavoritesCallback.unpack(packed)
        assert unpacked.fav_action == "remove"
        assert unpacked.favorite_id == 42
        assert unpacked.page == 0


class TestSettingsCallbacks:
    """Test settings-related callbacks."""

    def test_settings_callback(self):
        """Test SettingsCallback."""
        callback = SettingsCallback(action="setting", setting="language", value="en")
        packed = callback.pack()
        unpacked = SettingsCallback.unpack(packed)
        assert unpacked.setting == "language"
        assert unpacked.value == "en"

    def test_language_callback(self):
        """Test LanguageCallback."""
        callback = LanguageCallback(action="language", lang="si")
        packed = callback.pack()
        unpacked = LanguageCallback.unpack(packed)
        assert unpacked.lang == "si"

    def test_notifications_callback(self):
        """Test NotificationsCallback."""
        callback = NotificationsCallback(action="notifications", enabled=False)
        packed = callback.pack()
        unpacked = NotificationsCallback.unpack(packed)
        assert unpacked.enabled is False

    def test_delete_data_callback(self):
        """Test DeleteDataCallback."""
        callback = DeleteDataCallback(action="delete_data", confirm=True)
        packed = callback.pack()
        unpacked = DeleteDataCallback.unpack(packed)
        assert unpacked.confirm is True


class TestAdminCallback:
    """Test AdminCallback."""

    def test_admin_actions(self):
        """Test various admin actions."""
        actions = ["stats", "users", "broadcast", "status"]
        for action in actions:
            callback = AdminCallback(action="admin", admin_action=action, page=0)
            packed = callback.pack()
            unpacked = AdminCallback.unpack(packed)
            assert unpacked.admin_action == action

    def test_admin_user_info(self):
        """Test admin user info callback."""
        callback = AdminCallback(action="admin", admin_action="user_info", user_id=12345, page=0)
        packed = callback.pack()
        unpacked = AdminCallback.unpack(packed)
        assert unpacked.admin_action == "user_info"
        assert unpacked.user_id == 12345


class TestPaginationCallback:
    """Test PaginationCallback."""

    def test_pagination_contexts(self):
        """Test pagination for different contexts."""
        contexts = ["history", "favorites", "admin_users"]
        for context in contexts:
            callback = PaginationCallback(action="page", page=3, context=context)
            packed = callback.pack()
            unpacked = PaginationCallback.unpack(packed)
            assert unpacked.page == 3
            assert unpacked.context == context


class TestUtilityFunctions:
    """Test utility functions."""

    def test_pack_callback(self):
        """Test pack_callback function."""
        callback = MainMenuCallback(action="navigate", section="media")
        packed = pack_callback(callback)
        assert '{"a":"navigate","section":"media"}' == packed

    def test_unpack_callback(self):
        """Test unpack_callback function."""
        packed = '{"a":"navigate","section":"media"}'
        callback = unpack_callback(packed)
        assert callback is not None
        assert callback.action == "navigate"

    def test_get_action_from_callback(self):
        """Test extracting action without full parsing."""
        packed = '{"a":"navigate","section":"media"}'
        action = get_action_from_callback(packed)
        assert action == "navigate"

        action = get_action_from_callback("invalid json")
        assert action is None

        action = get_action_from_callback('{"section":"media"}')
        assert action is None