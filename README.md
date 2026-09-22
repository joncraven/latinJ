# latinJ
Utilities to update documents in Latin to use v, j, and æ for improved readibility

## Orthography fixer (`latinj` v2)

`latinj` normalises raw Latin to the **latin.craven.fr** reading standard
(the Latin.war / The Latin Library convention): consonantal `i→j`, the `ae`
ligature (`&aelig;`/`&AElig;`), and clean handling of `oe`, macrons, and HTML.
It is a Python port of the battle-tested orthography pipeline from the
latin-audiobooks project (design rationale: decision memo
`orthography-compare-decision-memo.md`, 2026-09-19, option (b), in that
sibling repo's `docs/`): the local pipeline is the base, Perl's rule
knowledge backfilled **as data** into `orthography/rules.json`, the Perl
mechanics dropped. The v1 `clean.pl` had a brittle workflow (mandatory
`fixed/` directory, forced `.html` rename, cwd-only paths) and known bugs
(case-smashing `vbi`→`Ubi`, Roman numerals destroyed at end of line,
`ieiunium`→`jeiunium`, greedy `aer`/`aether` ligatures); it is kept for
reference but receives no further development.

The user-facing workflow is unchanged: **unformatted Latin in → corrected Latin
out.**

### Quick start

`latinj` is a thin shell shim plus `latinj.py` and the `orthography/` rule
directory; it must stay next to them (it loads `orthography/rules.json` relative
to itself). You already have them when you clone the repo:

```console
$ cd latinJ && git checkout orthography-v2          # the fixer lives on this branch
$ echo "iam maius praesidium" | ./latinj            # run the shim in place, or:
$ export PATH="$PATH:$(pwd)" && echo "iam" | latinj # bare `latinj` on your PATH
$ cat input.txt | latinj > output.txt               # raw in / raw out
$ latinj -i chapter.html                            # correct a file in place
```

Requires only Python 3 (standard library only — no `pip install`). To use the
shim from anywhere, copy `latinj`, `latinj.py`, and the `orthography/`
directory together onto a directory that is on your `PATH` (copying the shim
alone fails — it can't find its engine).

### Usage

```console
$ latinj                           # stdin -> stdout
$ echo "iam maior praesidium" | latinj
jam major pr&aelig;sidium
$ latinj FILE [FILE...]            # corrected text to stdout
$ latinj -i FILE...                # correct files in place (replaces the fixed/ dir)
$ latinj --style unicode FILE      # Unicode æ/Æ output instead of &aelig; entities
$ latinj --log audit.jsonl FILE    # one JSON line per substitution, for QA
$ latinj --version                 # latinj 2.0.0
```

`--rules PATH` selects a different rule file (default `orthography/rules.json`);
`--version` prints `latinj 2.0.0`.

Every run prints a `latinj: N substitution(s)` count to stderr; with `--style
unicode` the same pass emits `æ`/`Æ` instead of entities (`aether`→`æther`).

### What `latinj` does

| Feature | Policy |
|---|---|
| consonantal `i` | written `j` — `iam→jam`, `eius→ejus`, `iustitia→justitia`, plus QA-validated prefix compounds (`adiutor→adjutor`, `conicit→conjicit` via `conici`, `abiecit→abjecit` via `abic`, `traiectum→trajectum` via `traiect`, `traiecit→trajecit` via `traieci`) |
| `ae` diphthong | `&aelig;`/`&AElig;` by default (`--style unicode` for `æ`/`Æ`), with position-free exceptions for Hebrew names (`Israel`, `Michaelis`, …) |
| `oe` | spelled out; `œ` expands, `&oelig;` is never emitted |
| macrons / breves / diaeresis | stripped (precomposed and combining, after NFC-normalise) |
| `u` / `v` | left as in the source — deliberate: the corpus is mixed |
| Roman numerals | never touched (no destructive `V→U`/`U→V` pass, so `IV`/`MVII`/`CVIII` stay intact) |
| capitalisation | preserved (`Iam→Jam`, `MAIOR→MAJOR`) |
| HTML input | detected automatically; tags, attributes, `<script>`, `<style>`, comments are never rewritten |
| idempotency | running the fixer twice changes nothing the second time |
| auditability | `--log` writes every substitution as JSONL (`rule_id`, `match`, `replacement`, `index`) |

The rule set (v1.2.0: `char_map` 30, `regex` 3, `word_regex` 70,
`strip_combining` 2, `exceptions` 10) lives in `orthography/rules.json` — new
corrections are data, not code.
A human-readable copy of the same five arrays lives in
`docs/orthography-ruleset.formal.yaml`; it is the reference for adding rules, and
every example pair it cites is pinned as a test in `tests/test_ruleset_examples.py`
(same counts as `orthography/rules.json` v1.2.0) so the data and the doc cannot drift.

### Not done (by design)

- **`u`/`v` and its prefixes** are never converted (memo §5 / rows 9–11).
- Perl's `V→U` pass is **out of scope** — it case-smashes (`vbi→Ubi`) and breaks
  numerals (memo row 8).
- **`aer*` / `aether*`** follow the general `ae` policy and are ligatured; no
  exception is in the set yet (memo row 12 — pending corpus QA).
- Punctuation cleanup is **out of scope** for this version (memo row 21).

### Development

```console
$ python3 -m venv .venv && .venv/bin/pip install pytest
$ .venv/bin/python -m pytest tests/ -q     # 63 tests
```

`tests/test_orthography_normalize.py` is the ported engine suite;
`tests/test_latinj_cli.py` is the v2 CLI + regression battery;
`tests/test_ruleset_examples.py` replays every example pair in the formal
rule-set through the CLI (generated from the YAML spec). Add new substitutions
by editing `orthography/rules.json` and re-running the tests — never hand-edit
the engine. Details: `orthography/README.md`.
