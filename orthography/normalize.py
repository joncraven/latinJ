"""Latin HTML orthography normaliser (library-site / latin.craven.fr standard).

Driven entirely by ``rules.json`` so new substitutions are data, not code.
Only text nodes are rewritten; tags, comments, scripts, and styles stay intact.
Every substitution is appended to an audit log.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

DEFAULT_RULES = Path(__file__).resolve().parent / "rules.json"

# Tags/comments whose inner text must not be rewritten.
_SKIP_BLOCKS = re.compile(
    r"(<!--.*?-->|<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<[^>]+>)",
    re.IGNORECASE | re.DOTALL,
)

LogEntry = dict[str, Any]
Rules = dict[str, Any]


def load_rules(path: str | Path | None = None) -> Rules:
    rules_path = Path(path) if path is not None else DEFAULT_RULES
    data = json.loads(rules_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"rules file must be a JSON object: {rules_path}")
    return data


def preserve_case(original: str, replacement: str) -> str:
    """If the rule replacement is lowercase, copy the match's case pattern."""
    if not replacement.islower():
        return replacement
    if original.isupper():
        return replacement.upper()
    if original and original[0].isupper():
        return replacement[0].upper() + replacement[1:]
    return replacement


def _protect_exceptions(text: str, exceptions: list[str]) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}
    for i, word in enumerate(sorted(exceptions, key=len, reverse=True)):
        token = f"\x00EXC{i}\x00"

        def repl(match: re.Match[str], tok: str = token) -> str:
            placeholders[tok] = match.group(0)
            return tok

        # Prefix, not whole-word: Israelis / Michaelis must stay unligatured.
        text = re.sub(rf"\b{re.escape(word)}", repl, text, flags=re.IGNORECASE)
    return text, placeholders


def _restore_exceptions(text: str, placeholders: dict[str, str]) -> str:
    for token, original in placeholders.items():
        text = text.replace(token, original)
    return text


def _log(log: list[LogEntry], rule_id: str, match: str, replacement: str, index: int) -> None:
    if match == replacement:
        return
    log.append(
        {
            "rule_id": rule_id,
            "match": match,
            "replacement": replacement,
            "index": index,
        }
    )


def _apply_map(
    text: str,
    items: list[dict[str, str]],
    log: list[LogEntry],
) -> str:
    # Longest source first so multi-char sequences win over letters.
    ordered = sorted(items, key=lambda r: len(r["from"]), reverse=True)
    for rule in ordered:
        src, dest, rid = rule["from"], rule["to"], rule["id"]
        if src not in text:
            continue
        start = 0
        pieces: list[str] = []
        while True:
            idx = text.find(src, start)
            if idx < 0:
                pieces.append(text[start:])
                break
            pieces.append(text[start:idx])
            pieces.append(dest)
            _log(log, rid, src, dest, idx)
            start = idx + len(src)
        text = "".join(pieces)
    return text


def _apply_regex_list(
    text: str,
    items: list[dict[str, str]],
    log: list[LogEntry],
    *,
    case_preserve: bool,
) -> str:
    for rule in items:
        flags = re.IGNORECASE if case_preserve else 0
        pattern = re.compile(rule["pattern"], flags)
        replacement = rule["replace"]
        rid = rule["id"]

        def repl(
            match: re.Match[str],
            *,
            _rid: str = rid,
            _repl: str = replacement,
            _preserve: bool = case_preserve,
        ) -> str:
            orig = match.group(0)
            new = preserve_case(orig, _repl) if _preserve else _repl
            _log(log, _rid, orig, new, match.start())
            return new

        text = pattern.sub(repl, text)
    return text


def normalize_text(text: str, rules: Rules) -> tuple[str, list[LogEntry]]:
    """Rewrite a plain-text (already de-tagged) Latin string. Returns text + log."""
    log: list[LogEntry] = []
    text = unicodedata.normalize("NFC", text)
    exceptions = list(rules.get("exceptions") or [])
    text, placeholders = _protect_exceptions(text, exceptions)

    text = _apply_map(text, list(rules.get("strip_combining") or []), log)
    text = _apply_map(text, list(rules.get("char_map") or []), log)
    text = _apply_regex_list(text, list(rules.get("regex") or []), log, case_preserve=False)
    text = _apply_regex_list(
        text, list(rules.get("word_regex") or []), log, case_preserve=True
    )

    text = _restore_exceptions(text, placeholders)
    return text, log


def normalize_html(html: str, rules: Rules) -> tuple[str, list[LogEntry]]:
    """Rewrite Latin in HTML text nodes only."""
    log: list[LogEntry] = []
    out: list[str] = []
    pos = 0
    for block in _SKIP_BLOCKS.finditer(html):
        if block.start() > pos:
            chunk = html[pos : block.start()]
            rewritten, chunk_log = normalize_text(chunk, rules)
            for entry in chunk_log:
                entry["index"] += pos
            log.extend(chunk_log)
            out.append(rewritten)
        out.append(block.group(0))
        pos = block.end()
    if pos < len(html):
        chunk = html[pos:]
        rewritten, chunk_log = normalize_text(chunk, rules)
        for entry in chunk_log:
            entry["index"] += pos
        log.extend(chunk_log)
        out.append(rewritten)
    return "".join(out), log


def normalize_file(
    input_path: str | Path,
    output_path: str | Path,
    rules: Rules,
    log_path: str | Path | None = None,
) -> list[LogEntry]:
    src = Path(input_path)
    dest = Path(output_path)
    html = src.read_text(encoding="utf-8")
    rewritten, log = normalize_html(html, rules)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rewritten, encoding="utf-8")
    if log_path is not None:
        lp = Path(log_path)
        lp.parent.mkdir(parents=True, exist_ok=True)
        with lp.open("w", encoding="utf-8") as fh:
            for entry in log:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return log
