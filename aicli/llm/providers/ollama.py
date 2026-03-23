"""Ollama local provider (internet-free)."""

from __future__ import annotations

import os

import ollama

from aicli.llm.providers.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    def __init__(self, model: str = "llama3.2", timeout: int = 60) -> None:
        self.model = model
        self.timeout = timeout
        self._base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    def complete(self, system: str, messages: list[dict]) -> str:
        all_messages = [{"role": "system", "content": system}] + messages
        response = ollama.chat(
            model=self.model,
            messages=all_messages,
            options={"num_predict": 512},
        )
        return response["message"]["content"]

    def validate_api_key(self) -> bool:
        try:
            ollama.list()
            return True
        except Exception:
            return False
