import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

import aiohttp
from config import config

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class UserContext:
    messages: deque = field(default_factory=lambda: deque(maxlen=20))
    last_activity: float = field(default_factory=time.time)

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(ChatMessage(role=role, content=content))
        self.last_activity = time.time()

    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        msgs = list(self.messages)
        if limit:
            msgs = msgs[-limit:]
        return [{"role": m.role, "content": m.content} for m in msgs]

    def clear(self) -> None:
        self.messages.clear()


class AIClient:
    """
    OpenAI-compatible chat completions client with per-user context management.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
        timeout: int = 30,
        max_context_turns: int = 10,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_context_turns = max_context_turns
        self._session: Optional[aiohttp.ClientSession] = None
        self._user_contexts: Dict[int, UserContext] = {}

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._session = aiohttp.ClientSession(timeout=self.timeout, headers=headers)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    def _get_context(self, user_id: int) -> UserContext:
        if user_id not in self._user_contexts:
            self._user_contexts[user_id] = UserContext()
        return self._user_contexts[user_id]

    def clear_context(self, user_id: int) -> None:
        if user_id in self._user_contexts:
            self._user_contexts[user_id].clear()

    def is_available(self) -> bool:
        return self.api_key is not None

    async def chat_completion(
        self,
        user_id: int,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Optional[str]:
        """
        Send a chat completion request with user context.

        Args:
            user_id: Telegram user ID
            message: User's message
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Max tokens in response

        Returns:
            Assistant's response or None if error/unavailable
        """
        if not self.is_available():
            logger.warning("AI client not configured (no API key)")
            return None

        context = self._get_context(user_id)
        context.add_message("user", message)

        # Build messages array
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add context messages (excluding the one we just added)
        context_messages = context.get_messages(limit=self.max_context_turns * 2)
        # Don't duplicate the last user message
        if context_messages and context_messages[-1]["role"] == "user":
            context_messages = context_messages[:-1]
        messages.extend(context_messages)
        messages.append({"role": "user", "content": message})

        try:
            session = await self._get_session()
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens

            async with session.post(f"{self.base_url}/chat/completions", json=payload) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error("AI API error %s: %s", resp.status, error_text)
                    return None

                data = await resp.json()
                choices = data.get("choices", [])
                if not choices:
                    logger.error("AI API returned no choices")
                    return None

                response = choices[0].get("message", {}).get("content", "")
                if response:
                    context.add_message("assistant", response)
                return response

        except asyncio.TimeoutError:
            logger.error("AI API request timed out")
            return None
        except aiohttp.ClientError as e:
            logger.error("AI API client error: %s", e)
            return None
        except Exception as e:
            logger.error("AI API unexpected error: %s", e)
            return None

    async def chat_completion_stream(
        self,
        user_id: int,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ):
        """
        Streaming chat completion (async generator).

        Yields chunks of the response as they arrive.
        """
        if not self.is_available():
            yield None
            return

        context = self._get_context(user_id)
        context.add_message("user", message)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        context_messages = context.get_messages(limit=self.max_context_turns * 2)
        if context_messages and context_messages[-1]["role"] == "user":
            context_messages = context_messages[:-1]
        messages.extend(context_messages)
        messages.append({"role": "user", "content": message})

        try:
            session = await self._get_session()
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": True,
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens

            async with session.post(f"{self.base_url}/chat/completions", json=payload) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error("AI API streaming error %s: %s", resp.status, error_text)
                    yield None
                    return

                full_response = ""
                async for line in resp.content:
                    line = line.decode("utf-8").strip()
                    if not line or line == "data: [DONE]":
                        continue
                    if line.startswith("data: "):
                        import json
                        try:
                            data = json.loads(line[6:])
                            choices = data.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    full_response += content
                                    yield content
                        except json.JSONDecodeError:
                            continue

                if full_response:
                    context.add_message("assistant", full_response)

        except asyncio.TimeoutError:
            logger.error("AI API streaming request timed out")
            yield None
        except aiohttp.ClientError as e:
            logger.error("AI API streaming client error: %s", e)
            yield None
        except Exception as e:
            logger.error("AI API streaming unexpected error: %s", e)
            yield None


# Global AI client instance (initialized in main.py with config)
ai_client: Optional[AIClient] = None


def init_ai_client() -> AIClient:
    """Initialize global AI client from config."""
    global ai_client
    ai_client = AIClient(
        api_key=config.ai_api_key,
        base_url=config.ai_base_url,
        model=config.ai_model,
    )
    return ai_client