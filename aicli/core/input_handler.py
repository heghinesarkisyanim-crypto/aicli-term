"""Input handler — parse and clean user input, detect language."""

from __future__ import annotations

import re
import unicodedata

from aicli.interfaces import Language, ParsedInput

# Armenian Unicode block: U+0531–U+058F
_ARMENIAN_RE = re.compile(r"[\u0531-\u058f]")


def parse_input(raw: str) -> ParsedInput:
    """Clean raw input and detect language (Armenian or English)."""
    text = _clean(raw)
    language = _detect_language(text)
    return ParsedInput(text=text, language=language)


def _clean(text: str) -> str:
    # Normalise unicode
    text = unicodedata.normalize("NFC", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Remove control characters
    text = re.sub(r"[\x00-\x1f\x7f]", "", text)
    return text


def _detect_language(text: str) -> Language:
    if _ARMENIAN_RE.search(text):
        return Language.HY
    return Language.EN
