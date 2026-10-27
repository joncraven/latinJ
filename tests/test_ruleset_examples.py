"""Formal rule-set acceptance battery (kanban t_edf1b598).

Every example pair cited in docs/orthography-ruleset.formal.yaml (the t_d270dcf7
approved rule set) is run through the REAL CLI (stdin -> stdout, default entity
style) and must match, idempotently.  Dropped-rule guards (Perl bugs that must
stay dead) and the composite acceptance sentence are included.

Generated mechanically from the YAML by the port run; do not hand-edit pairs —
change the rule set document, then regenerate.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "latinj.py"


def run_cli(text: str) -> str:
    proc = subprocess.run(
        [sys.executable, str(CLI)],
        input=text, capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.rstrip("\n")


def check(src: str, want: str) -> None:
    got = run_cli(src)
    assert got == want, f"{src!r} -> {got!r}, expected {want!r}"
    assert run_cli(got) == got, f"second pass changed {got!r}"


def _run(pairs):
    for src, want in pairs:
        check(src, want)


# --- adopted rules (docs/orthography-ruleset.formal.yaml: adopted_rules) ---

def test_test_adopted_rule_1_nfc_normalisation():
    _run([
    ('māter', 'mater'),
    ('Māter', 'Mater'),
    ('ma', 'ma'),
    ])

def test_test_adopted_rule_2_protect_exception_word_starts_hebrew_bib():
    _run([
    ('Israel', 'Israel'),
    ('Israelis et Michaelis', 'Israelis et Michaelis'),
    ('Praesidium et Israel', 'Pr&aelig;sidium et Israel'),
    ('Daniel et Ismael et Raphael', 'Daniel et Ismael et Raphael'),
    ('Isaiah', 'Isaiah'),
    ])

def test_test_adopted_rule_3_strip_combining_macron_and_breve():
    _run([
    ('Māter rēgina āmo', 'Mater regina amo'),
    ('consulto', 'consulto'),
    ])

def test_test_adopted_rule_4_character_substitution_map_char_map_30():
    _run([
    ('Cæsar', 'C&aelig;sar'),
    ('coelum poena', 'coelum poena'),
    ('lœ', 'loe'),
    ('Māter rēgina āmo', 'Mater regina amo'),
    ('ędes', '&aelig;des'),
    ('coepti', 'coepti'),
    ('consulto', 'consulto'),
    ])

def test_test_adopted_rule_5_ae_digraph_aelig_aelig_literal_re():
    _run([
    ('praesidium caedem', 'pr&aelig;sidium c&aelig;dem'),
    ('Aequor', '&AElig;quor'),
    ('pr&aelig;sidium', 'pr&aelig;sidium'),
    ('Israel', 'Israel'),
    ])

def test_test_adopted_rule_6_consonantal_i_j_word_regex_case_inse():
    _run([
    ('iam etiam iamque', 'jam etiam jamque'),
    ('iussu iactabit coniurationem eius huius cuius maior', 'jussu jactabit conjurationem ejus hujus cujus major'),
    ('Iam Iuppiter Iovi Ianuarias', 'Jam Juppiter Jovi Januarias'),
    ('iudicio iudicat iudicium iudicarit iudicarem iucundus', 'judicio judicat judicium judicarit judicarem jucundus'),
    ('maius peius Troia ieiunium iusiurandum Ihesus', 'majus pejus Troja jejunium jusiurandum Jesus'),
    ('traiectum', 'trajectum'),
    ('conicio', 'conjicio'),
    ('adic adicit', 'adjic adjicit'),
    ('abjic abjicat', 'abjic abjicat'),
    ('exieris', 'exieris'),
    ('init', 'init'),
    ('adeo', 'adeo'),
    ('perit', 'perit'),
    ('circumit', 'circumit'),
    ('etiam', 'etiam'),
    ('ivi', 'ivi'),
    ('iens', 'iens'),
    ('interior', 'interior'),
    ('interius', 'interius'),
    ])

def test_test_adopted_rule_7_proper_name_and_biblical_consonantal_i():
    _run([
    ('Iuppiter Iovi Iohann Ihesus Ioseph Pompeius', 'Juppiter Jovi Johann Jesus Joseph Pompejus'),
    ('Troia Traianus', 'Troja Trajanus'),
    ('Israel', 'Israel'),
    ])

def test_test_adopted_rule_8_conditional_addenda_qa_gated_not_yet_in():
    _run([
    ('eiusmodi huiusmodi', 'ejusmodi hujusmodi'),
    ('Gabriel', 'Gabriel'),
    ('aer', '&aelig;r'),
    ('regnaque', 'regnaque'),
    ('Gabrielis', 'Gabrielis'),
    ])

# --- dropped-rule guards: Python-side behaviour that must hold ---
def test_test_dropped_rule_guards():
    _run([
    ('vbi', 'vbi'),
    ('Anno IV', 'Anno IV'),
    ('MVII', 'MVII'),
    ('CVIII', 'CVIII'),
    ('voltus', 'voltus'),
    ('aduenio', 'aduenio'),
    ('servum', 'servum'),
    ('ivi', 'ivi'),
    ('interius', 'interius'),
    ('Nammei', 'Nammei'),
    ('<a href="http://www.thelatinlibrary.com/cicero/praesidium.html">praesidium</a>', '<a href="http://www.thelatinlibrary.com/cicero/praesidium.html">pr&aelig;sidium</a>'),
    ])

# --- composite acceptance sentence (adopted + guard in one pass) ---
def test_test_composite_acceptance_sentence():
    check(
        'Iam David, fili Israel, quis est maior omnibus? Cuius ieiunium et iusiurandum, traiecit MVII.',
        'Jam David, fili Israel, quis est major omnibus? Cujus jejunium et jusiurandum, trajecit MVII.',
    )
