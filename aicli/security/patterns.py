"""Security patterns — blocked commands and critical filesystem paths."""

from __future__ import annotations

import re

# Commands that are always blocked (no confirmation possible)
BLOCKED_PATTERNS: list[re.Pattern] = [
    re.compile(r"rm\s+-rf\s+/\s*$"),            # rm -rf / (root wipe)
    re.compile(r">\s*/dev/sd[a-z]"),             # Disk overwrite
    re.compile(r"mkfs"),                          # Filesystem format
    re.compile(r"dd\s+if="),                      # Disk duplication/wipe
    re.compile(r":\(\)\s*\{.*:\|:.*\}.*;:"),     # Fork bomb
    re.compile(r"base64\s+-d.*\|.*sh"),           # Encoded shell injection
    re.compile(r"chmod\s+[0-7]*7\s+/\s*$"),      # chmod 777 / (root permissions)
    re.compile(r"shred\s+.*/(dev|boot|sys)"),    # Shred system devices
]

# Paths that require explicit user confirmation
CRITICAL_PATHS: set[str] = {
    "/etc",
    "/boot",
    "/sys",
    "/proc",
    "/dev",
    "/root",
    "/usr/bin",
    "/usr/lib",
}

# Command prefixes that always need confirmation
REQUIRES_CONFIRMATION_PATTERNS: list[re.Pattern] = [
    re.compile(r"^\s*sudo\s+"),
    re.compile(r"^\s*rm\s+"),
    re.compile(r"^\s*chmod\s+"),
    re.compile(r"^\s*chown\s+"),
    re.compile(r"^\s*mv\s+.*\.\./"),
]
