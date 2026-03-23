"""Mock provider for demos and integration testing — no API key needed."""

from __future__ import annotations

import json
import re

from aicli.llm.providers.base import BaseLLMProvider

_RULES: list[tuple[re.Pattern, dict]] = [
    (
        re.compile(r"scaffold|flask|create.*project|stvegcир", re.I),
        {
            "intent": "scaffold",
            "commands": ["flask-basic demo_app"],
            "explanation": "Creates a basic Flask web project called demo_app",
            "is_dangerous": False,
            "requires_sudo": False,
            "affects_paths": ["./demo_app"],
        },
    ),
    (
        re.compile(r"python.?script|script.*project", re.I),
        {
            "intent": "scaffold",
            "commands": ["python-script my_script"],
            "explanation": "Creates a Python script project called my_script",
            "is_dangerous": False,
            "requires_sudo": False,
            "affects_paths": ["./my_script"],
        },
    ),
    (
        re.compile(r"\bwhat\b|\bexplain\b|\bhow\b|\bwhy\b|\binfo\b|inca", re.I),
        {
            "intent": "info",
            "commands": [],
            "explanation": "ls lists files in a directory. ls -lh shows sizes in human-readable format.",
            "is_dangerous": False,
            "requires_sudo": False,
            "affects_paths": [],
        },
    ),
    (
        re.compile(r"rm\s*-rf\s*/|delete.*root|destroy|format.*disk|fork.?bomb", re.I),
        {
            "intent": "dangerous",
            "commands": [],
            "explanation": "This would destroy the entire filesystem. Blocked for safety.",
            "is_dangerous": True,
            "requires_sudo": True,
            "affects_paths": ["/"],
        },
    ),
    (
        re.compile(r"process|running|ps\b|top\b", re.I),
        {
            "intent": "os_command",
            "commands": ["ps aux --sort=-%cpu | head -20"],
            "explanation": "Shows top 20 processes sorted by CPU usage",
            "is_dangerous": False,
            "requires_sudo": False,
            "affects_paths": [],
        },
    ),
    (
        re.compile(r"memory|ram|free\b", re.I),
        {
            "intent": "os_command",
            "commands": ["free -h"],
            "explanation": "Shows RAM usage in human-readable format",
            "is_dangerous": False,
            "requires_sudo": False,
            "affects_paths": [],
        },
    ),
    (
        re.compile(r"disk|storage|df\b|mount|du\b", re.I),
        {
            "intent": "os_command",
            "commands": ["df -h", "du -sh *"],
            "explanation": "Shows filesystem disk usage, then size of each item here",
            "is_dangerous": False,
            "requires_sudo": False,
            "affects_paths": [],
        },
    ),
    (
        re.compile(r"file|list|show|ls\b|dir\b", re.I),
        {
            "intent": "os_command",
            "commands": ["ls -lh"],
            "explanation": "Lists files in the current directory with sizes",
            "is_dangerous": False,
            "requires_sudo": False,
            "affects_paths": ["."],
        },
    ),
]

_FALLBACK = {
    "intent": "os_command",
    "commands": ["echo 'Mock provider: no rule matched'"],
    "explanation": "No matching rule — using fallback echo",
    "is_dangerous": False,
    "requires_sudo": False,
    "affects_paths": [],
}


class MockProvider(BaseLLMProvider):
    """Deterministic fake LLM — matches keywords, returns canned JSON responses."""

    def complete(self, system: str, messages: list[dict]) -> str:
        user_text = messages[-1]["content"] if messages else ""
        for pattern, response in _RULES:
            if pattern.search(user_text):
                return json.dumps(response)
        return json.dumps(_FALLBACK)

    def validate_api_key(self) -> bool:
        return True
