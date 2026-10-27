#!/usr/bin/env python3
"""latinj v2 — make ugly Latin look good (j, and æ where it belongs).

The workflow is unchanged: unformatted Latin in, corrected Latin out.

Usage:
  latinj                       # read stdin, write corrected text to stdout
  latinj FILE [FILE...]        # corrected text to stdout
  latinj -i FILE [FILE...]     # correct the files in place
  cat input.txt | latinj > out.txt

Replaces the old ``perl clean.pl`` workflow: there is no more ``fixed/``
directory requirement — pass ``-i`` to fix files in place, or redirect
stdout.  HTML input is detected automatically and rewritten text-node-safe
(tags, attributes, <script>, <style> and comments are never touched).

The rule set lives in ``orthography/rules.json`` — new substitutions are
data, not code.  Every substitution can be logged with ``--log audit.jsonl``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orthography.normalize import DEFAULT_RULES, load_rules, normalize_html, normalize_text  # noqa: E402

_TAG_HINT = re.compile(r"</?[a-zA-Z!/]")

# Post-pass for --style unicode: undo the site-standard entity output.
ENTITY_TO_UNICODE = [("&aelig;", "æ"), ("&AElig;", "Æ")]


def correct(text: str, rules, *, style: str = "entity", log=None) -> str:
    """Correct one blob of Latin (auto-detecting HTML vs plain text)."""
    mode = "html" if _TAG_HINT.search(text) else "text"
    if mode == "html":
        out, entries = normalize_html(text, rules)
    else:
        out, entries = normalize_text(text, rules)
    if style == "unicode":
        for src, dest in ENTITY_TO_UNICODE:
            n = out.count(src)
            if n:
                out = out.replace(src, dest)
                if log is not None:
                    log.append(
                        {
                            "rule_id": "style_unicode",
                            "match": src,
                            "replacement": dest,
                            "index": -1,
                            "count": n,
                        }
                    )
    if log is not None:
        log.extend(entries)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="latinj",
        description="Correct Latin orthography (consonantal i→j, ae ligature, macrons).",
    )
    parser.add_argument("files", nargs="*", type=Path, help="Input files (default: stdin)")
    parser.add_argument(
        "--rules", type=Path, default=DEFAULT_RULES,
        help="JSON rules file (default: orthography/rules.json)",
    )
    parser.add_argument(
        "--style", choices=("entity", "unicode"), default="entity",
        help="ae output form: &aelig; entities (site standard, default) or Unicode æ",
    )
    parser.add_argument(
        "-i", "--in-place", action="store_true",
        help="Rewrite the input files in place (otherwise corrected text goes to stdout)",
    )
    parser.add_argument(
        "--log", type=Path, default=None,
        help="Write one JSON object per substitution (JSONL) for auditing",
    )
    parser.add_argument("--version", action="version", version="latinj 2.0.0")
    args = parser.parse_args(argv)

    rules = load_rules(args.rules)
    audit: list[dict] = []

    if not args.files or all(p.name == "-" for p in args.files):
        text = sys.stdin.read()
        sys.stdout.write(correct(text, rules, style=args.style, log=audit))
        if audit and args.log is None and not sys.stdout.isatty():
            pass  # no implicit log to stdout; summary goes to stderr
    elif args.in_place:
        for path in args.files:
            if not path.is_file():
                parser.error(f"input not found: {path}")
            original = path.read_text(encoding="utf-8")
            fixed = correct(original, rules, style=args.style, log=audit)
            if fixed != original:
                path.write_text(fixed, encoding="utf-8")
    else:
        chunks = []
        for path in args.files:
            if not path.is_file():
                parser.error(f"input not found: {path}")
            chunks.append(correct(path.read_text(encoding="utf-8"), rules, style=args.style, log=audit))
        sys.stdout.write("\n".join(chunks))

    if args.log is not None:
        with args.log.open("w", encoding="utf-8") as fh:
            for entry in audit:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"latinj: {len(audit)} substitution(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
