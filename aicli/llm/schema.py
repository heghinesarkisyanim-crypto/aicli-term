"""Pydantic models for LLM response validation."""

from __future__ import annotations

from pydantic import BaseModel, field_validator, model_validator

from aicli.interfaces import Intent


class LLMResponseSchema(BaseModel):
    intent: Intent
    commands: list[str] = []
    explanation: str
    is_dangerous: bool
    requires_sudo: bool = False
    affects_paths: list[str] = []

    @field_validator("intent", mode="before")
    @classmethod
    def normalise_intent(cls, v: str) -> str:
        return v.lower().strip()

    @field_validator("commands", mode="before")
    @classmethod
    def normalise_commands(cls, v) -> list[str]:
        # Accept a plain string for backwards compat
        if isinstance(v, str):
            return [v.strip()] if v.strip() else []
        return [c.strip() for c in v if isinstance(c, str) and c.strip()]

    @model_validator(mode="before")
    @classmethod
    def migrate_command_field(cls, data: dict) -> dict:
        """Accept old single-string 'command' field and promote it to 'commands'."""
        if isinstance(data, dict) and "command" in data and "commands" not in data:
            cmd = data.pop("command", "")
            data["commands"] = [cmd] if cmd else []
        return data
