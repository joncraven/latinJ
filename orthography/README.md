# Latin HTML orthography pipeline

Rewrites a raw Latin HTML page to the **latin.craven.fr** corpus standard
(the Latin.war / The Latin Library convention used under
`library-site/resources/assets/`).

This is **not** the TTS Layer 1 normaliser (`latin_audio.layers.layer1_text`):
that path lowercases, strips ligatures, and unifies u/v for speech. This
pipeline is for **reading-site HTML**.

## Site standard (discovered from the 92-page corpus)

| Feature | Policy |
|---|---|
| `ae` diphthong | `&aelig;` / `&AElig;` (never spelled `ae`, never raw `æ`) |
| `oe` diphthong | spelled `oe` (`œ` expands; do **not** emit `&oelig;`) |
| consonantal *i* | written `j` (`jam`, `ejus`, `hujus`, `jussu`, `conjurationem`) |
| vowel length | macrons and breves **stripped** (corpus has none) |
| `u` / `v` | left as in the source (corpus is mixed: `voltus` and `vultus`) |
| HTML | tags, attributes, `<script>`, `<style>` untouched |

The live corpus lives in the nested repo
`/Volumes/CRAVEN/jon/Projects/latin-audiobooks/library-site/resources/assets/`
(not a `/corpus/` folder). Gold samples for this pipeline are under
`corpus/` in this tree so the card's acceptance path exists.

## Usage

```
python3 scripts/normalize_orthography.py INPUT.html OUTPUT.html
python3 scripts/normalize_orthography.py INPUT.html OUTPUT.html \
    --rules orthography/rules.json \
    --log substitutions.jsonl
```

Every substitution is one JSON line in the log (`rule_id`, `match`,
`replacement`, `index`). Default log path is `<output>.log.jsonl`.

## Adding rules without code changes

Edit `orthography/rules.json`:

- `exceptions` — stem prefixes whose `ae` must not ligature (`Israel`, `Israelis`, …)
- `char_map` / `strip_combining` — 1:1 (or 1:n) character rewrites
- `regex` — literal/regex substitutions on text nodes
- `word_regex` — case-insensitive, case-preserving word/stem rewrites (`iam`/`Iam` → `jam`/`Jam`)

Then re-run the tests:

```
python -m pytest tests/test_orthography_normalize.py -v
```

## Fixture

`tests/fixtures/orthography/tll_cat1_raw.html` is a TLL-shaped Catiline I
opening with spelled `ae`, `iam`/`iussu`/`coniur-`, a macron, `œ`, and `ę`.
`tll_cat1_expected.html` is the same text after the site standard.
`corpus/cicero/cat1.sample.html` is an excerpt of the live corpus page
and must be a no-op (idempotent) under the pipeline.
