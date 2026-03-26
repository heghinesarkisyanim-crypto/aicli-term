"""Tests for the 3-layer security shield."""

import pytest

from aicli.interfaces import CommandRequest
from aicli.security.shield import SecurityShield


def _req(command: str | list, is_dangerous: bool = False, affects_paths=None, requires_sudo: bool = False):
    commands = [command] if isinstance(command, str) else command
    return CommandRequest(
        commands=commands,
        explanation="test",
        is_dangerous=is_dangerous,
        requires_sudo=requires_sudo,
        affects_paths=affects_paths or [],
    )


@pytest.fixture
def shield():
    return SecurityShield(confirm_dangerous=True)


# --- Layer 1: Keyword blocklist ---

def test_rm_rf_root_blocked(shield):
    result = shield.check(_req("rm -rf /"))
    assert not result.allowed


def test_fork_bomb_blocked(shield):
    result = shield.check(_req(":(){ :|:& };:"))
    assert not result.allowed


def test_mkfs_blocked(shield):
    result = shield.check(_req("mkfs.ext4 /dev/sda1"))
    assert not result.allowed


def test_dd_blocked(shield):
    result = shield.check(_req("dd if=/dev/zero of=/dev/sda"))
    assert not result.allowed


def test_blocked_pattern_in_second_command(shield):
    """Dangerous command in a multi-command list is still caught."""
    result = shield.check(_req(["ls -lh", "rm -rf /"]))
    assert not result.allowed


# --- Layer 2: is_dangerous flag ---

def test_dangerous_flag_requires_confirmation(shield):
    result = shield.check(_req("rm -rf /tmp/old", is_dangerous=True))
    assert result.allowed
    assert result.needs_confirmation


def test_dangerous_flag_blocked_when_confirm_disabled():
    shield = SecurityShield(confirm_dangerous=False)
    result = shield.check(_req("some-cmd", is_dangerous=True))
    assert not result.allowed


# --- Layer 3: Critical path ---

def test_critical_path_requires_confirmation(shield):
    result = shield.check(_req("cat /etc/passwd", affects_paths=["/etc/passwd"]))
    assert result.allowed
    assert result.needs_confirmation


def test_safe_path_no_confirmation(shield):
    result = shield.check(_req("ls /home/user"))
    assert result.allowed
    assert not result.needs_confirmation


# --- Confirmation patterns ---

def test_rm_command_requires_confirmation(shield):
    result = shield.check(_req("rm -f myfile.txt"))
    assert result.allowed
    assert result.needs_confirmation


def test_sudo_requires_confirmation(shield):
    result = shield.check(_req("sudo apt-get update"))
    assert result.allowed
    assert result.needs_confirmation


def test_safe_ls_no_confirmation(shield):
    result = shield.check(_req("ls -lh"))
    assert result.allowed
    assert not result.needs_confirmation


def test_multi_command_safe(shield):
    result = shield.check(_req(["mkdir projects", "ls -lh projects"]))
    assert result.allowed
    assert not result.needs_confirmation
