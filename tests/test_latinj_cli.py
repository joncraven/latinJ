"""latinj v2 CLI tests (kanban t_6e9130f8).

Covers the three things the v2 port owes the old `perl clean.pl` workflow:
  1. raw-in/raw-out shape (stdin->stdout, files, -i in place) — no fixed/ dir,
     no forced .html rename, no leading-space hack;
  2. the decision-memo regression battery — every reproduced Perl bug must be
     wrong no more, and every previously-correct local rule must hold;
  3. --style unicode|entity (the memo's open decision: latinJ wants readable
     Latin, the site standard wants entities; the flag serves both).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from latinj import correct  # noqa: E402
from orthography.normalize import load_rules  # noqa: E402

CLI = ROOT / "latinj.py"
RULES = ROOT / "orthography" / "rules.json"


def run_cli(args, stdin=None):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


class TestCliWorkflow:
    def test_stdin_to_stdout(self):
        proc = run_cli([], stdin="iam et eius et praesidium\n")
        assert proc.returncode == 0, proc.stderr
        assert proc.stdout == "jam et ejus et pr&aelig;sidium\n"

    def test_stdin_unicode_style(self):
        proc = run_cli(["--style", "unicode"], stdin="Cæsar praesidium\n")
        assert proc.stdout == "Cæsar præsidium\n"

    def test_file_to_stdout(self, tmp_path):
        src = tmp_path / "input.txt"
        src.write_text("iam maior\n", encoding="utf-8")
        proc = run_cli([str(src)])
        assert proc.returncode == 0, proc.stderr
        assert proc.stdout == "jam major\n"

    def test_in_place_rewrites_file(self, tmp_path):
        src = tmp_path / "input.html"
        src.write_text("<p>iam coniurationem</p>\n", encoding="utf-8")
        proc = run_cli(["-i", str(src)])
        assert proc.returncode == 0, proc.stderr
        assert src.read_text(encoding="utf-8") == "<p>jam conjurationem</p>\n"

    def test_no_fixed_dir_required(self, tmp_path):
        # The old perl tool died unless ./fixed existed in cwd. Prove we don't.
        src = tmp_path / "a.html"
        src.write_text("iam", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(CLI), str(src)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0
        assert proc.stdout == "jam"
        assert not (tmp_path / "fixed").exists()

    def test_log_jsonl(self, tmp_path):
        log = tmp_path / "audit.jsonl"
        proc = run_cli(["--log", str(log)], stdin="iam\n")
        assert proc.returncode == 0, proc.stderr
        rows = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
        assert rows[0]["rule_id"] == "iam"
        assert rows[0]["match"] == "iam" and rows[0]["replacement"] == "jam"

    def test_missing_file_errors(self, tmp_path):
        proc = run_cli([str(tmp_path / "nope.txt")])
        assert proc.returncode != 0


class TestMemoRegressionBattery:
    """Every row the memo marked GO must hold; every Perl bug must be gone."""

    def setup_method(self):
        self.rules = load_rules(RULES)

    def one(self, s, style="entity"):
        return correct(s, self.rules, style=style)

    # --- Perl headline bugs, reproduced from the assessment ---
    def test_ieiunium_not_jeiunium(self):
        assert self.one("ieiunium") == "jejunium"

    def test_iusiurandum_medial_iu(self):
        assert self.one("iusiurandum") == "jusiurandum"
        assert self.one("Iusiurandum") == "Jusiurandum"

    def test_no_case_smash_vbi(self):
        assert self.one("vbi eras") == "vbi eras"  # no V->U pass at all

    def test_numerals_safe_at_eol(self):
        assert self.one("Anno IV") == "Anno IV"
        assert self.one("MVII et CIII") == "MVII et CIII"
        assert self.one("saeculum CVIII") == "s&aelig;culum CVIII"  # ae rule ok; numerals intact

    def test_israel_at_eol_not_ligatured(self):
        assert self.one("Israel.") == "Israel."
        assert self.one("Michael") == "Michael"

    def test_no_leading_space_hack(self):
        assert self.one("iam") == "jam"  # no injected leading space

    # --- Previously-correct rules must not regress ---
    def test_open_j_stems(self):
        assert self.one("iussus iuxta iure iustis") == "jussus juxta jure justis"

    def test_etiam_immunity(self):
        assert self.one("etiam") == "etiam"

    def test_eius_cuius_huius(self):
        assert self.one("eius cuius huius maior peius") == "ejus cujus hujus major pejus"

    def test_ire_family_immunity(self):
        # Perl needed explicit undo rules here; we must simply never convert.
        for w in ("ivi", "iens", "it", "eunt", "adeo", "interior", "interius"):
            assert self.one(w) == w

    # --- v1.2 backfill: prefix compounds, QA-validated forms only ---
    def test_ad_compounds(self):
        assert self.one("adiutor") == "adjutor"
        assert self.one("adiutorem") == "adjutorem"
        assert self.one("adiuvamus") == "adjuvamus"
        assert self.one("adicit") == "adjicit"
        assert self.one("adiectus") == "adjectus"  # v1.1 adiec rule

    def test_in_compounds(self):
        assert self.one("inicit") == "injicit"
        assert self.one("iniecit") == "injecit"
        assert self.one("iniuria") == "injuria"  # v1.1 iniur rule

    def test_con_compounds(self):
        assert self.one("conicit") == "conjicit"
        assert self.one("coniecit") == "conjecit"  # v1.1 coniec rule
        assert self.one("coniuratio") == "conjuratio"  # v1.1 coniur rule

    def test_ab_and_ob_compounds(self):
        assert self.one("abicit") == "abjicit"
        assert self.one("abiecit") == "abjecit"
        assert self.one("obicere") == "objicere"
        assert self.one("obiecit") == "objecit"

    def test_re_and_tra_compounds(self):
        assert self.one("reicit") == "rejicit"
        assert self.one("reiecit") == "rejecit"
        assert self.one("traiectum") == "trajectum"
        assert self.one("traiecit") == "trajecit"
        assert self.one("traicit") == "trajicit"
        assert self.one("traicio") == "trajicio"  # trans+iacio compound

    def test_false_positive_guards(self):
        # Forms the memo warned a generalised prefix regex would corrupt.
        # No j is ever invented; ae digraph policy (pr&aelig;est) is separate.
        assert self.one("praeest") == "pr&aelig;est"
        assert self.one("reius") == "reius"
        assert self.one("init") == "init"
        assert self.one("adeo") == "adeo"
        assert self.one("perit") == "perit"
        assert self.one("circumit") == "circumit"  # not QA-validated; leave spelled
        assert self.one("abiectus") == "abjectus"  # ab+iect compound, QA-validated

    # --- CLI-level: HTML awareness preserved in raw mode ---
    def test_html_untouched_around_tags(self):
        out = self.one('<a href="praesidium.html">iam</a>')
        assert 'href="praesidium.html"' in out
        assert ">jam<" in out

    def test_plain_text_has_no_html(self):
        out = self.one("vbi iam")
        assert "<" not in out
        assert out == "vbi jam"

    # --- Style switch resolves the open decision ---
    def test_unicode_style(self):
        assert self.one("Cæsar", style="unicode") == "Cæsar"
        assert self.one("praesidium", style="unicode") == "præsidium"
        assert self.one("Aeneas", style="unicode") == "Æneas"

    def test_entity_style_is_default_site_standard(self):
        assert self.one("praesidium") == "pr&aelig;sidium"

    def test_unicode_style_idempotent(self):
        once = self.one("praesidium", style="unicode")
        assert self.one(once, style="unicode") == once

    # --- Whole-rule-set invariant: correction is stable under repetition ---
    def test_double_correction_stable(self):
        once = self.one("iam praesidium ieiunium Israel MVII coniurationem inicit")
        assert self.one(once) == once
