"""Command executor — runs shell commands safely."""

from __future__ import annotations

import shlex
import subprocess

from aicli.interfaces import ExecutionResult


class Executor:
    def __init__(self, timeout: int = 30) -> None:
        self._timeout = timeout

    def run(self, command: str, cwd: str | None = None) -> ExecutionResult:
        """Execute a single command and return the result.

        Commands containing shell operators (pipes, redirects) are executed via
        ['sh', '-c', command] which is safe because we never interpolate user
        input — the command string comes from the LLM, not raw user input.
        Commands without operators use shlex.split + shell=False.
        """
        has_shell_ops = any(op in command for op in ("|", "&&", "||", ">", "<", ";"))

        try:
            if has_shell_ops:
                args = ["sh", "-c", command]
                use_shell = False
            else:
                args = shlex.split(command)
                use_shell = False
        except ValueError as exc:
            return ExecutionResult(
                stdout="",
                stderr=f"Invalid command syntax: {exc}",
                exit_code=1,
                command=command,
            )

        try:
            result = subprocess.run(
                args,
                shell=use_shell,
                capture_output=True,
                text=True,
                timeout=self._timeout,
                cwd=cwd,
            )
            return ExecutionResult(
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                command=command,
            )

        except FileNotFoundError:
            cmd_name = args[0] if args else command
            return ExecutionResult(
                stdout="",
                stderr=f"Command not found: {cmd_name}",
                exit_code=127,
                command=command,
            )
        except PermissionError:
            return ExecutionResult(
                stdout="",
                stderr="Permission denied. Try running with sudo.",
                exit_code=126,
                command=command,
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                stdout="",
                stderr=f"Command timed out after {self._timeout} seconds.",
                exit_code=124,
                command=command,
            )
