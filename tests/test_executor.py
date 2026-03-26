"""Tests for the command executor."""

import pytest

from aicli.core.executor import Executor


@pytest.fixture
def executor():
    return Executor(timeout=5)


def test_successful_command(executor):
    result = executor.run("echo hello")
    assert result.success
    assert "hello" in result.stdout


def test_exit_code_captured(executor):
    result = executor.run("false")  # always exits 1
    assert not result.success
    assert result.exit_code == 1


def test_command_not_found(executor):
    result = executor.run("this_command_does_not_exist_xyz")
    assert not result.success
    assert result.exit_code == 127
    assert "not found" in result.stderr.lower()


def test_stderr_captured(executor):
    result = executor.run("ls /nonexistent_path_xyz")
    assert not result.success
    assert result.stderr.strip() != ""


def test_invalid_syntax(executor):
    # Unmatched quotes → shlex.split fails
    result = executor.run('echo "unclosed')
    assert not result.success


def test_cwd_respected(executor, tmp_path):
    result = executor.run("pwd", cwd=str(tmp_path))
    assert result.success
    assert str(tmp_path) in result.stdout


def test_pipe_command_works(executor):
    # Commands with pipes are routed through sh -c and work correctly
    result = executor.run("echo hello | tr a-z A-Z")
    assert result.success
    assert "HELLO" in result.stdout


def test_simple_command_no_shell(executor):
    # Commands without shell operators use shlex.split (no shell process)
    result = executor.run("echo hello world")
    assert result.success
    assert result.stdout.strip() == "hello world"
