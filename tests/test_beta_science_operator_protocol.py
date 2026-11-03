"""CLI contract tests: no participant is generated or inferred by this suite."""
from __future__ import annotations

import json
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
        assert all(x["code"].startswith("SCI_" + item["task_id"] + "_")
                   for x in options)
    assert "NOT_OBSERVED" in result["input_contract"]["technical_codes"]
    assert "NOT_OBSERVED" in result["input_contract"]["usability_codes"]
    assert "participant" in result["instructions"].lower()
    assert "http://127.0.0.1:" not in stdout
    assert "cookie=" not in stdout


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
        assert sheet["scientific_options"] == rubric["scientific_options"]
        assert rubric["correct_answer_code"] in {
            option["code"] for option in sheet["scientific_options"]}
        assert "correct_answer_code" not in sheet
        assert "scientific_explanation" not in sheet
        assert "technical_task_ids" not in sheet
        assert "technical_success_criterion" not in sheet
        assert "usability_observation_criterion" not in sheet
    assert "correct_answer_code" not in stdout
    assert "scientific_explanation" not in stdout
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
    wrong = tasks[2]["scientific_options"][1]["code"]
    path = write_submission(tmp_path, {
        "schema": SCHEMA, "observations": [
            response(tasks[0], technical="TECH_COMPLETED",
                     usability="UX_FRICTION"),
            response(tasks[2], technical="TECH_COMPLETED",
                     scientific=wrong, usability="UX_BLOCKED"),
            response(tasks[6], technical="TECH_FAILED",
                     scientific=MISSING, usability="UX_CLEAR"),
            response(tasks[8], technical="TECH_BLOCKED",
                     scientific=MISSING, usability=MISSING),
        ],
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


def test_empty_submission_means_no_observations_not_zero_successes(tmp_path):
    path = write_submission(tmp_path, {"schema": SCHEMA, "observations": []})
    rc, result, _ = cli("--evaluate", str(path))
    assert rc == 0 and result["tasks_with_any_coded_observation"] == 0
    assert result["participant_count"] is None
    assert result["rollup"]["technical"][MISSING] == 12
    assert result["rollup"]["scientific"][MISSING] == 12
    assert result["rollup"]["usability"][MISSING] == 12
    assert all(all(t[field] == MISSING for field in (
        "technical", "scientific", "usability")) for t in result["tasks"])
