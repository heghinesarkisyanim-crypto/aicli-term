"""Session manager — persists command history and working directory."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path


class SessionManager:
    def __init__(
        self,
        history_file: str = "~/.aicli/history.json",
        history_size: int = 100,
        context_window: int = 5,
    ) -> None:
        self._history_file = Path(os.path.expanduser(history_file))
        self._history_size = history_size
        self._context_window = context_window
        self._history: list[dict] = []
        self.working_dir: str = os.getcwd()
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_entry(self, user: str, assistant_raw: str, result: str) -> None:
        entry = {
            "ts": datetime.now().isoformat(),
            "user": user,
            "assistant": assistant_raw,
            "result": result,
        }
        self._history.append(entry)
        if len(self._history) > self._history_size:
            self._history = self._history[-self._history_size :]
        self._save()

    def get_context(self) -> list[dict]:
        """Return the last N entries for LLM context."""
        return self._history[-self._context_window :]

    def get_history(self) -> list[dict]:
        return list(self._history)

    def clear(self) -> None:
        self._history = []
        self._save()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if self._history_file.exists():
            try:
                data = json.loads(self._history_file.read_text())
                self._history = data.get("history", [])
            except (json.JSONDecodeError, KeyError):
                self._history = []

    def _save(self) -> None:
        self._history_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "session_id": datetime.now().strftime("%Y-%m-%d"),
            "history": self._history,
            "working_dir": self.working_dir,
        }
        self._history_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
