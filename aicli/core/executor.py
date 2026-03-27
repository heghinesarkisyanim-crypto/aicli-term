from __future__ import annotations

import os
import pty
import select
import shlex
import subprocess
import sys

from aicli.interfaces import ExecutionResult


def _needs_tty(args: list[str]) -> bool:
    """Dynamically detect whether a command requires a real TTY.
 
    Instead of a hardcoded list, we inspect the binary itself:
    - If the command is not found in PATH at all, return False early.
    - Run the command with --help piped to /dev/null, then check whether
      it re-opens /dev/tty directly (like `clear`, `reset`, `vim` do) by
      examining its file descriptors via /proc — not portable, but works on Linux.
 
    The reliable cross-platform signal is simpler: probe whether the binary
    is linked against curses/terminfo (via `file` or `ldd`).  But the most
    practical approach that requires zero prior knowledge is:
 
      Run with stdout redirected to a pipe.  If the process produces nothing
      on stdout but exits 0, it likely wrote directly to the TTY — so rerun
      it without capturing.  If it produces output on the pipe, capture it.
 
    We implement a two-phase probe:
      Phase 1 — try capturing via a PTY so the subprocess thinks it has a
                 terminal.  A PTY is a fake terminal that still lets us read
                 the output, so `clear` will emit escape codes, `vim` will
                 start its UI, etc.
      Phase 2 — read back what the PTY produced.  If it contains terminal
                 control sequences (ESC[...) and no printable payload, we
                 classify it as a TTY-rewriting command and hand control
                 directly to the real terminal instead of capturing.
    """


    if not args:
        return False

    if args[0] == "sh" and len(args) >= 3:
        first_word = shlex.split(args[2])[0] if args[2].strip() else ""
    else:
        first_word = os.path.basename(args[0])

    try:
        master_fd, slave_fd = pty.openpty()
        probe = subprocess.Popen(
            args,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
            env={**os.environ, "TERM": "xterm-256color", "COLUMNS": "80", "LINES": "24"},
            )
        os.close(slave_fd)

        output = b""

        ready, _, _ = select.select([master_fd], [], [], 0.15)
        if ready:
            try:
                output = os.read(master_fd, 4096)
            except OSError:
                pass

        try:
            probe.kill()
            probe.wait(timeout=1)
        except Exception:
            pass
        os.close(master_fd)

        return output.startswith(b"\x1b[") or output.startswith(b"\x1b(")

    except Exception:
        return False


class Executor:
    def __init__(self, timeout: int = 30) -> None:
        self._timeout = timeout

    def run(self, command: str, cwd: str | None = None) -> ExecutionResult:
        """Execute a command and return the result.

        Commands containing shell operators are executed via ['sh', '-c', command].
        We dynamically detect whether the command needs a real TTY by probing it
        with a pseudo-terminal — no hardcoded command list required.
        """
        has_shell_ops = any(op in command for op in ("|", "&&", "||", ">", "<", ";"))

        try:
            if has_shell_ops:
                args = ["sh", "-c", command]
            else:
                args = shlex.split(command)
        except ValueError as exc:
            return ExecutionResult(
                stdout="",
                stderr=f"Invalid command syntax: {exc}",
                exit_code=1,
                command=command,
            )

        try:
            if _needs_tty(args):
                result = subprocess.run(
                    args,
                    stdin=sys.stdin,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    timeout=self._timeout,
                    cwd=cwd,
                )
                return ExecutionResult(
                    stdout="",
                    stderr="",
                    exit_code=result.returncode,
                    command=command,
                )
            else:
                result = subprocess.run(
                    args,
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
