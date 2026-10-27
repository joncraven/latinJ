#!/usr/bin/env python3
"""CLI: rewrite a raw Latin HTML page to the site orthography standard.

Usage:
  python3 scripts/normalize_orthography.py INPUT.html OUTPUT.html
  python3 scripts/normalize_orthography.py INPUT.html OUTPUT.html \\
      --rules orthography/rules.json --log substitutions.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orthography.normalize import DEFAULT_RULES, load_rules, normalize_file  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Normalise Latin HTML orthography to the latin.craven.fr corpus standard."
    )
    parser.add_argument("input", type=Path, help="Raw Latin HTML file")
    parser.add_argument("output", type=Path, help="Destination HTML path")
    parser.add_argument(
        "--rules",
        type=Path,
        default=DEFAULT_RULES,
        help="JSON rules file (default: orthography/rules.json)",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=None,
        help="Write one JSON object per substitution (JSONL). Defaults to <output>.log.jsonl",
    )
    args = parser.parse_args(argv)

    if not args.input.is_file():
        parser.error(f"input not found: {args.input}")
    log_path = args.log if args.log is not None else Path(str(args.output) + ".log.jsonl")
    rules = load_rules(args.rules)
    log = normalize_file(args.input, args.output, rules, log_path=log_path)
    summary = {
        "input": str(args.input),
        "output": str(args.output),
        "rules": str(args.rules),
        "log": str(log_path),
        "substitutions": len(log),
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
