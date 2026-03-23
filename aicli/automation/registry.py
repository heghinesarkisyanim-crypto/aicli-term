"""Template registry — maps scaffold names to their template directories."""

from __future__ import annotations

from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"

REGISTRY: dict[str, Path] = {
    "flask-basic": TEMPLATES_DIR / "flask-basic",
    "flask-api": TEMPLATES_DIR / "flask-api",
    "python-script": TEMPLATES_DIR / "python-script",
    "venv-setup": TEMPLATES_DIR / "venv-setup",
}


def get_template_dir(name: str) -> Path:
    if name not in REGISTRY:
        available = ", ".join(REGISTRY.keys())
        raise ValueError(f"Unknown template '{name}'. Available: {available}")
    return REGISTRY[name]


def list_templates() -> list[str]:
    return list(REGISTRY.keys())
