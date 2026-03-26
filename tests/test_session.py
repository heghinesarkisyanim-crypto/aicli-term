"""Tests for session manager."""

import pytest

from aicli.core.session import SessionManager


@pytest.fixture
def session(tmp_path):
    return SessionManager(
        history_file=str(tmp_path / "history.json"),
        history_size=5,
        context_window=3,
    )


def test_add_and_retrieve(session):
    session.add_entry("show files", "ls -lh", "success")
    history = session.get_history()
    assert len(history) == 1
    assert history[0]["user"] == "show files"
    assert history[0]["result"] == "success"


def test_context_window_limits(session):
    for i in range(10):
        session.add_entry(f"cmd {i}", f"result {i}", "ok")
    context = session.get_context()
    assert len(context) == 3  # context_window=3


def test_history_size_limit(session):
    for i in range(10):
        session.add_entry(f"cmd {i}", f"result {i}", "ok")
    history = session.get_history()
    assert len(history) == 5  # history_size=5


def test_persistence(tmp_path):
    history_path = str(tmp_path / "history.json")
    s1 = SessionManager(history_file=history_path)
    s1.add_entry("hello", "ls", "success")

    s2 = SessionManager(history_file=history_path)
    assert len(s2.get_history()) == 1
    assert s2.get_history()[0]["user"] == "hello"


def test_clear(session):
    session.add_entry("cmd", "result", "ok")
    session.clear()
    assert session.get_history() == []


def test_corrupted_history_file(tmp_path):
    path = tmp_path / "history.json"
    path.write_text("not valid json")
    # Should not crash; starts fresh
    session = SessionManager(history_file=str(path))
    assert session.get_history() == []
