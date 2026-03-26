"""Tests for input handler — language detection and input cleaning."""

from aicli.core.input_handler import parse_input
from aicli.interfaces import Language


def test_english_detected():
    result = parse_input("show files in current directory")
    assert result.language == Language.EN


def test_armenian_detected():
    result = parse_input("ցույց տուր ֆայլերը")
    assert result.language == Language.HY


def test_mixed_language_detects_armenian():
    # Armenian chars present → HY
    result = parse_input("list files ֆայլ")
    assert result.language == Language.HY


def test_whitespace_collapsed():
    result = parse_input("  show    files  ")
    assert result.text == "show files"


def test_control_chars_removed():
    result = parse_input("show\x00files\x1f")
    assert "\x00" not in result.text
    assert "\x1f" not in result.text


def test_empty_string():
    result = parse_input("   ")
    assert result.text == ""
    assert result.language == Language.EN


def test_unicode_normalized():
    # Should not crash on various unicode inputs
    result = parse_input("ñoño café")
    assert result.text == "ñoño café"
