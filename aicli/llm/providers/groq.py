"""Groq provider — fast inference via Groq Cloud."""

from __future__ import annotations

import os

import groq as groq_sdk

from aicli.llm.providers.base import BaseLLMProvider


class GroqProvider(BaseLLMProvider):
    def __init__(self, model: str = "llama-3.3-70b-versatile", timeout: int = 15) -> None:
        self.model = model
        self.timeout = timeout
        api_key = os.environ.get("LLM_API_KEY") or os.environ.get("GROQ_API_KEY", "")
        self._client = groq_sdk.Groq(api_key=api_key)

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
        key = os.environ.get("LLM_API_KEY") or os.environ.get("GROQ_API_KEY", "")
        return bool(key and not key.startswith("your_"))
