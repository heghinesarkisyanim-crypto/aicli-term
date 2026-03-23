"""Confirmation and input prompts."""

from __future__ import annotations

from rich.console import Console
from rich.prompt import Confirm

_console = Console()


def ask_confirm(message: str) -> bool:
    """Prompt the user for yes/no. Default is NO (safe)."""
    _console.print()
    return Confirm.ask(f"[bold yellow]?[/bold yellow] {message}", default=False)
