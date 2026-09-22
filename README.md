# latinJ
Utilities to update documents in Latin to use v, j, and æ for improved readibility

## Version 2 (orthography-v2)

The v1 `clean.pl` had a brittle workflow (mandatory `fixed/` directory, forced
`.html` rename, cwd-only paths) and known bugs (case-smashing `vbi`→`Ubi`,
Roman numerals destroyed at end of line, `ieiunium`→`jeiunium`, greedy
`aer`/`aether` ligatures). It is superseded by **`latinj`**, a Python port of
the battle-tested orthography pipeline from the latin-audiobooks project
(decision memo `orthography-compare-decision-memo.md`, 2026-09-19).

The user-facing workflow is unchanged: **unformatted Latin in → corrected
Latin out.**

```console
$ latinj                          # stdin → stdout
$ echo "iam maior praesidium" | latinj
jam major pr&aelig;sidium
$ latinj FILE [FILE...]           # corrected text to stdout
$ latinj -i FILE...               # correct files in place (replaces the fixed/ dir)
$ latinj --style unicode FILE     # Unicode æ output instead of &aelig; entities
$ latinj --log audit.jsonl FILE   # one JSON line per substitution, for QA
```

`clean.pl` is kept for reference but receives no further development.

### What v2 does

| Feature | Policy |
|---|---|
| consonantal *i* | written `j` — `iam→jam`, `eius→ejus`, `iustitia→justitia`, plus QA-validated prefix compounds (`adiutor→adjutor`, `inicit→injicit`, `abiecit→abjecit`, `traiectum→trajectum`) |
| `ae` diphthong | `&aelig;`/`&AElig;` by default (`--style unicode` for `æ`), with position-free exceptions for Hebrew names (`Israel`, `Michaelis`, …) |
| `oe` | spelled out; `œ` expands, `&oelig;` is never emitted |
| macrons/breves | stripped (precomposed and combining) |
| `u`/`v` | left as in the source — deliberate: the corpus is mixed |
| Roman numerals | never touched (no destructive `V→U`/`U→V` pass, so `IV` stays `IV`) |
| capitalisation | preserved (`Iam→Jam`, `MAIOR→MAJOR`) |
| HTML input | detected automatically; tags, attributes, `<script>`, `<style>`, comments are never rewritten |
| NFD input | NFC-normalised first (no more `a`+◌̈ corruption) |
| idempotency | running the fixer twice changes nothing the second time |
| auditability | `--log` writes every substitution as JSONL |

Rules live in `orthography/rules.json` — new corrections are data, not code.
The formal rule-set document (`docs/orthography-ruleset.formal.yaml`, approved
in t_d270dcf7) is the spec; every example pair it cites is pinned as a test
(`tests/test_ruleset_examples.py`), and the parent deliverable `ruleset.json`
carries the same five rule arrays (`exceptions`, `char_map`, `strip_combining`,
`regex`, `word_regex`) as `orthography/rules.json` v1.2.0 — verified identical.

### Development

```console
$ python3 -m venv .venv && .venv/bin/pip install pytest
$ .venv/bin/python -m pytest tests/ -q     # 63 tests
```

`tests/test_orthography_normalize.py` is the ported engine suite;
`tests/test_latinj_cli.py` is the v2 CLI + regression battery;
`tests/test_ruleset_examples.py` replays every example pair in the formal
rule-set through the CLI (generated from the YAML spec).
