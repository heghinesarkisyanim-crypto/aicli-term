"""Anthropic Claude provider."""

from __future__ import annotations

import os

import anthropic

from aicli.llm.providers.base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, model: str, timeout: int = 15) -> None:
        self.model = model
        self.timeout = timeout
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self._client = anthropic.Anthropic(api_key=api_key)

    def complete(self, system: str, messages: list[dict]) -> str:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=512,
            system=system,
            messages=messages,
            timeout=self.timeout,
        )
        return response.content[0].text

    def validate_api_key(self) -> bool:
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        return bool(key and key != "your_anthropic_key_here")
