"""Configuration loader — reads settings.yaml and .env."""

from __future__ import annotations

from pathlib import Path

import yaml
from dotenv import load_dotenv

_DEFAULT_CONFIG = Path(__file__).parent.parent / "config" / "settings.yaml"


def load_config(config_path: Path | None = None) -> dict:
    """Load YAML config and .env file. Returns config dict.

    Environment variables LLM_PROVIDER, LLM_MODEL override YAML values.
    """
    load_dotenv()  # loads .env from cwd or parent dirs

    path = config_path or _DEFAULT_CONFIG
    if not path.exists():
        data = _defaults()
    else:
        with open(path) as f:
            data = yaml.safe_load(f) or {}

        # Merge with defaults for any missing keys
        defaults = _defaults()
        for section, values in defaults.items():
            if section not in data:
                data[section] = values
            elif isinstance(values, dict):
                for k, v in values.items():
                    data[section].setdefault(k, v)

    # Environment variable overrides (LLM_PROVIDER, LLM_MODEL, LLM_API_KEY)
    import os
    if provider := os.environ.get("LLM_PROVIDER"):
        data["llm"]["provider"] = provider.lower()
    if model := os.environ.get("LLM_MODEL"):
        data["llm"]["model"] = model

    return data


def _defaults() -> dict:
    return {
        "llm": {
            "provider": "anthropic",
            "model": "claude-haiku-4-5-20251001",
            "timeout": 15,
            "max_retries": 3,
        },
        "security": {
            "confirm_dangerous": True,
            "dry_run_default": False,
            "blocked_paths": ["/etc", "/boot", "/sys", "/proc", "/dev"],
        },
        "session": {
            "history_size": 100,
            "context_window": 5,
            "history_file": "~/.aicli/history.json",
        },
        "ui": {
            "language": "en",
            "color_theme": "dark",
        },
    }
