"""CLI contract tests: no participant is generated or inferred by this suite."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "beta_science_operator_protocol.py"
SCHEMA = "pfl.beta_science_operator_observations.v1"
MISSING = "NOT_OBSERVED"
MACHINE_IDS = {
    "S9_TEMPORAL_COMPARE", "S9_PAIR_EXPORT_OFFLINE",
    "S9_SINGLE_EXPORT_OFFLINE", "S9_FAMILY_SCOPE",
    "RESTART_DOCTOR_GUEST_LINK", "LAB_B0_B3", "LAB_S7_20",
    "LAB_S8_DESCRIPTORS", "LAB_S3_TEMPORAL", "S9_EIGHT_TABS",
}


def cli(*args: str) -> tuple[int, dict, str]:
    completed = subprocess.run(
        [sys.executable, "-B", str(SCRIPT), *args],
        cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=10, check=False,
    )
    assert completed.stderr == ""
    assert completed.stdout.count("\n") == 1
    data = json.loads(completed.stdout)
    assert type(data) is dict
    return completed.returncode, data, completed.stdout


def write_submission(tmp_path: Path, payload: dict, name="anonymous_fixture.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")
    return path


def response(task: dict, *, technical="TECH_COMPLETED",
             scientific: str | None = None, usability="UX_CLEAR") -> dict:
    return {
        "task_id": task["task_id"],
        "technical": technical,
        "scientific": scientific if scientific is not None
                      else task["correct_answer_code"],
        "usability": usability,
    }


def test_template_closed_12_tasks_machine_references_and_rubric():
    rc, result, stdout = cli("--template")
    assert rc == 0
    assert result["schema"] == "pfl.beta_science_operator_template.v1"
    assert result["status"] == "OPERATOR_TEMPLATE_ONLY"
    assert result["R5"] == "STOP_R5"
    assert result["task_count"] == 12
    tasks = result["tasks"]
    assert len(tasks) == len({task["task_id"] for task in tasks}) == 12
    assert [task["task_id"] for task in tasks] == [
        f"OP{index:02d}" for index in range(1, 13)]
    assert {m for t in tasks for m in t["technical_task_ids"]} == MACHINE_IDS
    assert {t["area"] for t in tasks} == {"OBSERVATORY", "LABORATORY", "OFFLINE"}
    assert all(t["technical_success_criterion"] and
               t["scientific_question"] and t["scientific_explanation"] and
               t["usability_observation_criterion"] for t in tasks)
    for item in tasks:
        options = item["scientific_options"]
        assert len(options) == 2
        assert len({option["code"] for option in options}) == 2
        assert item["correct_answer_code"] in [x["code"] for x in options]
        assert item["participant_option_to_scientific_code"] == {
            label: option["code"]
            for label, option in zip(("A", "B"), options, strict=True)}
        assert all(x["code"].startswith("SCI_" + item["task_id"] + "_")
                   for x in options)
    assert "NOT_OBSERVED" in result["input_contract"]["technical_codes"]
    assert "NOT_OBSERVED" in result["input_contract"]["usability_codes"]
    assert "participant" in result["instructions"].lower()
    assert "http://127.0.0.1:" not in stdout
    assert "cookie=" not in stdout


def test_prepatch_red_participant_sheet_opaque_balanced_ab_without_answer_leaks():
    rc, sheet, raw = cli("--participant-sheet")
    assert rc == 0
    _, rubric, _ = cli("--template")
    correct_position = {"A": 0, "B": 0}
    for handout, operator in zip(sheet["tasks"], rubric["tasks"], strict=True):
        choices = handout["scientific_options"]
        assert [choice["code"] for choice in choices] == ["A", "B"]
        assert all(set(choice) == {"code", "meaning"} for choice in choices)
        assert all(not choice["code"].startswith("SCI_") for choice in choices)
        operator_codes = [item["code"] for item in operator["scientific_options"]]
        position = operator_codes.index(operator["correct_answer_code"])
        correct_position["AB"[position]] += 1
        assert [c["meaning"] for c in choices] == [
            c["meaning"] for c in operator["scientific_options"]]
    assert correct_position == {"A": 6, "B": 6}
    assert "SCI_OP01_EQUIVALENT" not in raw
    assert "SCI_OP03_NONCAUSAL_BOUNDS" not in raw
    assert "correct_answer_code" not in raw


def test_prepatch_red_correct_position_not_deducible_from_task_parity():
    """An ABAB... answer sequence remains guessable after one known answer.

    This is a methodological falsifier, not a participant observation.
    """
    _, rubric, _ = cli("--template")
    _, sheet, _ = cli("--participant-sheet")
    positions = []
    for item, handed in zip(rubric["tasks"], sheet["tasks"], strict=True):
        assert [choice["code"] for choice in handed["scientific_options"]] == ["A", "B"]
        mapping = item["participant_option_to_scientific_code"]
        positions.append(next(label for label, code in mapping.items()
                              if code == item["correct_answer_code"]))
    assert positions.count("A") == positions.count("B") == 6
    assert positions != ["A" if i % 2 == 0 else "B" for i in range(12)]
    assert positions != ["B" if i % 2 == 0 else "A" for i in range(12)]


def test_prepatch_red_empty_observation_list_must_be_incomplete(tmp_path):
    path = write_submission(tmp_path, {"schema": SCHEMA, "observations": []})
    rc, result, raw = cli("--evaluate", str(path))
    assert rc == 1
    assert result == {
        "schema": "pfl.beta_science_operator_evaluation.v1",
        "status": "OPERATOR_REJECTED",
        "error_code": "OPERATOR_SESSION_INCOMPLETE",
        "participant_count": None,
    }
    assert str(path) not in raw


def test_participant_sheet_contains_only_questions_options_actions_and_ids():
    rc, result, stdout = cli("--participant-sheet")
    assert rc == 0
    assert set(result) == {"schema", "tasks"}
    assert result["schema"] == "pfl.beta_science_operator_participant_sheet.v1"
    assert len(result["tasks"]) == 12
    _, operator, _ = cli("--template")
    for sheet, rubric in zip(result["tasks"], operator["tasks"], strict=True):
        assert set(sheet) == {
            "task_id", "operator_action", "scientific_question",
            "scientific_options",
        }
        assert sheet["task_id"] == rubric["task_id"]
        assert sheet["operator_action"] == rubric["operator_action"]
        assert sheet["scientific_question"] == rubric["scientific_question"]
        assert [opt["code"] for opt in sheet["scientific_options"]] == ["A", "B"]
        assert [opt["meaning"] for opt in sheet["scientific_options"]] == [
            opt["meaning"] for opt in rubric["scientific_options"]]
        assert all(set(opt) == {"code", "meaning"} for opt in sheet["scientific_options"])
        assert rubric["correct_answer_code"] in {
            option["code"] for option in rubric["scientific_options"]}
        assert "correct_answer_code" not in sheet
        assert "scientific_explanation" not in sheet
        assert "participant_option_to_scientific_code" not in sheet
        assert "technical_task_ids" not in sheet
        assert "technical_success_criterion" not in sheet
        assert "usability_observation_criterion" not in sheet
    assert "correct_answer_code" not in stdout
    assert "scientific_explanation" not in stdout
    assert "participant_option_to_scientific_code" not in stdout
    assert "technical_task_ids" not in stdout
    assert "OPERATOR_NOT_ASSESSED" not in stdout


@pytest.mark.parametrize("technical", (
    "TECH_FAILED", "TECH_BLOCKED", "NOT_OBSERVED",
))
@pytest.mark.parametrize("answer_index", (0, 1))
def test_scientific_answer_requires_completed_technical_task(
    tmp_path, technical, answer_index,
):
    _, rubric, _ = cli("--template")
    item = rubric["tasks"][0]
    answer = item["scientific_options"][answer_index]["code"]
    path = write_submission(tmp_path, {
        "schema": SCHEMA,
        "observations": [response(
            item, technical=technical, scientific=answer,
        )],
    })
    rc, result, stdout = cli("--evaluate", str(path))
    assert rc == 1
    assert result == {
        "schema": "pfl.beta_science_operator_evaluation.v1",
        "status": "OPERATOR_REJECTED",
        "error_code": "OPERATOR_INPUT_INVALID",
        "participant_count": None,
    }
    assert str(path) not in stdout


def test_self_check_only_instrument_not_participation_or_live_beta():
    rc, result, stdout = cli("--self-check")
    assert rc == 0
    assert result == {
        "schema": "pfl.beta_science_operator_self_check.v1",
        "status": "OPERATOR_INSTRUMENT_VALID",
        "R5": "STOP_R5",
        "tasks_defined": 12,
        "participant_count": None,
        "participants_observed": False,
        "evaluation_executed": False,
        "live_beta_checked": False,
        "release_gate_changed": False,
    }
    assert "source_id" not in stdout


def test_anonymous_temp_fixture_evaluates_three_separate_classes(tmp_path):
    _, template, _ = cli("--template")
    tasks = template["tasks"]
    wrong = next(
        option["code"] for option in tasks[2]["scientific_options"]
        if option["code"] != tasks[2]["correct_answer_code"]
    )
    recorded = [
        response(tasks[0], technical="TECH_COMPLETED",
                 usability="UX_FRICTION"),
        response(tasks[2], technical="TECH_COMPLETED",
                 scientific=wrong, usability="UX_BLOCKED"),
        response(tasks[6], technical="TECH_FAILED",
                 scientific=MISSING, usability="UX_CLEAR"),
        response(tasks[8], technical="TECH_BLOCKED",
                 scientific=MISSING, usability=MISSING),
    ]
    recorded_ids = {row["task_id"] for row in recorded}
    full = recorded + [
        response(task, technical=MISSING, scientific=MISSING,
                 usability=MISSING)
        for task in tasks if task["task_id"] not in recorded_ids
    ]
    path = write_submission(tmp_path, {
        "schema": SCHEMA, "observations": full,
    })
    rc, result, stdout = cli("--evaluate", str(path))
    assert rc == 0
    assert result["status"] == "OPERATOR_EVALUATION_COMPLETE"
    assert result["schema"] == "pfl.beta_science_operator_evaluation.v1"
    assert result["R5"] == "STOP_R5"
    assert result["gate_eligibility"] == "OPERATOR_NOT_ASSESSED"
    assert result["participant_count"] is None
    assert result["participant_identity_collected"] is False
    assert result["tasks_defined"] == 12
    assert result["tasks_with_any_coded_observation"] == 4
    assert result["rollup"]["technical"] == {
        "TECH_COMPLETED": 2, "TECH_BLOCKED": 1,
        "TECH_FAILED": 1, MISSING: 8,
    }
    assert result["rollup"]["scientific"] == {
        "SCI_CORRECT": 1, "SCI_INCORRECT": 1, MISSING: 10,
    }
    assert result["rollup"]["usability"] == {
        "UX_CLEAR": 1, "UX_FRICTION": 1, "UX_BLOCKED": 1, MISSING: 9,
    }
    by_id = {t["task_id"]: t for t in result["tasks"]}
    assert by_id["OP01"] == {
        "task_id": "OP01", "technical": "TECH_COMPLETED",
        "scientific": "SCI_CORRECT", "usability": "UX_FRICTION",
    }
    assert by_id["OP03"] == {
        "task_id": "OP03", "technical": "TECH_COMPLETED",
        "scientific": "SCI_INCORRECT", "usability": "UX_BLOCKED",
    }
    assert by_id["OP07"]["technical"] == "TECH_FAILED"
    assert by_id["OP07"]["scientific"] == MISSING
    assert by_id["OP09"]["technical"] == "TECH_BLOCKED"
    assert by_id["OP09"]["scientific"] == MISSING
    assert by_id["OP12"]["scientific"] == MISSING
    assert str(path) not in stdout
    assert path.name not in stdout
    assert "anonymous_fixture" not in stdout
    assert all(t["scientific"] in ("SCI_CORRECT", "SCI_INCORRECT", MISSING)
               for t in result["tasks"])


@pytest.mark.parametrize("additional", [
    {"participant_name": "Test Person"},
    {"email": "person@example.invalid"},
    {"timestamp": "2026-11-03T12:00:00Z"},
    {"comment": "Operator narrative"},
    {"cookies": "session=CANARY"},
    {"credential": "password:CANARY"},
    {"ip": "127.0.0.1"},
    {"url": "http://127.0.0.1:32765/?session=CANARY"},
    {"path": "C:\\Users\\SECRET_CANARY\\records.json"},
])
def test_rejects_extra_fields_with_pii_and_never_echoes_them(tmp_path, additional):
    _, template, _ = cli("--template")
    item = response(template["tasks"][0])
    item.update(additional)
    path = write_submission(tmp_path, {
        "schema": SCHEMA, "observations": [item],
    })
    rc, result, stdout = cli("--evaluate", str(path))
    assert rc == 1
    assert result["status"] == "OPERATOR_REJECTED"
    assert result["error_code"] == "OPERATOR_INPUT_INVALID"
    assert "participant_count" in result and result["participant_count"] is None
    assert all(str(value) not in stdout for value in additional.values())
    assert str(path) not in stdout


@pytest.mark.parametrize("malformed", [
    {"schema": SCHEMA, "observations": [], "session": "SECRET_CANARY"},
    {"schema": SCHEMA, "observations": "not-a-list"},
    {"schema": "unknown.schema", "observations": []},
    {"observations": []},
    {"schema": SCHEMA, "observations": None},
])
def test_rejects_unknown_top_level_or_schema(tmp_path, malformed):
    path = write_submission(tmp_path, malformed)
    rc, result, stdout = cli("--evaluate", str(path))
    assert rc == 1 and result["status"] == "OPERATOR_REJECTED"
    assert result["error_code"] == "OPERATOR_SCHEMA_INVALID"
    assert str(path) not in stdout


@pytest.mark.parametrize("invalid", [
    {"task_id": "OP01", "technical": "TECH_COMPLETED",
     "scientific": "SCI_OP01_EQUIVALENT", "usability": "UX_OK"},
    {"task_id": "OP01", "technical": "TECH_COMPLETED",
     "scientific": "SCI_OP02_NONNEGATIVE_UNKNOWN", "usability": "UX_CLEAR"},
    {"task_id": "OP01", "technical": "TECH_COMPLETED",
     "scientific": "name@private.invalid", "usability": "UX_CLEAR"},
    {"task_id": "OP999", "technical": "TECH_COMPLETED",
     "scientific": "NOT_OBSERVED", "usability": "UX_CLEAR"},
    {"task_id": "OP01", "technical": True,
     "scientific": "NOT_OBSERVED", "usability": "UX_CLEAR"},
    {"task_id": "OP01", "technical": "TECH_COMPLETED",
     "scientific": "NOT_OBSERVED", "usability": "UX_CLEAR", "free_text": "CANARY"},
])
def test_rejects_unapproved_codes_and_types(tmp_path, invalid):
    path = write_submission(tmp_path, {
        "schema": SCHEMA, "observations": [invalid],
    })
    rc, result, stdout = cli("--evaluate", str(path))
    assert rc == 1
    assert result["error_code"] == "OPERATOR_INPUT_INVALID"
    assert str(path) not in stdout and "CANARY" not in stdout


def test_rejects_repeated_tasks_and_too_many_entries(tmp_path):
    _, template, _ = cli("--template")
    item = response(template["tasks"][0])
    for rows in ([item, item], [item] * 13):
        path = write_submission(tmp_path, {"schema": SCHEMA, "observations": rows})
        rc, result, _ = cli("--evaluate", str(path))
        assert rc == 1 and result["error_code"] == "OPERATOR_INPUT_INVALID"


@pytest.mark.parametrize("raw", [
    b'{"schema":"A","schema":"B","observations":[]}',
    b'{"schema":"pfl.beta_science_operator_observations.v1","observations":[{"task_id":"OP01","task_id":"OP02"}]}',
    b'{"schema":"pfl.beta_science_operator_observations.v1","observations":NaN}',
    b'{"schema":"pfl.beta_science_operator_observations.v1","observations":',
    b'\xff\xfe',
    b'{' + b'a' * 17000,
])
def test_rejects_duplicate_json_nonfinite_invalid_utf8_and_oversize(tmp_path, raw):
    path = tmp_path / "CANARY_raw_input.json"
    path.write_bytes(raw)
    rc, result, stdout = cli("--evaluate", str(path))
    assert rc == 1
    assert result["status"] == "OPERATOR_REJECTED"
    assert result["error_code"] in ("OPERATOR_JSON_INVALID", "OPERATOR_FILE_TOO_LARGE")
    assert "CANARY" not in stdout and str(path) not in stdout


def test_invalid_path_or_arguments_fail_closed_without_exposing_filename(tmp_path):
    missing = tmp_path / "secret-person-passport-canary.json"
    for args in (("--evaluate", str(missing)), ("--unknown",),
                 ("--template", "--self-check"), ()):
        rc, result, stdout = cli(*args)
        assert rc == 1 and result["status"] == "OPERATOR_REJECTED"
        assert result["error_code"].startswith("OPERATOR_")
        assert "verified_guest_url" not in stdout
        assert str(missing) not in stdout and missing.name not in stdout


def test_blank_session_exact_schema_and_zero_participant_claims(tmp_path):
    rc, blank, stdout = cli("--blank-session")
    assert rc == 0
    assert set(blank) == {"schema", "observations"}
    assert blank["schema"] == SCHEMA
    assert len(blank["observations"]) == 12
    assert [item["task_id"] for item in blank["observations"]] == [
        f"OP{index:02d}" for index in range(1, 13)]
    assert all(set(item) == {
        "task_id", "technical", "scientific", "usability"}
        and all(item[field] == MISSING for field in (
            "technical", "scientific", "usability"))
        for item in blank["observations"])
    assert str(tmp_path) not in stdout
    assert not list(tmp_path.iterdir()), "blank-session must not create files"
    assert "participant_count" not in stdout


def test_new_session_creates_exact_utf8_blank_once_and_roundtrips(tmp_path):
    output = tmp_path / "anonymous-operator-session.json"
    assert not output.exists()
    rc, created, stdout = cli("--new-session", str(output))
    assert rc == 0
    assert created == {
        "schema": "pfl.beta_science_operator_session_creation.v1",
        "status": "OPERATOR_SESSION_CREATED",
        "encoding": "UTF-8",
        "tasks_defined": 12,
        "participant_count": None,
        "participants_observed": False,
        "R5": "STOP_R5",
    }
    assert created["participant_count"] is None
    assert str(output) not in stdout
    assert output.name not in stdout
    assert "127.0.0.1" not in stdout
    assert output.is_file()
    stored = output.read_bytes()
    assert stored.startswith(b'{"observations":')
    assert not stored.startswith((b"\xff\xfe", b"\xfe\xff",
                                  b"\xef\xbb\xbf"))
    assert b"\x00" not in stored
    assert stored.decode("utf-8").endswith("\n")
    blank_rc, blank, blank_stdout = cli("--blank-session")
    assert blank_rc == 0
    assert stored == blank_stdout.encode("utf-8")
    assert json.loads(stored.decode("utf-8")) == blank
    assert len(blank["observations"]) == 12
    evaluated_rc, evaluated, evaluated_stdout = cli("--evaluate", str(output))
    assert evaluated_rc == 1
    assert evaluated == {
        "schema": "pfl.beta_science_operator_evaluation.v1",
        "status": "OPERATOR_REJECTED",
        "error_code": "OPERATOR_NO_OBSERVATIONS",
        "participant_count": None,
    }
    assert str(output) not in evaluated_stdout
    before = output.read_bytes()
    repeated_rc, repeated, repeated_stdout = cli("--new-session", str(output))
    assert repeated_rc == 1
    assert repeated["error_code"] == "OPERATOR_SESSION_EXISTS"
    assert repeated["status"] == "OPERATOR_REJECTED"
    assert output.read_bytes() == before
    assert str(output) not in repeated_stdout


def test_new_session_refuses_repo_targets_without_creating_them():
    for forbidden in (
        ROOT / "scripts" / "__operator_session_must_not_create__.json",
        ROOT / "__operator_session_must_not_create__.json",
    ):
        assert not forbidden.exists(), "Choose a target absent from this checkout"
        rc, result, stdout = cli("--new-session", str(forbidden))
        assert rc == 1
        assert result["error_code"] == "OPERATOR_SESSION_PATH_FORBIDDEN"
        assert "OPERATOR_SESSION_CREATED" not in stdout
        assert str(forbidden) not in stdout
        assert forbidden.name not in stdout
        assert not forbidden.exists()


def test_new_session_refuses_any_other_git_worktree(tmp_path):
    external_repo = tmp_path / "second_repository"
    external_repo.mkdir()
    (external_repo / ".git").mkdir()
    destination = external_repo / "should-not-create-session.json"
    assert not destination.exists()
    rc, result, stdout = cli("--new-session", str(destination))
    assert rc == 1
    assert result["error_code"] == "OPERATOR_SESSION_PATH_FORBIDDEN"
    assert str(destination) not in stdout
    assert not destination.exists()
    assert {entry.name for entry in external_repo.iterdir()} == {".git"}


@pytest.mark.parametrize("hardlink_into_git", (False, True))
def test_prepatch_red_new_session_rejects_windows_ntfs_ads_destination(
    tmp_path, hardlink_into_git,
):
    """NTFS ADS writes are not standalone sessions; hardlinks alias Git files.

    The fixture is disposable, outside either project checkout, and is never
    user or institutional material. Unix has no NTFS ADS and is not covered.
    """
    if sys.platform != "win32":
        # Not an NTFS ADS test on POSIX, where ':' is a literal filename.
        # This limitation is explicitly recorded in the operator receipt.
        return
    repo = tmp_path / "synthetic_git_canary"
    repo.mkdir()
    (repo / ".git").mkdir()
    original = repo / "protected_fixture.txt"
    original.write_bytes(b"DISPOSABLE_GIT_SOURCE_BYTES")
    outside = tmp_path / "external_sessions"
    outside.mkdir()
    alias = outside / "hardlinked_alias.txt"
    if hardlink_into_git:
        os.link(original, alias)
        assert os.path.samefile(original, alias)
    else:
        alias.write_bytes(b"DISPOSABLE_OUTSIDE_BYTES")
    before = alias.read_bytes()
    target = Path(str(alias) + ":operator_protocol")
    original_stream = Path(str(original) + ":operator_protocol")
    assert not target.exists()
    assert not original_stream.exists()
    rc, result, stdout = cli("--new-session", str(target))
    assert rc == 1
    assert result["status"] == "OPERATOR_REJECTED"
    assert result["error_code"] == "OPERATOR_SESSION_PATH_INVALID"
    assert str(target) not in stdout
    assert alias.read_bytes() == before
    assert original.read_bytes() == b"DISPOSABLE_GIT_SOURCE_BYTES"
    assert not target.exists(), "No alternate data stream may be created"
    assert not original_stream.exists(), "Hardlink must not add an ADS inside Git"
    assert {p.name for p in outside.iterdir()} == {alias.name}


def test_new_session_refuses_missing_parent_existing_directory_and_existing_file(
    tmp_path,
):
    existing = tmp_path / "existing-canary.json"
    existing.write_bytes(b"KEEP_THESE_BYTES")
    unavailable_parent = tmp_path / "missing-canary" / "nested.json"
    cases = [
        (unavailable_parent, "OPERATOR_SESSION_PARENT_UNAVAILABLE"),
        (tmp_path, "OPERATOR_SESSION_EXISTS"),
        (existing, "OPERATOR_SESSION_EXISTS"),
    ]
    for candidate, code in cases:
        before = set(tmp_path.iterdir())
        rc, result, stdout = cli("--new-session", str(candidate))
        assert rc == 1
        assert result["status"] == "OPERATOR_REJECTED"
        assert result["error_code"] == code
        assert str(candidate) not in stdout
        assert candidate.name not in stdout
        assert set(tmp_path.iterdir()) == before
        assert existing.read_bytes() == b"KEEP_THESE_BYTES"
    assert not unavailable_parent.parent.exists()


def test_new_session_rejects_outside_symlink_parent_resolving_into_repo(tmp_path):
    import os

    link = tmp_path / "linked_repository"
    destination = link / "__operator_link_traversal_must_not_create__.json"
    real_target = ROOT / destination.name
    assert not real_target.exists()
    try:
        link.symlink_to(ROOT, target_is_directory=True)
    except OSError as exc:
        # Windows without SeCreateSymbolicLinkPrivilege cannot create this
        # fixture (WinError 1314). This is NOT proof that the application
        # rejects a directory symlink; the real junction test covers Windows
        # linked-directory containment separately.
        assert sys.platform == "win32", "Unexpected directory symlink failure"
        assert getattr(exc, "winerror", None) == 1314, (
            "Unexpected directory symlink creation failure")
        assert not os.path.lexists(link)
        assert not real_target.exists()
        assert not list(tmp_path.iterdir()), "Denied creation must not leave artifacts"
        print("SYMLINK_PROTECTION_NOT_VERIFIED: Windows denied directory symlink "
              "creation (WinError 1314); real junction test covers linked dirs")
        return
    assert not (ROOT / destination.name).exists()
    rc, result, stdout = cli("--new-session", str(destination))
    assert rc == 1
    assert result["status"] == "OPERATOR_REJECTED"
    assert result["error_code"] == "OPERATOR_SESSION_PATH_FORBIDDEN"
    assert str(destination) not in stdout
    assert not (ROOT / destination.name).exists()
    assert os.path.islink(link)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows junction semantics")
def test_new_session_refuses_windows_junction_into_repository(tmp_path):
    # Windows junctions are accessible even where regular symlink creation
    # requires privileges. No child of the repository may be created.
    linked = tmp_path / "junction_into_checkout"
    made = subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", str(linked), str(ROOT)],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False,
    )
    assert made.returncode == 0, "Windows test fixture junction unavailable"
    target = linked / "__operator_junction_must_not_create__.json"
    real_target = ROOT / target.name
    assert not real_target.exists()
    try:
        rc, result, stdout = cli("--new-session", str(target))
        assert rc == 1
        assert result["error_code"] == "OPERATOR_SESSION_PATH_FORBIDDEN"
        assert result["status"] == "OPERATOR_REJECTED"
        assert str(target) not in stdout
        assert not real_target.exists()
    finally:
        removed = subprocess.run(
            ["cmd.exe", "/c", "rmdir", str(linked)],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", check=False,
        )
        assert removed.returncode == 0, "Could not remove disposable junction"


def test_new_session_rejects_collision_with_broken_symlink(tmp_path):
    import os

    link = tmp_path / "broken-session-link.json"
    target = tmp_path / "nonexistent-target.json"
    assert not target.exists()
    try:
        link.symlink_to(target)
    except OSError as exc:
        # The no-overwrite check against a *broken file symlink* cannot be
        # exercised without creating that symlink. WinError 1314 proves a
        # privileged-creation blocker, not successful application protection.
        assert sys.platform == "win32", "Unexpected file symlink failure"
        assert getattr(exc, "winerror", None) == 1314, (
            "Unexpected file symlink creation failure")
        assert not os.path.lexists(link)
        assert not target.exists()
        assert not list(tmp_path.iterdir()), "Denied creation must not leave artifacts"
        print("SYMLINK_PROTECTION_NOT_VERIFIED: Windows denied file symlink "
              "creation (WinError 1314); no overwrite claim for this fixture")
        return
    rc, result, stdout = cli("--new-session", str(link))
    assert rc == 1
    assert result["error_code"] == "OPERATOR_SESSION_EXISTS"
    assert link.is_symlink()
    assert not (tmp_path / "nonexistent-target.json").exists()
    assert str(link) not in stdout


def test_all_explicit_not_observed_is_not_a_completed_session(tmp_path):
    _, blank, _ = cli("--blank-session")
    path = write_submission(tmp_path, blank)
    rc, result, stdout = cli("--evaluate", str(path))
    assert rc == 1
    assert result == {
        "schema": "pfl.beta_science_operator_evaluation.v1",
        "status": "OPERATOR_REJECTED",
        "error_code": "OPERATOR_NO_OBSERVATIONS",
        "participant_count": None,
    }
    assert str(path) not in stdout


@pytest.mark.parametrize("missing_count", (1, 4, 11, 12))
def test_partial_sessions_rejected_even_with_valid_individual_rows(
    tmp_path, missing_count,
):
    _, blank, _ = cli("--blank-session")
    rows = blank["observations"][:12 - missing_count]
    if rows:
        rows[0] = dict(rows[0], technical="TECH_COMPLETED")
    path = write_submission(tmp_path, {"schema": SCHEMA, "observations": rows})
    rc, result, stdout = cli("--evaluate", str(path))
    assert rc == 1
    assert result["status"] == "OPERATOR_REJECTED"
    assert result["error_code"] == "OPERATOR_SESSION_INCOMPLETE"
    assert result["participant_count"] is None
    assert str(path) not in stdout


def test_full_session_with_explicit_not_observed_tasks_is_valid(tmp_path):
    _, blank, _ = cli("--blank-session")
    rows = blank["observations"]
    rows[0] = dict(rows[0], technical="TECH_COMPLETED",
                   scientific="SCI_OP01_EQUIVALENT", usability="UX_FRICTION")
    rows[1] = dict(rows[1], technical="TECH_BLOCKED",
                   scientific=MISSING, usability="UX_BLOCKED")
    path = write_submission(tmp_path, {"schema": SCHEMA, "observations": rows})
    rc, result, stdout = cli("--evaluate", str(path))
    assert rc == 0
    assert result["status"] == "OPERATOR_EVALUATION_COMPLETE"
    assert result["tasks_with_any_coded_observation"] == 2
    assert result["rollup"]["scientific"]["SCI_CORRECT"] == 1
    assert result["rollup"]["scientific"][MISSING] == 11
    assert result["rollup"]["technical"][MISSING] == 10
    assert result["rollup"]["technical"]["TECH_BLOCKED"] == 1
    assert result["participant_count"] is None
    assert str(path) not in stdout
