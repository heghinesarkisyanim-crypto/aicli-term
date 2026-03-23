"""OpenAI provider."""

from __future__ import annotations

import os

from openai import OpenAI

from aicli.llm.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model: str = "gpt-4o", timeout: int = 15) -> None:
        self.model = model
        self.timeout = timeout
        api_key = os.environ.get("OPENAI_API_KEY", "")
        self._client = OpenAI(api_key=api_key)

    def complete(self, system: str, messages: list[dict]) -> str:
        all_messages = [{"role": "system", "content": system}] + messages
        response = self._client.chat.completions.create(
            model=self.model,
            messages=all_messages,
            max_tokens=512,
            timeout=self.timeout,
        )
        return response.choices[0].message.content or ""

    def validate_api_key(self) -> bool:
        key = os.environ.get("OPENAI_API_KEY", "")
        return bool(key and key != "your_openai_key_here")
