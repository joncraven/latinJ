"""Orthography normalisation pipeline for Latin HTML (kanban t_9bc32c48).

Site standard is the latin.craven.fr / Latin.war corpus:
  * ae diphthong as &aelig; / &AElig; (never spelled ae, never raw æ)
  * oe stays spelled oe (œ expands; do not emit &oelig;)
  * consonantal i written j (jam, ejus, hujus, jussu) matching TLL
  * no vowel-length marks (macrons/breves stripped)
  * HTML tags and attributes are left untouched

Tests are written first; the module under test lives at
orthography/normalize.py and is driven by orthography/rules.json.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from orthography.normalize import (  # noqa: E402
    load_rules,
    normalize_file,
    normalize_html,
    normalize_text,
)

RULES = ROOT / "orthography" / "rules.json"
FIXTURES = ROOT / "tests" / "fixtures" / "orthography"
CORPUS = ROOT / "corpus"
CLI = ROOT / "scripts" / "normalize_orthography.py"


@pytest.fixture(scope="module")
def rules():
    return load_rules(RULES)


class TestAeLigature:
    def test_spelled_ae_becomes_entity(self, rules):
        out, log = normalize_text("praesidium caedem", rules)
        assert "pr&aelig;sidium" in out
        assert "c&aelig;dem" in out
        assert "ae" not in out.replace("&aelig;", "")
        assert any(e["rule_id"] == "ae_digraph_lower" for e in log)

    def test_unicode_ae_becomes_entity(self, rules):
        out, log = normalize_text("Cæsar", rules)
        assert out == "C&aelig;sar"
        assert any(e["match"] == "æ" for e in log)

    def test_titlecase_ae_becomes_AElig(self, rules):
        out, _ = normalize_text("Aeneas AEquor", rules)
        assert out.startswith("&AElig;neas")
        assert "&AElig;quor" in out or "&AElig;Quor" in out

    def test_israel_is_not_ligatured(self, rules):
        out, _ = normalize_text("Israel et Ismael et Raphael", rules)
        assert "Israel" in out
        assert "Ismael" in out
        assert "Raphael" in out
        assert "&aelig;" not in out.lower()

    def test_declined_hebrew_names_are_not_ligatured(self, rules):
        out, _ = normalize_text("Israelis et Michaelis", rules)
        assert out == "Israelis et Michaelis"

    def test_nfd_diaeresis_is_not_ligatured(self, rules):
        nfd = "a" + "e\u0308" + "r"
        out, _ = normalize_text(nfd, rules)
        assert out == "aër"
        assert "&aelig;" not in out


class TestOeAndMacrons:
    def test_oe_ligature_expands_not_entity(self, rules):
        out, log = normalize_text("cœlum pœna", rules)
        assert out == "coelum poena"
        assert "&oelig;" not in out.lower()
        assert any(e["rule_id"] == "ligature_oe_lower" for e in log)

    def test_macrons_and_breves_stripped(self, rules):
        out, log = normalize_text("Māter rēgīna ămō", rules)
        assert out == "Mater regina amo"
        assert any(e["rule_id"].startswith("length_") for e in log)

    def test_combining_macron_stripped(self, rules):
        out, _ = normalize_text("ma" + "\u0304" + "ter", rules)
        assert out == "mater"

    def test_e_caudata_becomes_aelig(self, rules):
        out, _ = normalize_text("ędes", rules)
        assert out == "&aelig;des"


class TestConsonantalJ:
    def test_iam_to_jam_but_etiam_untouched(self, rules):
        out, log = normalize_text("iam etiam iamque", rules)
        assert out == "jam etiam jamque"
        assert any(e["match"].lower().startswith("iam") for e in log)

    def test_iussu_iactabit_coniurationem(self, rules):
        out, _ = normalize_text("iussu iactabit coniurationem eius huius cuius maior", rules)
        assert out == "jussu jactabit conjurationem ejus hujus cujus major"

    def test_title_case_iam_and_iuppiter_preserve_case(self, rules):
        out, log = normalize_text("Iam Iuppiter Iovi Ianuarias", rules)
        assert out == "Jam Juppiter Jovi Januarias"
        assert any(e["match"] == "Iam" and e["replacement"] == "Jam" for e in log)
        assert any(e["match"] == "Iuppiter" for e in log)

    def test_iudic_family_and_iucund(self, rules):
        out, _ = normalize_text(
            "iudicio iudicat iudicium iudicarit iudicarem iucundus", rules
        )
        assert out == "judicio judicat judicium judicarit judicarem jucundus"

    def test_iacere_eiec_medial_cuius_iunx(self, rules):
        out, _ = normalize_text("iacere eiecerit eiectus alicuius iunxerunt", rules)
        assert out == "jacere ejecerit ejectus alicujus junxerunt"

    def test_exieris_is_not_rewritten(self, rules):
        out, log = normalize_text("exieris", rules)
        assert out == "exieris"
        assert not any("ieris" in e["match"].lower() for e in log)

    def test_assessment_stems_maius_troia_ieiun_iusiur(self, rules):
        out, _ = normalize_text("maius peius Troia ieiunium iusiurandum Ihesus", rules)
        assert out == "majus pejus Troja jejunium jusiurandum Jesus"


class TestHtmlAwareness:
    def test_does_not_rewrite_attributes(self, rules):
        html = '<a href="https://www.thelatinlibrary.com/cicero/praesidium.html">praesidium</a>'
        out, _ = normalize_html(html, rules)
        assert 'href="https://www.thelatinlibrary.com/cicero/praesidium.html"' in out
        assert ">pr&aelig;sidium<" in out

    def test_skips_script_and_style(self, rules):
        html = "<style>aelicious{}</style><script>var ae=1;</script><p>ae</p>"
        out, _ = normalize_html(html, rules)
        assert "<style>aelicious{}</style>" in out
        assert "<script>var ae=1;</script>" in out
        assert "<p>&aelig;</p>" in out


class TestFixtureAndCorpus:
    def test_known_text_before_after(self, rules):
        raw = (FIXTURES / "tll_cat1_raw.html").read_text(encoding="utf-8")
        expected = (FIXTURES / "tll_cat1_expected.html").read_text(encoding="utf-8")
        out, log = normalize_html(raw, rules)
        assert out == expected
        assert log, "every substitution must be logged"

    def test_corpus_sample_is_idempotent(self, rules):
        sample = (CORPUS / "cicero" / "cat1.sample.html").read_text(encoding="utf-8")
        out, log = normalize_html(sample, rules)
        assert out == sample
        assert log == []

    def test_custom_rule_without_code_change(self, tmp_path, rules):
        custom = json.loads(RULES.read_text(encoding="utf-8"))
        custom["word_regex"].append(
            {"id": "custom_foobar", "pattern": r"\bfoobar\b", "replace": "FOO"}
        )
        rules_path = tmp_path / "rules.json"
        rules_path.write_text(json.dumps(custom), encoding="utf-8")
        loaded = load_rules(rules_path)
        out, log = normalize_text("hello foobar", loaded)
        assert out == "hello FOO"
        assert any(e["rule_id"] == "custom_foobar" for e in log)


class TestCli:
    def test_cli_writes_output_and_jsonl_log(self, tmp_path):
        infile = FIXTURES / "tll_cat1_raw.html"
        outfile = tmp_path / "out.html"
        logpath = tmp_path / "subs.jsonl"
        proc = subprocess.run(
            [
                sys.executable,
                str(CLI),
                str(infile),
                str(outfile),
                "--rules",
                str(RULES),
                "--log",
                str(logpath),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stderr
        expected = (FIXTURES / "tll_cat1_expected.html").read_text(encoding="utf-8")
        assert outfile.read_text(encoding="utf-8") == expected
        lines = [json.loads(l) for l in logpath.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert lines
        assert {row["rule_id"] for row in lines}

    def test_normalize_file_helper(self, tmp_path, rules):
        src = FIXTURES / "tll_cat1_raw.html"
        dest = tmp_path / "copied.html"
        log = normalize_file(src, dest, rules)
        assert dest.read_text(encoding="utf-8") == (
            FIXTURES / "tll_cat1_expected.html"
        ).read_text(encoding="utf-8")
        assert isinstance(log, list) and log
