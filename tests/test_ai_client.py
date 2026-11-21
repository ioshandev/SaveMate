import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from core.ai_client import AIClient, ChatMessage, UserContext


class TestChatMessage:
    """Test ChatMessage dataclass."""

    def test_creation(self):
        """Test creating a chat message."""
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.timestamp > 0


class TestUserContext:
    """Test UserContext dataclass."""

    def test_add_message(self):
        """Test adding messages to context."""
        ctx = UserContext()
        ctx.add_message("user", "Hello")
        ctx.add_message("assistant", "Hi there!")

        assert len(ctx.messages) == 2
        assert ctx.messages[0].role == "user"
        assert ctx.messages[1].role == "assistant"

    def test_get_messages(self):
        """Test getting messages with limit."""
        ctx = UserContext()
        for i in range(5):
            ctx.add_message("user", f"Message {i}")

        msgs = ctx.get_messages(limit=3)
        assert len(msgs) == 3
        assert msgs[0]["content"] == "Message 2"
        assert msgs[-1]["content"] == "Message 4"

    def test_clear(self):
        """Test clearing context."""
        ctx = UserContext()
        ctx.add_message("user", "Hello")
        ctx.clear()
        assert len(ctx.messages) == 0


class TestAIClient:
    """Test AIClient class."""

    @pytest.fixture
    def ai_client(self):
        """Create AI client with mock API key."""
        return AIClient(api_key="test_key", base_url="https://api.test.com/v1")

    def test_init(self, ai_client):
        """Test client initialization."""
        assert ai_client.api_key == "test_key"
        assert ai_client.base_url == "https://api.test.com/v1"
        assert ai_client.model == "gpt-4o-mini"

    def test_is_available(self, ai_client):
        """Test availability check."""
        assert ai_client.is_available() is True

        client_no_key = AIClient(api_key=None)
        assert client_no_key.is_available() is False

    def test_clear_context(self, ai_client):
        """Test clearing user context."""
        user_id = 12345
        ai_client._user_contexts[user_id] = UserContext()
        ai_client._user_contexts[user_id].add_message("user", "Hello")

        ai_client.clear_context(user_id)
        assert len(ai_client._user_contexts[user_id].messages) == 0

    @pytest.mark.asyncio
    async def test_chat_completion_no_key(self):
        """Test chat completion without API key."""
        client = AIClient(api_key=None)
        response = await client.chat_completion(12345, "Hello")
        assert response is None

    @pytest.mark.asyncio
    async def test_chat_completion_success(self, ai_client):
        """Test successful chat completion."""
        # Mock the session
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={
            "choices": [{"message": {"content": "Hello! How can I help?"}}]
        })
        mock_resp.text = AsyncMock(return_value="OK")

        # Create a proper async context manager mock for the response
        class MockPostContext:
            async def __aenter__(self):
                return mock_resp
            async def __aexit__(self, *args):
                return None

        mock_session = AsyncMock()
        mock_session.closed = False
        # In aiohttp, session.post() returns an async context manager directly
        # (internally it wraps a coroutine)
        mock_session.post = MagicMock(return_value=MockPostContext())

        ai_client._session = mock_session

        response = await ai_client.chat_completion(12345, "Hello")
        assert response == "Hello! How can I help?"
        assert len(ai_client._user_contexts[12345].messages) == 2  # user + assistant

    @pytest.mark.asyncio
    async def test_chat_completion_api_error(self, ai_client):
        """Test chat completion with API error."""
        mock_session = AsyncMock()
        mock_resp = AsyncMock()
        mock_resp.status = 500
        mock_resp.text = AsyncMock(return_value="Internal Server Error")
        mock_session.post.return_value.__aenter__.return_value = mock_resp

        ai_client._session = mock_session

        response = await ai_client.chat_completion(12345, "Hello")
        assert response is None

    @pytest.mark.asyncio
    async def test_chat_completion_timeout(self, ai_client):
        """Test chat completion timeout."""
        import asyncio
        mock_session = AsyncMock()
        mock_session.post.side_effect = asyncio.TimeoutError()
        ai_client._session = mock_session

        response = await ai_client.chat_completion(12345, "Hello")
        assert response is None

    @pytest.mark.asyncio
    async def test_chat_completion_stream(self, ai_client):
        """Test streaming chat completion."""
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.content = AsyncMock()

        async def async_iter(self):
            yield b'data: {"choices":[{"delta":{"content":"Hel"}}]}'
            yield b'data: {"choices":[{"delta":{"content":"lo"}}]}'
            yield b'data: [DONE]'

        mock_resp.content.__aiter__ = async_iter

        # Create a proper async context manager mock for the response
        class MockPostContext:
            async def __aenter__(self):
                return mock_resp
            async def __aexit__(self, *args):
                return None

        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.post = MagicMock(return_value=MockPostContext())

        ai_client._session = mock_session

        chunks = []
        async for chunk in ai_client.chat_completion_stream(12345, "Hello"):
            if chunk:
                chunks.append(chunk)

        assert chunks == ["Hel", "lo"]
        assert "".join(chunks) == "Hello"
        assert len(ai_client._user_contexts[12345].messages) == 2


class TestGlobalAIClient:
    """Test global AI client initialization."""

    def test_init_ai_client(self):
        """Test initializing global AI client."""
        import core.ai_client as ai_module
        ai_module.ai_client = None  # Reset global state
        from unittest.mock import patch

        mock_config = MagicMock()
        mock_config.ai_api_key = "test_global_key"
        mock_config.ai_base_url = "https://api.example.com/v1"
        mock_config.ai_model = "gpt-4o-mini"

        with patch('core.ai_client.config', mock_config):
            from core.ai_client import init_ai_client
            client = init_ai_client()
            assert client is not None
            assert client.api_key == "test_global_key"
            assert ai_module.ai_client is client