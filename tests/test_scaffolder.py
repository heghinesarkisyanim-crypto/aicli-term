"""Tests for the scaffolding system."""

import pytest

from aicli.automation.scaffolder import Scaffolder
from aicli.interfaces import ScaffoldRequest


@pytest.fixture
def scaffolder():
    return Scaffolder()


def test_flask_basic_scaffold(scaffolder, tmp_path):
    req = ScaffoldRequest(
        template="flask-basic",
        project_name="testapp",
        target_dir=str(tmp_path / "testapp"),
    )
    created = scaffolder.scaffold(req)
    assert len(created) > 0

    # Check key files exist
    target = tmp_path / "testapp"
    assert (target / "app.py").exists()
    assert (target / "requirements.txt").exists()


def test_python_script_scaffold(scaffolder, tmp_path):
    req = ScaffoldRequest(
        template="python-script",
        project_name="myscript",
        target_dir=str(tmp_path / "myscript"),
    )
    scaffolder.scaffold(req)
    target = tmp_path / "myscript"
    assert (target / "main.py").exists()
    assert (target / "requirements.txt").exists()


def test_project_name_in_file(scaffolder, tmp_path):
    req = ScaffoldRequest(
        template="python-script",
        project_name="awesome_tool",
        target_dir=str(tmp_path / "awesome_tool"),
    )
    scaffolder.scaffold(req)
    content = (tmp_path / "awesome_tool" / "main.py").read_text()
    assert "awesome_tool" in content


def test_existing_dir_raises(scaffolder, tmp_path):
    (tmp_path / "existing").mkdir()
    req = ScaffoldRequest(
        template="python-script",
        project_name="existing",
        target_dir=str(tmp_path / "existing"),
    )
    with pytest.raises(FileExistsError):
        scaffolder.scaffold(req)


def test_unknown_template_raises(scaffolder, tmp_path):
    req = ScaffoldRequest(
        template="nonexistent-template",
        project_name="proj",
        target_dir=str(tmp_path / "proj"),
    )
    with pytest.raises(ValueError, match="Unknown template"):
        scaffolder.scaffold(req)


def test_rollback_on_failure(scaffolder, tmp_path, monkeypatch):
    """If rendering fails mid-way, no directory should remain."""
    def failing_render(self, *args, **kwargs):
        raise RuntimeError("Simulated render failure")

    monkeypatch.setattr(Scaffolder, "_render_tree", failing_render)

    req = ScaffoldRequest(
        template="python-script",
        project_name="failproj",
        target_dir=str(tmp_path / "failproj"),
    )
    with pytest.raises(RuntimeError):
        scaffolder.scaffold(req)

    assert not (tmp_path / "failproj").exists()
