"""Coded v2 revision and exact-byte evaluation evidence ? synthetic harness only.

Owns no application code. Reuses the existing isolated v2 form helper.
No real participants, no network, no Chrome, no uploads or gate changes.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from test_beta_operator_instrument_versioning import _prepared_v2, run_cli


MISSING = "NOT_OBSERVED"
V2_SCHEMA = "pfl.beta_science_operator_observations.v2"
V2_RESULT_SCHEMA = "pfl.beta_science_operator_evaluation.v2"


def test_prepatch_red_v2_evaluation_binds_exact_source_bytes(tmp_path: Path):
    """Existing v2 result omits exact coded source SHA despite rubric SHA."""
    document, rubric, _, source, _, rubric_path = _prepared_v2(
        tmp_path, "source_sha_prepatch")
    selected = next(row for row in document["observations"]
                    if row["task_id"] == "OP01")
    selected["technical"] = "TECH_COMPLETED"
    selected["scientific"] = rubric["tasks"][0]["correct_answer_code"]
    selected["usability"] = "UX_CLEAR"
    # Intentionally noncanonical whitespace to require hashing RAW BYTES,
    # not reconstructed JSON or a normalized representation.
    raw_input = (json.dumps(document, ensure_ascii=True, indent=2) + "\n").encode(
        "utf-8")
    source.write_bytes(raw_input)
    result_file = source.parent / "scored SHA synthetic.json"
    assert not result_file.exists()
    rc, receipt, stdout = run_cli("--evaluate-form", source, rubric_path, result_file)
    assert rc == 0, receipt
    assert receipt["status"] == "OPERATOR_FORM_EVALUATION_EXPORTED"
    assert str(source) not in stdout and str(result_file) not in stdout
    assert result_file.is_file()
    evaluated = json.loads(result_file.read_bytes().decode("utf-8"))
    assert evaluated["schema"] == V2_RESULT_SCHEMA
    assert evaluated["operator_instrument_sha256"] == hashlib.sha256(
        rubric_path.read_bytes()).hexdigest()
    assert evaluated["handout_sha256"] == document["handout_sha256"]
    assert evaluated["coded_input_sha256"] == hashlib.sha256(raw_input).hexdigest()
    assert source.read_bytes() == raw_input
    assert evaluated["participant_count"] is None




def _synthetic_record(
    source: Path,
    destination: Path,
    task_id: str,
    technical: str,
    scientific: str,
    usability: str,
) -> tuple[int, dict, str]:
    """One real subprocess; the values are *fabricated harness observations*."""
    return run_cli(
        "--record-form", source, destination,
        task_id, technical, scientific, usability,
    )


def _assert_safe_stdout(raw: str, *paths: Path) -> None:
    for path in paths:
        assert str(path) not in raw
        assert path.name not in raw
    assert "PRIVATE_CANARY" not in raw
    assert "session_cookie" not in raw


def _assert_record_receipt(
    code: int, receipt: dict, raw: str, source: Path, destination: Path,
) -> dict:
    assert code == 0, receipt
    assert receipt["status"] == "OPERATOR_FORM_OBSERVATION_RECORDED"
    assert receipt["source_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert receipt["destination_sha256"] == hashlib.sha256(
        destination.read_bytes()).hexdigest()
    assert receipt["source_sha256"] != receipt["destination_sha256"]
    assert receipt.get("participant_count") is None
    assert receipt.get("participants_observed") in (None, False)
    _assert_safe_stdout(raw, source, destination)
    assert destination.is_file()
    data = destination.read_bytes()
    assert data.startswith(b"{")
    assert not data.startswith((b"\xff\xfe", b"\xfe\xff", b"\xef\xbb\xbf"))
    assert b"\x00" not in data
    return json.loads(data.decode("utf-8"))


def test_v2_record_form_two_step_synthetic_chain_and_exact_export_sha(
    tmp_path: Path,
):
    """First blocked OP09 then completed OP01; both revisions independently bound."""
    blank, rubric, _, source, _, key = _prepared_v2(tmp_path, "revision_chain")
    assert blank["schema"] == V2_SCHEMA
    assert len(blank["observations"]) == 12
    # Re-encode the unchanged blank synthetic v2 source with noncanonical
    # whitespace: predecessor SHA must fingerprint exact bytes, not JSON AST.
    source.write_bytes((json.dumps(blank, ensure_ascii=True, indent=2) +
                        "\n").encode("utf-8"))
    root_bytes = source.read_bytes()
    assert root_bytes and b"  " in root_bytes
    row_ids = {row["task_id"] for row in blank["observations"]}
    assert len(row_ids) == 12

    revision1 = source.parent / "revision one \u03a9 blocked.json"
    rc, proof1, stdout1 = _synthetic_record(
        source, revision1, "OP09", "TECH_BLOCKED", MISSING, "UX_BLOCKED",
    )
    snapshot1 = _assert_record_receipt(rc, proof1, stdout1, source, revision1)
    assert source.read_bytes() == root_bytes
    assert snapshot1["form_id"] == blank["form_id"]
    assert snapshot1["rubric_sha256"] == blank["rubric_sha256"]
    assert snapshot1["handout_sha256"] == blank["handout_sha256"]
    assert len(snapshot1["observations"]) == 12
    assert set(snapshot1) == set(blank)
    by_id1 = {x["task_id"]: x for x in snapshot1["observations"]}
    assert by_id1["OP09"] == {
        "task_id": "OP09", "technical": "TECH_BLOCKED",
        "scientific": MISSING, "usability": "UX_BLOCKED",
    }
    assert all(item == next(
        old for old in blank["observations"] if old["task_id"] == item["task_id"])
        for item in snapshot1["observations"] if item["task_id"] != "OP09")

    # First descendant is a valid *coded* but partly unobserved synthetic
    # record, so evaluation must hash precisely the bytes on disk at time of read.
    scored1 = source.parent / "evaluated revision one.json"
    rc, score_receipt1, raw_score1 = run_cli(
        "--evaluate-form", revision1, key, scored1,
    )
    assert rc == 0, score_receipt1
    _assert_safe_stdout(raw_score1, revision1, key, scored1)
    result1 = json.loads(scored1.read_text(encoding="utf-8"))
    assert result1["coded_input_sha256"] == hashlib.sha256(
        revision1.read_bytes()).hexdigest()
    assert result1["rollup"]["technical"]["TECH_BLOCKED"] == 1
    assert result1["rollup"]["scientific"][MISSING] == 12
    assert result1["participant_count"] is None

    # Another edit is created from the DESCENDANT file, never in-place;
    # A/B codes remain rubric-private and session-specific.
    correct_op01 = next(
        row["correct_answer_code"] for row in rubric["tasks"]
        if row["task_id"] == "OP01"
    )
    assert correct_op01 in ("A", "B")
    revision2 = source.parent / "revision two \u03a9 completed.json"
    source1_bytes = revision1.read_bytes()
    rc, proof2, stdout2 = _synthetic_record(
        revision1, revision2, "OP01", "TECH_COMPLETED", correct_op01, "UX_FRICTION",
    )
    snapshot2 = _assert_record_receipt(rc, proof2, stdout2, revision1, revision2)
    assert revision1.read_bytes() == source1_bytes
    assert source.read_bytes() == root_bytes
    assert snapshot2["form_id"] == snapshot1["form_id"]
    assert snapshot2["observations"][8] == snapshot1["observations"][8]
    assert snapshot2["observations"][0] == {
        "task_id": "OP01", "technical": "TECH_COMPLETED",
        "scientific": correct_op01, "usability": "UX_FRICTION",
    }

    scored2 = source.parent / "evaluated revision two \u03a9.json"
    rc, score_receipt2, raw_score2 = run_cli(
        "--evaluate-form", revision2, key, scored2,
    )
    assert rc == 0, score_receipt2
    _assert_safe_stdout(raw_score2, revision2, key, scored2)
    result2 = json.loads(scored2.read_bytes().decode("utf-8"))
    assert result2["schema"] == V2_RESULT_SCHEMA
    assert result2["coded_input_sha256"] == hashlib.sha256(
        revision2.read_bytes()).hexdigest()
    assert result2["coded_input_sha256"] != result1["coded_input_sha256"]
    assert result2["operator_instrument_sha256"] == hashlib.sha256(
        key.read_bytes()).hexdigest()
    assert result2["handout_sha256"] == blank["handout_sha256"]
    assert result2["rollup"]["technical"]["TECH_COMPLETED"] == 1
    assert result2["rollup"]["technical"]["TECH_BLOCKED"] == 1
    assert result2["rollup"]["scientific"]["SCI_CORRECT"] == 1
    assert result2["rollup"]["scientific"][MISSING] == 11
    assert result2["tasks_with_any_coded_observation"] == 2
    assert result2["participant_count"] is None
    assert result2["gate_eligibility"] == "OPERATOR_NOT_ASSESSED"
    assert result2["R5"] == "STOP_R5"


def test_v2_record_form_repeated_task_fails_without_output_or_mutation(tmp_path: Path):
    blank, _, _, source, _, _ = _prepared_v2(tmp_path, "duplicate_record")
    first = source.parent / "one already coded.json"
    rc, receipt, raw = _synthetic_record(
        source, first, "OP09", "TECH_BLOCKED", MISSING, "UX_FRICTION",
    )
    _assert_record_receipt(rc, receipt, raw, source, first)
    before = first.read_bytes()
    source_before = source.read_bytes()
    for scientific in (MISSING, "A", "B"):
        destination = source.parent / ("REJECT_OP09_" + scientific + ".json")
        assert not destination.exists()
        rc, fail, raw_fail = _synthetic_record(
            first, destination, "OP09", "TECH_COMPLETED",
            scientific, "UX_CLEAR",
        )
        assert rc != 0
        assert fail["status"] == "OPERATOR_REJECTED"
        assert fail["error_code"] == "OPERATOR_OBSERVATION_ALREADY_RECORDED"
        assert fail["participant_count"] is None
        assert not destination.exists()
        assert first.read_bytes() == before
        assert source.read_bytes() == source_before
        _assert_safe_stdout(raw_fail, first, destination)


@pytest.mark.parametrize("technical", (
    "TECH_BLOCKED", "TECH_FAILED", MISSING,
))
@pytest.mark.parametrize("answer", ("A", "B"))
def test_v2_record_form_scientific_veto_when_technical_not_completed(
    tmp_path: Path, technical: str, answer: str,
):
    blank, _, _, source, _, _ = _prepared_v2(
        tmp_path, "technical_veto_" + technical + answer)
    destination = source.parent / "no-science-while-blocked.json"
    before = source.read_bytes()
    rc, error, raw = _synthetic_record(
        source, destination, "OP01", technical, answer, "UX_CLEAR",
    )
    assert rc != 0
    assert error["status"] == "OPERATOR_REJECTED"
    assert error["error_code"].startswith("OPERATOR_")
    assert error["participant_count"] is None
    assert not destination.exists()
    assert source.read_bytes() == before
    _assert_safe_stdout(raw, source, destination)


def test_v2_record_form_accepts_ux_only_code_without_scientific_imputation(
    tmp_path: Path,
):
    _, _, _, source, _, key = _prepared_v2(tmp_path, "ux_only")
    destination = source.parent / "coded UX only.json"
    rc, receipt, raw = _synthetic_record(
        source, destination, "OP04", MISSING, MISSING, "UX_FRICTION",
    )
    result = _assert_record_receipt(rc, receipt, raw, source, destination)
    row = next(item for item in result["observations"] if item["task_id"] == "OP04")
    assert row["technical"] == MISSING
    assert row["scientific"] == MISSING
    assert row["usability"] == "UX_FRICTION"
    # A UX-only task is NOT blank. A subsequent attempt must be rejected
    # even though its technical and scientific fields remain NOT_OBSERVED.
    forbidden_successor = source.parent / "must-not-recode-ux-only.json"
    before_ux = destination.read_bytes()
    rc2, reject, reject_stdout = _synthetic_record(
        destination, forbidden_successor,
        "OP04", "TECH_COMPLETED", "A", "UX_CLEAR",
    )
    assert rc2 != 0 and reject["status"] == "OPERATOR_REJECTED"
    assert reject["error_code"] == "OPERATOR_OBSERVATION_ALREADY_RECORDED"
    assert reject["participant_count"] is None
    assert not forbidden_successor.exists()
    assert destination.read_bytes() == before_ux
    _assert_safe_stdout(reject_stdout, destination, forbidden_successor)
    scored = source.parent / "ux-only-classification.json"
    rc, result_receipt, _ = run_cli("--evaluate-form", destination, key, scored)
    assert rc == 0, result_receipt
    evaluation = json.loads(scored.read_bytes().decode("utf-8"))
    assert evaluation["coded_input_sha256"] == hashlib.sha256(
        destination.read_bytes()).hexdigest()
    assert evaluation["rollup"]["scientific"][MISSING] == 12
    assert evaluation["rollup"]["usability"]["UX_FRICTION"] == 1


def test_v2_record_form_separate_sessions_remain_isolated(tmp_path: Path):
    prepared_a = _prepared_v2(tmp_path, "session_A")
    prepared_b = _prepared_v2(tmp_path, "session_B")
    left, right = prepared_a[0], prepared_b[0]
    assert left["form_id"] != right["form_id"]
    outputs = []
    for label, prepared in (("A", prepared_a), ("B", prepared_b)):
        input_session, _, _, source, _, _ = prepared
        destination = source.parent / ("revision unique " + label + ".json")
        rc, receipt, raw = _synthetic_record(
            source, destination, "OP02", "TECH_COMPLETED", "A", "UX_CLEAR",
        )
        revised = _assert_record_receipt(rc, receipt, raw, source, destination)
        assert revised["form_id"] == input_session["form_id"]
        assert revised["rubric_sha256"] == input_session["rubric_sha256"]
        outputs.append(destination)
    assert outputs[0].read_bytes() != outputs[1].read_bytes()




@pytest.mark.parametrize("problem", (
    "wrong_v1_schema",
    "unknown_top_level",
    "missing_form_id",
    "bad_form_id_type",
    "bad_form_id_format",
    "bad_rubric_digest",
    "bad_handout_digest",
    "missing_task",
    "extra_task",
    "duplicate_task_id",
    "unknown_task_id",
    "extra_pii_field",
    "scientific_answer_without_tech",
    "scientific_code_not_opaque",
    "wrong_observation_type",
    "unknown_technical_status",
    "unknown_usability_status",
))
def test_v2_record_form_rejects_corrupt_or_unbound_session_before_writing(
    tmp_path: Path, problem: str,
):
    """Every malformed/PII scenario remains a disposable synthetic fixture."""
    blank, _, _, original, _, _ = _prepared_v2(tmp_path, problem)
    source = original.parent / ("tampered " + problem + ".json")
    destination = original.parent / ("rejected " + problem + ".json")
    document = json.loads(original.read_bytes().decode("utf-8"))
    assert len(document["observations"]) == 12
    first = document["observations"][0]
    if problem == "wrong_v1_schema":
        document["schema"] = "pfl.beta_science_operator_observations.v1"
    elif problem == "unknown_top_level":
        document["source_path"] = "C:/PRIVATE_CANARY/not_public.json"
    elif problem == "missing_form_id":
        document.pop("form_id")
    elif problem == "bad_form_id_type":
        document["form_id"] = True
    elif problem == "bad_form_id_format":
        document["form_id"] = "not-hex32"
    elif problem == "bad_rubric_digest":
        document["rubric_sha256"] = "missing"
    elif problem == "bad_handout_digest":
        document["handout_sha256"] = None
    elif problem == "missing_task":
        document["observations"].pop()
    elif problem == "extra_task":
        document["observations"].append(dict(first))
    elif problem == "duplicate_task_id":
        document["observations"][1]["task_id"] = first["task_id"]
    elif problem == "unknown_task_id":
        first["task_id"] = "OP99"
    elif problem == "extra_pii_field":
        first["email"] = "PRIVATE_CANARY@example.invalid"
    elif problem == "scientific_answer_without_tech":
        first["scientific"] = "A"
    elif problem == "scientific_code_not_opaque":
        first["technical"] = "TECH_COMPLETED"
        first["scientific"] = "SCI_OP01_EQUIVALENT"
    elif problem == "wrong_observation_type":
        document["observations"][0] = "PRIVATE_CANARY"
    elif problem == "unknown_technical_status":
        first["technical"] = "TECH_SPOOFED"
    elif problem == "unknown_usability_status":
        first["usability"] = "UX_GOOD"
    else:
        raise AssertionError("Unknown negative test case")
    source.write_bytes(json.dumps(
        document, sort_keys=True, ensure_ascii=True,
        separators=(",", ":")).encode("utf-8"))
    assert not destination.exists()
    before = source.read_bytes()
    rc, rejected, raw = _synthetic_record(
        source, destination, "OP09", "TECH_BLOCKED", MISSING, "UX_BLOCKED",
    )
    assert rc != 0
    assert rejected["status"] == "OPERATOR_REJECTED"
    assert rejected["error_code"].startswith("OPERATOR_")
    if problem in ("wrong_v1_schema", "missing_form_id",
                   "bad_form_id_type", "bad_form_id_format",
                   "bad_rubric_digest", "bad_handout_digest"):
        assert rejected["error_code"] == "OPERATOR_FORM_MISMATCH"
    assert rejected["participant_count"] is None
    assert not destination.exists()
    assert source.read_bytes() == before
    _assert_safe_stdout(raw, source, destination)


@pytest.mark.parametrize("mode", (
    "output_already_exists",
    "same_as_source",
    "missing_parent",
    "directory_output",
    "repo_output",
    "windows_ads",
))
def test_v2_record_form_destination_policy_is_atomic_and_write_once(
    tmp_path: Path, mode: str,
):
    """No overwrite, new file in checkout or hidden NTFS streams."""
    if mode == "windows_ads" and os.name != "nt":
        # No claim that Unix paths support NTFS alternate data streams.
        pytest.skip("NTFS ADS specific test requires Windows")
    blank, _, _, source, _, _ = _prepared_v2(tmp_path, mode)
    anchor = source.parent / "existing synthetic anchor.txt"
    anchor.write_bytes(b"KEEP_SYNTHETIC_SENTINEL")
    existing = source.parent / "occupied report.json"
    existing.write_bytes(b"EXISTING_REPORT_UNCHANGED")
    if mode == "output_already_exists":
        destination = existing
    elif mode == "same_as_source":
        destination = source
    elif mode == "missing_parent":
        destination = source.parent / "NONEXISTING_PARENT" / "result.json"
    elif mode == "directory_output":
        destination = source.parent
    elif mode == "repo_output":
        destination = Path(__file__).resolve().parents[1] / (
            "__operator_record_form_must_not_write__.json")
        assert not destination.exists()
    elif mode == "windows_ads":
        destination = Path(str(anchor) + ":synthetic_record")
        assert not os.path.lexists(destination)
    else:
        raise AssertionError("Unknown destination test case")
    before = source.read_bytes()
    children = set(source.parent.iterdir())
    rc, failure, raw = _synthetic_record(
        source, destination, "OP03", "TECH_COMPLETED", "B", "UX_CLEAR",
    )
    assert rc != 0
    assert failure["status"] == "OPERATOR_REJECTED"
    assert failure["error_code"].startswith("OPERATOR_")
    assert failure["participant_count"] is None
    assert source.read_bytes() == before
    assert anchor.read_bytes() == b"KEEP_SYNTHETIC_SENTINEL"
    assert existing.read_bytes() == b"EXISTING_REPORT_UNCHANGED"
    assert not (source.parent / "NONEXISTING_PARENT").exists()
    assert not (Path(__file__).resolve().parents[1] /
                "__operator_record_form_must_not_write__.json").exists()
    assert set(source.parent.iterdir()) == children
    if mode == "windows_ads":
        assert not os.path.lexists(destination)
    _assert_safe_stdout(raw, source, destination)


def test_v1_record_form_is_rejected_without_implicit_schema_migration(tmp_path: Path):
    code, legacy, _ = run_cli("--blank-session")
    assert code == 0
    assert legacy["schema"] == "pfl.beta_science_operator_observations.v1"
    source = tmp_path / "legacy v1 fake operator record.json"
    destination = tmp_path / "must not migrate v1 to v2.json"
    source.write_bytes(json.dumps(
        legacy, ensure_ascii=True, separators=(",", ":")).encode("utf-8"))
    before = source.read_bytes()
    rc, rejected, raw = _synthetic_record(
        source, destination, "OP01", "TECH_COMPLETED", "A", "UX_CLEAR",
    )
    assert rc != 0
    assert rejected["status"] == "OPERATOR_REJECTED"
    assert rejected["error_code"] == "OPERATOR_FORM_MISMATCH"
    assert rejected["participant_count"] is None
    assert not destination.exists()
    assert source.read_bytes() == before
    _assert_safe_stdout(raw, source, destination)


def test_v2_record_form_refuses_empty_operation_not_spurious_record(
    tmp_path: Path,
):
    _, _, _, source, _, _ = _prepared_v2(tmp_path, "empty_action")
    destination = source.parent / "empty must not be recorded.json"
    before = source.read_bytes()
    rc, failure, raw = _synthetic_record(
        source, destination, "OP02", MISSING, MISSING, MISSING,
    )
    assert rc != 0
    assert failure["status"] == "OPERATOR_REJECTED"
    assert failure["error_code"] == "OPERATOR_OBSERVATION_EMPTY"
    assert not destination.exists()
    assert source.read_bytes() == before
    _assert_safe_stdout(raw, source, destination)
