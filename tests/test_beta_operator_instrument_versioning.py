"""Version-binding contract for the synthetic operator instrument.

PREPATCH tests are intentionally genuine behavioral falsifiers on the
published v1 CLI. These are *not* human responses or a randomized trial.
Additional v2 contract tests use independently CSPRNG-assigned local forms.
All written payloads are anonymous synthetic harness data in tmp_path.
"""
from __future__ import annotations
import os

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "beta_science_operator_protocol.py"
V1_SCHEMA = "pfl.beta_science_operator_observations.v1"
MISSING = "NOT_OBSERVED"


def run_cli(*arguments: str | Path) -> tuple[int, dict, str]:
    completed = subprocess.run(
        [sys.executable, "-B", str(CLI), *map(str, arguments)],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=12,
        check=False,
    )
    assert completed.stderr == "", "No absolute paths or tracebacks on stderr"
    assert completed.stdout.count("\n") == 1
    assert len(completed.stdout) < 35_000
    payload = json.loads(completed.stdout)
    assert isinstance(payload, dict)
    return completed.returncode, payload, completed.stdout


def write_fixture(tmp_path: Path, document: dict, name: str) -> Path:
    path = tmp_path / name
    path.write_bytes(
        (json.dumps(document, ensure_ascii=True, sort_keys=True,
                    separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
    )
    return path


def synthetic_v1_nonempty() -> dict:
    blank_rc, blank, _ = run_cli("--blank-session")
    rubric_rc, rubric, _ = run_cli("--template")
    assert blank_rc == rubric_rc == 0
    assert blank["schema"] == V1_SCHEMA
    assert len(blank["observations"]) == 12
    answer = rubric["tasks"][0]["correct_answer_code"]
    blank["observations"][0].update(
        technical="TECH_COMPLETED", scientific=answer, usability="UX_CLEAR")
    return blank


# PREPATCH baseline: v1 stays supported, but it is a globally fixed
# unbound form. These factual tests must PASS; do not retrospectively call v1
# itself an invalid submission or pretend a new CLI already existed.

def test_prepatch_legacy_v1_fixed_public_answer_key_is_repeatably_inferable():
    rc1, sheet1, _ = run_cli("--participant-sheet")
    rc2, sheet2, _ = run_cli("--participant-sheet")
    rubric_rc, rubric, _ = run_cli("--template")
    assert rc1 == rc2 == rubric_rc == 0
    assert sheet1 == sheet2
    assert set(sheet1) == {"schema", "tasks"}
    assert len(sheet1["tasks"]) == len(rubric["tasks"]) == 12
    exposed = {}
    for public, operator in zip(sheet1["tasks"], rubric["tasks"], strict=True):
        exposed[public["task_id"]] = next(
            letter for letter, code in
            operator["participant_option_to_scientific_code"].items()
            if code == operator["correct_answer_code"])
    assert len(exposed) == 12 and set(exposed.values()) == {"A", "B"}
    assert "form_id" not in sheet1
    assert "instrument_version" not in sheet1


def test_prepatch_legacy_v1_unbound_scientific_code_is_still_accepted(tmp_path):
    source = write_fixture(tmp_path, synthetic_v1_nonempty(),
                           "synthetic_legacy_without_form_id.json")
    rc, payload, raw = run_cli("--evaluate", source)
    assert rc == 0 and payload["status"] == "OPERATOR_EVALUATION_COMPLETE"
    assert payload["rollup"]["scientific"]["SCI_CORRECT"] == 1
    assert payload["participant_count"] is None
    assert payload["operator_instrument_sha256"]
    assert str(source) not in raw


def test_prepatch_red_legacy_v1_scoring_receipt_must_disclose_unbound_status(
    tmp_path: Path,
):
    """Real methodological receipt gap, NOT a demand to refuse historic v1."""
    source = write_fixture(tmp_path, synthetic_v1_nonempty(),
                           "synthetic_legacy_receipt_no_binding.json")
    rc, payload, raw = run_cli("--evaluate", source)
    assert rc == 0 and payload["status"] == "OPERATOR_EVALUATION_COMPLETE"
    assert payload["participant_count"] is None
    assert str(source) not in raw
    # Existing output fingerprints the *current* rubric, although the
    # v1 observations did not bind themselves to it. The output must not
    # imply a form-specific historical proof; it must disclose this caveat.
    assert payload.get("instrument_binding") == "LEGACY_UNBOUND"


# OPT-IN V2 contract. These are forward-looking requirements for the separately
# owned production implementation, not PREPATCH regressions or human evidence.
# Two form generations can select the same 6/6 permutation by chance. Tests
# must not pretend otherwise or assert fabricated participant randomization.

def _prepared_v2(tmp_path: Path, stem: str) -> tuple[dict, dict, str, Path, Path, Path]:
    private = tmp_path / ("private rubric " + stem)
    public = tmp_path / ("public participant " + stem)
    # The product now refuses private artifacts in inherited/public ACL
    # directories. Python >=3.13 on Windows creates a protected 0700 DACL.
    os.mkdir(private, mode=0o700)
    public.mkdir()
    session = private / ("sesion " + stem + ".json")
    rubric = private / ("rubrica " + stem + ".json")
    handout = public / ("ficha " + stem + ".html")
    for target in (session, handout, rubric):
        assert not target.exists()
        assert not target.is_relative_to(ROOT)
    code, receipt, raw = run_cli("--prepare-form", session, handout, rubric)
    assert code == 0, receipt
    assert receipt["status"].startswith("OPERATOR_")
    assert receipt.get("participants_observed") is False
    assert receipt.get("participant_count") is None
    for target in (session, rubric, handout):
        assert target.is_file()
        assert str(target) not in raw
        assert target.name not in raw
    assert "correct_answer_code" not in raw
    assert "participant_id" not in receipt
    for content in (session.read_bytes(), rubric.read_bytes(), handout.read_bytes()):
        assert content
        assert not content.startswith((b"\xff\xfe", b"\xfe\xff", b"\xef\xbb\xbf"))
        assert b"\x00" not in content
        assert content.decode("utf-8")
    body = json.loads(session.read_text(encoding="utf-8"))
    key = json.loads(rubric.read_text(encoding="utf-8"))
    html = handout.read_text(encoding="utf-8")
    return body, key, html, session, handout, rubric


def _rubric_forms(key: dict) -> tuple[dict[str, str], dict[str, dict]]:
    """Operator mapping only. No right answers may appear on public handouts."""
    assert key["schema"] == "pfl.beta_science_operator_template.v2"
    rows = key["tasks"]
    assert len(rows) == 12
    code, legacy_rubric, _ = run_cli("--template")
    assert code == 0
    scientific_correct = {
        item["task_id"]: item["correct_answer_code"]
        for item in legacy_rubric["tasks"]
    }
    choices: dict[str, str] = {}
    by_id: dict[str, dict] = {}
    for row in rows:
        tid = row["task_id"]
        assert tid not in by_id
        by_id[tid] = row
        mapping = row["participant_option_to_scientific_code"]
        assert set(mapping) == {"A", "B"}
        assert all(isinstance(code, str) and code.startswith("SCI_" + tid + "_")
                   for code in mapping.values())
        assert len(set(mapping.values())) == 2
        assert row["correct_answer_code"] in {"A", "B"}
        assert mapping[row["correct_answer_code"]] == scientific_correct[tid]
        choices[tid] = row["correct_answer_code"]
    return choices, by_id


def test_v2_prepare_two_independent_operator_assigned_form_bindings(tmp_path: Path):
    first = _prepared_v2(tmp_path, "001")
    second = _prepared_v2(tmp_path, "002")
    seen_ids = set()
    for session, rubric, html, source_path, public_path, key_path in (first, second):
        assert session["schema"] == "pfl.beta_science_operator_observations.v2"
        assert rubric["schema"] == "pfl.beta_science_operator_template.v2"
        assert session["form_id"] == rubric["form_id"]
        import re
        assert re.fullmatch(r"[0-9a-f]{32}", session["form_id"])
        seen_ids.add(session["form_id"])
        handout_sha = hashlib.sha256(public_path.read_bytes()).hexdigest()
        assert session["handout_sha256"] == handout_sha
        assert rubric["handout_sha256"] == handout_sha
        assert len(session["observations"]) == 12
        assert {entry["task_id"] for entry in session["observations"]} == {
            f"OP{index:02d}" for index in range(1, 13)
        }
        assert all(
            set(entry) == {"task_id", "technical", "scientific", "usability"}
            and all(entry[field] == MISSING for field in (
                "technical", "scientific", "usability"))
            for entry in session["observations"]
        )
        correct_labels, by_id = _rubric_forms(rubric)
        assert set(by_id) == set(correct_labels)
        assert list(correct_labels.values()).count("A") == 6
        assert list(correct_labels.values()).count("B") == 6
        assert "<html" in html.lower() and "</html>" in html.lower()
        for tid in correct_labels:
            assert tid in html
        # Public handout can display the correct *meaning*, but must never
        # disclose operator-only answer symbols, maps or scoring indicators.
        assert "SCI_OP" not in html
        assert "correct_answer_code" not in html
        assert "participant_option_to_scientific_code" not in html
        assert "scientific_explanation" not in html
        assert source_path.parent != public_path.parent
        assert key_path.parent != public_path.parent
    assert len(seen_ids) == 2, "Independent 128-bit form IDs must not be reused"
    # Do not assert the two 6/6 permutations differ: identical draws are valid.


def test_v2_evaluate_form_uses_rubric_scoped_ab_codes_and_closes_without_people(
    tmp_path: Path,
):
    session, rubric, _, input_path, handout, rubric_path = _prepared_v2(tmp_path, "eval")
    correct, _ = _rubric_forms(rubric)
    rows = {item["task_id"]: item for item in session["observations"]}
    rows["OP01"].update(
        technical="TECH_COMPLETED", scientific=correct["OP01"],
        usability="UX_FRICTION")
    rows["OP03"].update(
        technical="TECH_COMPLETED",
        scientific="B" if correct["OP03"] == "A" else "A",
        usability="UX_CLEAR")
    rows["OP09"].update(
        technical="TECH_BLOCKED", scientific=MISSING, usability="UX_BLOCKED")
    input_path.write_bytes((json.dumps(
        session, ensure_ascii=True, sort_keys=True,
        separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8"))
    before = input_path.read_bytes()
    output = input_path.parent / "synthetic_v2_scored_outcome.json"
    assert not output.exists()
    rc, receipt, raw = run_cli("--evaluate-form", input_path, rubric_path, output)
    assert rc == 0, receipt
    assert receipt["status"].startswith("OPERATOR_")
    assert receipt.get("participant_count") is None
    for private in (input_path, rubric_path, output, handout):
        assert str(private) not in raw and private.name not in raw
    assert output.is_file()
    raw_output = output.read_bytes()
    assert raw_output.startswith(b"{") and b"\x00" not in raw_output
    assert not raw_output.startswith((b"\xff\xfe", b"\xfe\xff", b"\xef\xbb\xbf"))
    result = json.loads(raw_output.decode("utf-8"))
    assert result["form_reference"] == session["form_id"][:12]
    assert result["handout_sha256"] == session["handout_sha256"]
    assert result["form_binding"] == "MATCHED_V2_FORM_AND_RUBRIC"
    assert result.get("instrument_binding") != "LEGACY_UNBOUND", (
        "Versioned v2 receipt must not also claim the legacy rubric is unbound"
    )
    assert result["participant_count"] is None
    assert result["gate_eligibility"] == "OPERATOR_NOT_ASSESSED"
    assert result["R5"] == "STOP_R5"
    assert result["tasks_with_any_coded_observation"] == 3
    assert result["rollup"]["technical"]["TECH_COMPLETED"] == 2
    assert result["rollup"]["technical"]["TECH_BLOCKED"] == 1
    assert result["rollup"]["scientific"]["SCI_CORRECT"] == 1
    assert result["rollup"]["scientific"]["SCI_INCORRECT"] == 1
    assert result["rollup"]["scientific"][MISSING] == 10
    assert result["operator_instrument_sha256"] == hashlib.sha256(
        rubric_path.read_bytes()).hexdigest()
    # The output is a classification, not a transcript or human response.
    assert all(row["scientific"] in ("SCI_CORRECT", "SCI_INCORRECT", MISSING)
               for row in result["tasks"])
    assert "participant_id" not in result
    assert input_path.read_bytes() == before
    # Exclusive output; a second attempt must not overwrite existing evidence.
    rc2, failure, _ = run_cli("--evaluate-form", input_path, rubric_path, output)
    assert rc2 != 0 and failure["status"] == "OPERATOR_REJECTED"
    assert output.read_bytes() == raw_output


@pytest.mark.parametrize("tamper", (
    "wrong_rubric",
    "form_id",
    "handout_sha",
    "version",
    "partial",
    "invalid_answer",
    "blocked_science",
    "additional_pii",
    "all_missing",
    "duplicate_task",
    "rubric_tamper",
    "utf16",
))
def test_v2_evaluate_form_rejects_unbound_invalid_without_writing(
    tmp_path: Path, tamper: str,
):
    session, rubric, _, input_path, _, rubric_path = _prepared_v2(
        tmp_path, "invalid_" + tamper)
    if tamper == "wrong_rubric":
        _, _, _, _, _, rubric_path = _prepared_v2(tmp_path, "other_" + tamper)
    elif tamper == "form_id":
        session["form_id"] = "0" * 32 if session["form_id"] != "0" * 32 else "1" * 32
    elif tamper == "handout_sha":
        session["handout_sha256"] = "0" * 64
    elif tamper == "version":
        session["schema"] = V1_SCHEMA
    elif tamper == "partial":
        session["observations"].pop()
    elif tamper == "invalid_answer":
        session["observations"][0].update(
            technical="TECH_COMPLETED", scientific="SCI_OP01_EQUIVALENT")
    elif tamper == "blocked_science":
        session["observations"][0].update(
            technical="TECH_BLOCKED", scientific="A")
    elif tamper == "additional_pii":
        session["observations"][0]["email"] = "CANARY_PRIVATE@example.invalid"
        session["observations"][0]["technical"] = "TECH_COMPLETED"
    elif tamper == "all_missing":
        pass
    elif tamper == "duplicate_task":
        session["observations"][0]["technical"] = "TECH_COMPLETED"
        session["observations"][1]["task_id"] = (
            session["observations"][0]["task_id"])
    elif tamper == "rubric_tamper":
        rubric["tasks"][0]["correct_answer_code"] = "SCI_OP01_EQUIVALENT"
        rubric_path.write_bytes(json.dumps(
            rubric, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True).encode("utf-8"))
    elif tamper == "utf16":
        session["observations"][0]["technical"] = "TECH_COMPLETED"
    else:
        raise AssertionError("Unknown test tamper variant")
    document_bytes = json.dumps(
        session, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    input_path.write_bytes(
        document_bytes.encode("utf-16")
        if tamper == "utf16" else document_bytes.encode("utf-8"))
    output = input_path.parent / "NO_REPORT_IS_PERMITTED.json"
    assert not output.exists()
    rc, failure, raw = run_cli("--evaluate-form", input_path, rubric_path, output)
    assert rc != 0
    assert failure["status"] == "OPERATOR_REJECTED"
    assert failure["error_code"].startswith("OPERATOR_")
    if tamper in ("wrong_rubric", "form_id", "handout_sha", "version"):
        assert failure["error_code"] == "OPERATOR_FORM_MISMATCH"
    if tamper == "rubric_tamper":
        assert failure["error_code"] == "OPERATOR_FORM_RUBRIC_INVALID"
    if tamper == "utf16":
        assert failure["error_code"] == "OPERATOR_JSON_INVALID"
    assert not output.exists()
    assert "CANARY_PRIVATE" not in raw
    for path in (input_path, rubric_path, output):
        assert str(path) not in raw and path.name not in raw


def test_v2_cannot_silently_accept_legacy_v1_or_v2_in_wrong_evaluator(
    tmp_path: Path,
):
    session, _, _, v2_path, _, rubric = _prepared_v2(tmp_path, "compat")
    rc, rejected, _ = run_cli("--evaluate", v2_path)
    assert rc != 0 and rejected["status"] == "OPERATOR_REJECTED"
    legacy = write_fixture(tmp_path, synthetic_v1_nonempty(),
                           "historical_v1_legacy.json")
    output = tmp_path / "INVALID_V1_FORM_EXPORT.json"
    rc, rejected, _ = run_cli("--evaluate-form", legacy, rubric, output)
    assert rc != 0
    assert rejected["status"] == "OPERATOR_REJECTED"
    assert rejected["error_code"] == "OPERATOR_FORM_MISMATCH"
    assert not output.exists()
    # Historic v1 is still a functional explicit legacy path, not destroyed.
    rc, accepted, _ = run_cli("--evaluate", legacy)
    assert rc == 0 and accepted["status"] == "OPERATOR_EVALUATION_COMPLETE"
    assert accepted["instrument_binding"] == "LEGACY_UNBOUND"
    assert accepted["participant_count"] is None



@pytest.mark.parametrize("destination_problem", (
    "same_parent_for_key",
    "existing_participant_output",
    "same_output_path",
    "inside_git_checkout",
))
def test_v2_prepare_form_rejects_unsafe_three_file_destinations_atomically(
    tmp_path: Path, destination_problem: str,
):
    private = tmp_path / "private rubric"
    public = tmp_path / "public handout"
    private.mkdir()
    public.mkdir()
    session = private / "synthetic coded v2.json"
    rubric = private / "private operator key v2.json"
    participant = public / "public form v2.html"
    existing_bytes = b"NEVER_OVERWRITE_PREEXISTING_FIXTURE"
    if destination_problem == "same_parent_for_key":
        participant = private / "participant same dir.html"
    elif destination_problem == "existing_participant_output":
        participant.write_bytes(existing_bytes)
    elif destination_problem == "same_output_path":
        rubric = session
    elif destination_problem == "inside_git_checkout":
        participant = ROOT / "__operator_form_must_not_create__.html"
        assert not participant.exists()
    else:
        raise AssertionError("unexpected destination problem")
    initial_private = set(private.iterdir())
    initial_public = set(public.iterdir())
    rc, rejected, raw = run_cli("--prepare-form", session, participant, rubric)
    assert rc != 0 and rejected["status"] == "OPERATOR_REJECTED"
    assert rejected["error_code"].startswith("OPERATOR_")
    assert rejected["participant_count"] is None
    assert not session.exists()
    if rubric != session:
        assert not rubric.exists()
    if destination_problem == "existing_participant_output":
        assert participant.read_bytes() == existing_bytes
    else:
        assert not participant.exists()
    assert set(private.iterdir()) == initial_private
    assert set(public.iterdir()) == initial_public
    for path in (session, participant, rubric):
        assert str(path) not in raw and path.name not in raw
    assert "correct_answer_code" not in raw


def test_prepatch_red_v2_coded_observations_must_not_share_participant_folder(
    tmp_path: Path,
):
    """A participant-readable folder must not receive private coded responses.

    This is a real privacy boundary in the three-artifact generator, not a
    new questionnaire, user identity or OS-ACL assertion.
    """
    public = tmp_path / "public participant"
    private = tmp_path / "private supervisor"
    public.mkdir()
    private.mkdir()
    session = public / "private-coded-observations-misplaced.json"
    handout = public / "participant-handout.html"
    rubric = private / "private-operator-rubric.json"
    rc, rejected, raw = run_cli("--prepare-form", session, handout, rubric)
    assert rc == 1
    assert rejected["status"] == "OPERATOR_REJECTED"
    assert rejected["error_code"] == "OPERATOR_FORM_KEY_NOT_SEPARATED"
    assert not session.exists() and not handout.exists() and not rubric.exists()
    assert not any(public.iterdir()) and not any(private.iterdir())
    for path in (session, handout, rubric):
        assert str(path) not in raw


def test_v2_evaluate_form_output_write_once_outside_git_and_no_ads(
    tmp_path: Path,
):
    session, key, _, source, _, rubric_path = _prepared_v2(
        tmp_path, "output_safety")
    correct, _ = _rubric_forms(key)
    session["observations"][0].update(
        technical="TECH_COMPLETED", scientific=correct["OP01"])
    source.write_bytes((json.dumps(session, sort_keys=True, separators=(",", ":"),
                                  ensure_ascii=True) + "\n").encode("utf-8"))
    original = source.read_bytes()
    occupied = source.parent / "existing scored v2.json"
    occupied.write_bytes(b"PRIVATE_SYNTHETIC_SENTINEL")
    repo = ROOT / "__operator_v2_export_must_never_create__.json"
    assert not repo.exists()
    cases = [occupied, source, repo, source.parent / "missing parent" / "report.json"]
    if sys.platform == "win32":
        anchor = source.parent / "stream anchor.txt"
        anchor.write_bytes(b"STREAM_ANCHOR_MUST_REMAIN")
        cases.append(Path(str(anchor) + ":scientific_result"))
    for destination in cases:
        rc, rejected, raw = run_cli(
            "--evaluate-form", source, rubric_path, destination)
        assert rc != 0
        assert rejected["status"] == "OPERATOR_REJECTED"
        assert rejected["error_code"].startswith("OPERATOR_")
        assert rejected["participant_count"] is None
        assert source.read_bytes() == original
        assert occupied.read_bytes() == b"PRIVATE_SYNTHETIC_SENTINEL"
        assert not repo.exists()
        assert not (source.parent / "missing parent").exists()
        if sys.platform == "win32":
            assert anchor.read_bytes() == b"STREAM_ANCHOR_MUST_REMAIN"
            assert not Path(str(anchor) + ":scientific_result").exists()
        for path in (source, rubric_path, destination):
            assert str(path) not in raw
            assert path.name not in raw
