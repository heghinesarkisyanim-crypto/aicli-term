"""Rich-based terminal UI — all output goes through here."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

from aicli.interfaces import ExecutionResult, LLMResponse
from aicli.ui.themes import DARK_THEME

_console = Console(theme=DARK_THEME)


def set_theme(theme) -> None:
    global _console
    _console = Console(theme=theme)


def command_preview(response: LLMResponse) -> None:
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column(style="dim", width=14)
    table.add_column()

    if response.commands:
        if len(response.commands) == 1:
            table.add_row("Command:", f"[cmd]{response.commands[0]}[/cmd]")
        else:
            for i, cmd in enumerate(response.commands, 1):
                label = f"Step {i}:" if i > 1 else "Commands:"
                table.add_row(label, f"[cmd]{cmd}[/cmd]")

    table.add_row("Explanation:", f"[explain]{response.explanation}[/explain]")

    safe_label = "[success]Safe[/success]" if not response.is_dangerous else "[warning]Dangerous[/warning]"
    table.add_row("Safety:", safe_label)

    if response.requires_sudo:
        table.add_row("Note:", "[warning]Requires sudo[/warning]")

    _console.print(Panel(table, title="[bold]aicli[/bold]", border_style="blue"))


def execution_result(result: ExecutionResult, step: int | None = None) -> None:
    label = f"Step {step} " if step is not None else ""
    if result.success:
        _console.print(f"[success]{label}Done[/success] (exit 0)")
        if result.stdout.strip():
            _console.print(result.stdout.rstrip())
    else:
        _console.print(f"[error]{label}Failed[/error] (exit {result.exit_code})")
        if result.stderr.strip():
            _console.print(f"[error]{result.stderr.rstrip()}[/error]")
        if result.stdout.strip():
            _console.print(result.stdout.rstrip())


def step_header(n: int, total: int, command: str) -> None:
    if total > 1:
        _console.print(Rule(f"[dim]step {n}/{total}[/dim]  [cmd]{command}[/cmd]", style="dim blue"))


def scaffold_success(project_name: str, files: list[str]) -> None:
    _console.print(
        f"[success]Project '{project_name}' created[/success] ({len(files)} files)"
    )
    for f in files:
        _console.print(f"  [path]{f}[/path]")


def dangerous_warning(explanation: str) -> None:
    _console.print(
        Panel(
            f"[error]{explanation}[/error]",
            title="[error]BLOCKED — Dangerous Command[/error]",
            border_style="red",
        )
    )


def security_block(reason: str) -> None:
    _console.print(f"[error]Blocked:[/error] {reason}")


def dry_run(commands: list[str]) -> None:
    _console.print("[warning]Dry-run — would execute:[/warning]")
    for i, cmd in enumerate(commands, 1):
        prefix = f"  {i}." if len(commands) > 1 else "  "
        _console.print(f"{prefix} [cmd]{cmd}[/cmd]")


def info(text: str) -> None:
    _console.print(f"[info]{text}[/info]")


def error(text: str) -> None:
    _console.print(f"[error]Error:[/error] {text}")


def debug(obj: object) -> None:
    _console.print(f"[dim]DEBUG: {obj!r}[/dim]")


def confirm(message: str) -> bool:
    from aicli.ui.prompts import ask_confirm
    return ask_confirm(message)
