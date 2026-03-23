"""Abstract base class for all LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """All providers must implement this interface."""

    @abstractmethod
    def complete(self, system: str, messages: list[dict]) -> str:
        """Send messages to the LLM and return the raw text response."""

    @abstractmethod
    def validate_api_key(self) -> bool:
        """Check that the API key / connection is valid. Returns True if ok."""
