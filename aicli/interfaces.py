"""Shared data structures used across all modules."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Intent(str, Enum):
    OS_COMMAND = "os_command"
    SCAFFOLD = "scaffold"
    INFO = "info"
    DANGEROUS = "dangerous"


class Language(str, Enum):
    EN = "en"
    HY = "hy"


@dataclass
class ParsedInput:
    text: str
    language: Language


@dataclass
class LLMResponse:
    intent: Intent
    commands: list[str]          # one or more shell commands to run in sequence
    explanation: str
    is_dangerous: bool
    requires_sudo: bool = False
    affects_paths: list[str] = field(default_factory=list)

    @property
    def command(self) -> str:
        """First command — convenience accessor used by scaffold routing."""
        return self.commands[0] if self.commands else ""


@dataclass
class CommandRequest:
    commands: list[str]          # all commands to execute in order
    explanation: str
    is_dangerous: bool
    requires_sudo: bool
    affects_paths: list[str]
    dry_run: bool = False


@dataclass
class ScaffoldRequest:
    template: str
    project_name: str
    target_dir: str
    extra_params: dict = field(default_factory=dict)


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    command: str = ""

    @property
    def success(self) -> bool:
        return self.exit_code == 0
