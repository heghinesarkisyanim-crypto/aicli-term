"""CLI entry point for aicli."""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console

from aicli import __version__
from aicli.automation.scaffolder import Scaffolder
from aicli.config import load_config
from aicli.core.executor import Executor
from aicli.core.pipeline import Pipeline
from aicli.core.session import SessionManager
from aicli.llm.engine import LLMEngine
from aicli.security.shield import SecurityShield
from aicli.ui import display
from aicli.ui.themes import get_theme

app = typer.Typer(
    name="aicli",
    help="Natural language to Linux commands powered by AI.",
    add_completion=False,
    no_args_is_help=True,
)

_console = Console()


def _build_provider(cfg: dict):
    """Instantiate the configured LLM provider."""
    llm_cfg = cfg["llm"]
    provider_name: str = llm_cfg["provider"]
    model: str = llm_cfg["model"]
    timeout: int = llm_cfg["timeout"]

    match provider_name:
        case "anthropic":
            from aicli.llm.providers.anthropic import AnthropicProvider
            return AnthropicProvider(model=model, timeout=timeout)
        case "openai":
            from aicli.llm.providers.openai import OpenAIProvider
            return OpenAIProvider(model=model, timeout=timeout)
        case "ollama":
            from aicli.llm.providers.ollama import OllamaProvider
            return OllamaProvider(model=model, timeout=timeout)
        case "groq":
            from aicli.llm.providers.groq import GroqProvider
            return GroqProvider(model=model, timeout=timeout)
        case "mock":
            from aicli.llm.providers.mock import MockProvider
            return MockProvider()
        case _:
            _console.print(f"[red]Unknown provider '{provider_name}'. Use: anthropic, openai, ollama, groq, mock[/red]")
            raise typer.Exit(1)


@app.command()
def run(
    command: str = typer.Argument(..., help="Natural language command (English or Armenian)"),
    config_file: Path | None = typer.Option(None, "--config", "-c", help="Path to settings.yaml"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview command without executing"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show raw LLM response"),
    no_color: bool = typer.Option(False, "--no-color", help="Disable colored output"),
    provider: str | None = typer.Option(None, "--provider", "-p", help="Override LLM provider"),
) -> None:
    """Translate a natural language request into a Linux command and execute it."""
    cfg = load_config(config_file)

    # Apply CLI overrides
    if provider:
        cfg["llm"]["provider"] = provider
    if no_color:
        cfg["ui"]["color_theme"] = "no-color"

    # Apply UI theme
    theme = get_theme(cfg["ui"]["color_theme"])
    display.set_theme(theme)

    # Build provider and validate key
    try:
        llm_provider = _build_provider(cfg)
    except typer.Exit:
        sys.exit(1)

    if not llm_provider.validate_api_key():
        _console.print(
            "[red]API key not found or invalid.[/red]\n"
            "Copy [bold].env.example[/bold] to [bold].env[/bold] and set your key."
        )
        raise typer.Exit(1)

    # Assemble components
    engine = LLMEngine(llm_provider, max_retries=cfg["llm"]["max_retries"])
    executor = Executor(timeout=30)
    scaffolder = Scaffolder()
    session = SessionManager(
        history_file=cfg["session"]["history_file"],
        history_size=cfg["session"]["history_size"],
        context_window=cfg["session"]["context_window"],
    )
    shield = SecurityShield(confirm_dangerous=cfg["security"]["confirm_dangerous"])

    effective_dry_run = dry_run or cfg["security"]["dry_run_default"]

    pipeline = Pipeline(
        engine=engine,
        executor=executor,
        scaffolder=scaffolder,
        session=session,
        shield=shield,
        dry_run=effective_dry_run,
        verbose=verbose,
    )

    pipeline.run(command)


@app.command()
def history() -> None:
    """Show recent command history."""
    cfg = load_config()
    session = SessionManager(
        history_file=cfg["session"]["history_file"],
        history_size=cfg["session"]["history_size"],
    )
    entries = session.get_history()
    if not entries:
        _console.print("[dim]No history yet.[/dim]")
        return

    for i, entry in enumerate(entries[-20:], 1):
        ts = entry.get("ts", "")[:19]
        user = entry.get("user", "")
        result = entry.get("result", "")
        _console.print(f"[dim]{i:3}. [{ts}][/dim] {user}  [dim]→ {result}[/dim]")


@app.command()
def clear_history() -> None:
    """Clear all command history."""
    cfg = load_config()
    session = SessionManager(history_file=cfg["session"]["history_file"])
    session.clear()
    _console.print("[green]History cleared.[/green]")


@app.command()
def templates() -> None:
    """List available scaffold templates."""
    from aicli.automation.registry import list_templates
    _console.print("[bold]Available templates:[/bold]")
    for name in list_templates():
        _console.print(f"  • {name}")


def _version_callback(value: bool) -> None:
    if value:
        _console.print(f"aicli {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", callback=_version_callback, is_eager=True, help="Show version and exit"
    ),
) -> None:
    pass
