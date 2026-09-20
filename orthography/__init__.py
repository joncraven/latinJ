"""orthography package — Latin HTML orthography normalisation."""

from .normalize import (
    DEFAULT_RULES,
    load_rules,
    normalize_file,
    normalize_html,
    normalize_text,
)

__all__ = [
    "DEFAULT_RULES",
    "load_rules",
    "normalize_file",
    "normalize_html",
    "normalize_text",
]
