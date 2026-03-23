"""Security shield — 3-layer validation before command execution."""

from __future__ import annotations

from dataclasses import dataclass

from aicli.interfaces import CommandRequest
from aicli.security.patterns import (
    BLOCKED_PATTERNS,
    CRITICAL_PATHS,
    REQUIRES_CONFIRMATION_PATTERNS,
)


@dataclass
class ShieldResult:
    allowed: bool
    needs_confirmation: bool = False
    reason: str = ""


class SecurityShield:
    def __init__(self, confirm_dangerous: bool = True) -> None:
        self._confirm_dangerous = confirm_dangerous

    def check(self, req: CommandRequest) -> ShieldResult:
        """Run all 3 security layers against every command in the request."""

        # Layer 1: Keyword blocklist — hard block against ALL commands, no bypass
        for cmd in req.commands:
            for pattern in BLOCKED_PATTERNS:
                if pattern.search(cmd):
                    return ShieldResult(
                        allowed=False,
                        reason=f"Command '{cmd[:60]}' matches blocked pattern.",
                    )

        # Layer 2: is_dangerous flag from LLM
        if req.is_dangerous:
            if not self._confirm_dangerous:
                return ShieldResult(
                    allowed=False,
                    reason="Command flagged as dangerous by AI analysis.",
                )
            return ShieldResult(
                allowed=True,
                needs_confirmation=True,
                reason="AI flagged this command as potentially dangerous.",
            )

        # Layer 3: Critical path protection
        for path in req.affects_paths:
            for critical in CRITICAL_PATHS:
                if path.startswith(critical):
                    return ShieldResult(
                        allowed=True,
                        needs_confirmation=True,
                        reason=f"Command affects critical system path: {path}",
                    )

        # Confirmation patterns (rm, sudo, chmod, etc.) — check all commands
        for cmd in req.commands:
            for pattern in REQUIRES_CONFIRMATION_PATTERNS:
                if pattern.search(cmd):
                    return ShieldResult(
                        allowed=True,
                        needs_confirmation=True,
                        reason=f"Command requires confirmation: {cmd[:60]}",
                    )

        return ShieldResult(allowed=True)
