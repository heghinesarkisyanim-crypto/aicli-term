"""Tests for LLM engine — JSON parsing and retry logic."""

import json
from unittest.mock import MagicMock

import pytest

from aicli.interfaces import Intent
from aicli.llm.engine import LLMEngine


def _make_engine(response_text: str, fail_times: int = 0):
    """Build an LLMEngine with a mocked provider."""
    provider = MagicMock()
    call_count = {"n": 0}

    def complete(system, messages):
        call_count["n"] += 1
        if call_count["n"] <= fail_times:
            raise ValueError("simulated bad JSON")
        return response_text

    provider.complete.side_effect = complete
    return LLMEngine(provider, max_retries=3)


# New-style responses with "commands" list
_VALID_RESPONSE = json.dumps({
    "intent": "os_command",
    "commands": ["ls -lh"],
    "explanation": "Lists files",
    "is_dangerous": False,
    "requires_sudo": False,
    "affects_paths": ["."],
})

_MULTI_COMMAND_RESPONSE = json.dumps({
    "intent": "os_command",
    "commands": ["mkdir projects", "ls -lh projects"],
    "explanation": "Creates directory then lists it",
    "is_dangerous": False,
    "requires_sudo": False,
    "affects_paths": ["./projects"],
})

_INFO_RESPONSE = json.dumps({
    "intent": "info",
    "commands": [],
    "explanation": "grep searches for patterns",
    "is_dangerous": False,
    "requires_sudo": False,
    "affects_paths": [],
})

_SCAFFOLD_RESPONSE = json.dumps({
    "intent": "scaffold",
    "commands": ["flask-basic myapp"],
    "explanation": "Creates Flask project",
    "is_dangerous": False,
    "requires_sudo": False,
    "affects_paths": ["./myapp"],
})

# Old-style single "command" string — backwards compat
_LEGACY_RESPONSE = json.dumps({
    "intent": "os_command",
    "command": "ls -lh",
    "explanation": "Lists files",
    "is_dangerous": False,
    "requires_sudo": False,
    "affects_paths": ["."],
})


def test_parses_os_command():
    engine = _make_engine(_VALID_RESPONSE)
    resp = engine.process("show files", "en", [])
    assert resp.intent == Intent.OS_COMMAND
    assert resp.commands == ["ls -lh"]
    assert resp.command == "ls -lh"
    assert not resp.is_dangerous


def test_parses_multi_command():
    engine = _make_engine(_MULTI_COMMAND_RESPONSE)
    resp = engine.process("create projects dir and list it", "en", [])
    assert resp.intent == Intent.OS_COMMAND
    assert len(resp.commands) == 2
    assert resp.commands[0] == "mkdir projects"
    assert resp.commands[1] == "ls -lh projects"


def test_parses_info_intent():
    engine = _make_engine(_INFO_RESPONSE)
    resp = engine.process("what is grep", "en", [])
    assert resp.intent == Intent.INFO
    assert resp.commands == []


def test_parses_scaffold_intent():
    engine = _make_engine(_SCAFFOLD_RESPONSE)
    resp = engine.process("create flask project", "en", [])
    assert resp.intent == Intent.SCAFFOLD
    assert resp.commands == ["flask-basic myapp"]


def test_backwards_compat_single_command_field():
    """Old 'command' string field must still parse correctly."""
    engine = _make_engine(_LEGACY_RESPONSE)
    resp = engine.process("show files", "en", [])
    assert resp.commands == ["ls -lh"]


def test_retries_on_bad_json():
    engine = _make_engine(_VALID_RESPONSE, fail_times=2)
    resp = engine.process("show files", "en", [])
    assert resp.intent == Intent.OS_COMMAND


def test_raises_after_max_retries():
    engine = _make_engine(_VALID_RESPONSE, fail_times=99)
    with pytest.raises(RuntimeError, match="LLM failed"):
        engine.process("show files", "en", [])


def test_strips_markdown_fences():
    wrapped = "```json\n" + _VALID_RESPONSE + "\n```"
    engine = _make_engine(wrapped)
    resp = engine.process("show files", "en", [])
    assert resp.commands == ["ls -lh"]


def test_ignores_trailing_prose():
    with_prose = _VALID_RESPONSE + "\n\nHere is the explanation of the command above."
    engine = _make_engine(with_prose)
    resp = engine.process("show files", "en", [])
    assert resp.commands == ["ls -lh"]
