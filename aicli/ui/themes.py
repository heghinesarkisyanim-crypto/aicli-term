"""Color themes for the terminal UI."""

from __future__ import annotations

from rich.theme import Theme

DARK_THEME = Theme(
    {
        "cmd": "bold cyan",
        "explain": "dim white",
        "success": "bold green",
        "error": "bold red",
        "warning": "bold yellow",
        "info": "blue",
        "prompt": "bold magenta",
        "path": "underline cyan",
    }
)

LIGHT_THEME = Theme(
    {
        "cmd": "bold blue",
        "explain": "dim black",
        "success": "bold dark_green",
        "error": "bold dark_red",
        "warning": "bold dark_orange3",
        "info": "navy_blue",
        "prompt": "bold purple",
        "path": "underline blue",
    }
)

NO_COLOR_THEME = Theme({})


def get_theme(name: str) -> Theme:
    match name:
        case "light":
            return LIGHT_THEME
        case "no-color":
            return NO_COLOR_THEME
        case _:
            return DARK_THEME
