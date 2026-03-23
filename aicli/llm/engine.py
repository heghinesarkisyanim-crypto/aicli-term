"""LLM Engine — orchestrates API calls with retry logic and JSON validation."""

from __future__ import annotations

import json
import re
import time

from pydantic import ValidationError

from aicli.interfaces import LLMResponse
from aicli.llm.prompts import SYSTEM_PROMPT, build_user_message
from aicli.llm.providers.base import BaseLLMProvider
from aicli.llm.schema import LLMResponseSchema


class LLMEngine:
    def __init__(self, provider: BaseLLMProvider, max_retries: int = 3) -> None:
        self._provider = provider
        self._max_retries = max_retries

    def process(self, text: str, language: str, history: list[dict]) -> LLMResponse:
        """Translate natural language to a structured LLMResponse."""
        messages = build_user_message(text, language, history)

        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                raw = self._provider.complete(SYSTEM_PROMPT, messages)
                return self._parse(raw)
            except (ValueError, ValidationError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt < self._max_retries - 1:
                    time.sleep(2**attempt)
            except Exception as exc:
                last_error = exc
                if attempt < self._max_retries - 1:
                    time.sleep(2**attempt)

        raise RuntimeError(
            f"LLM failed after {self._max_retries} attempts: {last_error}"
        )

    def _parse(self, raw: str) -> LLMResponse:
        """Extract JSON from raw LLM output and validate with Pydantic."""
        text = raw.strip()

        # Strip markdown code fences
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
            text = text.strip()

        # Find the start of the first JSON object (handles leading prose)
        start = text.find("{")
        if start == -1:
            raise ValueError(f"No JSON object found in LLM response: {text[:200]}")

        # raw_decode stops after the first complete object — ignores trailing text
        data, _ = json.JSONDecoder().raw_decode(text, start)

        schema = LLMResponseSchema.model_validate(data)

        return LLMResponse(
            intent=schema.intent,
            commands=schema.commands,
            explanation=schema.explanation,
            is_dangerous=schema.is_dangerous,
            requires_sudo=schema.requires_sudo,
            affects_paths=schema.affects_paths,
        )
