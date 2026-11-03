"""Real OS operator handoff: synthetic fixture only, never a human session.

This module covers the new --evaluate-to contract and reuses pre-existing
science_server, doctor and operator helpers. It does NOT duplicate browser
Chrome tests or claim empirical observations. All mutable files live in pytest
temporary directories outside a Git worktree.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import parse_qsl, urlsplit

from test_beta_supervised_runtime import (
    CANONICAL_PAIRS,
    CANONICAL_QUERY,
    ENV,
    PROTOCOL,
    ROOT,
    _no_accounts_or_game_db,
    _protocol,
    _require_synthetic_stop,
    _source_digests,
    run_doctor,
    science_server,
)


def _protocol_with_raw(*args: str | Path) -> tuple[int, dict, str]:
    """Check JSON stdout and privacy, not only a parsed Python dictionary."""
    p = subprocess.run(
        [sys.executable, "-B", str(PROTOCOL), *map(str, args)],
        cwd=ROOT, env=ENV, stdin=subprocess.DEVNULL,
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=15, check=False,
    )
    assert p.stderr == "", "No traceback/path may be written to stderr"
    assert p.stdout.count("\n") == 1
    assert len(p.stdout) < 35_000
    decoded = json.loads(p.stdout)
    assert type(decoded) is dict
    return p.returncode, decoded, p.stdout


def _external_directory(tmp_path: Path) -> Path:
    # Temporary pytest root must be external to this Git checkout and its
    # ancestors, including on Windows, before any operator CLI writes.
    external = tmp_path / "\u00d3pera sint\u00e9tica \u00b7 pruebas con espacios"
    external.mkdir()
    assert not external.resolve().is_relative_to(ROOT.resolve())
    assert not any(os.path.lexists(p / ".git")
                   for p in (external, *external.parents))
    return external


def _coded_synthetic_fixture(path: Path, rubric: dict) -> dict:
    """Manual synthetic harness codes, explicitly not an observed participant."""
    source = json.loads(path.read_bytes().decode("utf-8"))
    assert source["schema"] == "pfl.beta_science_operator_observations.v1"
    assert len(source["observations"]) == len(rubric["tasks"]) == 12
    key = {t["task_id"]: t for t in rubric["tasks"]}
    wrong_s3 = next(
        option["code"] for option in key["OP03"]["scientific_options"]
        if option["code"] != key["OP03"]["correct_answer_code"]
    )
    for item in source["observations"]:
        if item["task_id"] == "OP11":
            item.update(
                technical="TECH_COMPLETED",
                scientific=key["OP11"]["correct_answer_code"],
                usability="UX_FRICTION",
            )
        elif item["task_id"] == "OP03":
            item.update(
                technical="TECH_COMPLETED",
                scientific=wrong_s3,
                usability="UX_CLEAR",
            )
        elif item["task_id"] == "OP09":
            item.update(
                technical="TECH_BLOCKED",
                scientific="NOT_OBSERVED",
                usability="UX_BLOCKED",
            )
    assert {entry["task_id"] for entry in source["observations"]} == set(key)
    path.write_bytes(
        (json.dumps(source, sort_keys=True, separators=(",", ":"),
                    ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")
    )
    return source


def _assert_no_path_or_people(raw: str, *paths: Path) -> None:
    for path in paths:
        assert str(path) not in raw
        assert path.name not in raw
    payload = json.loads(raw)
    assert "participant_id" not in payload
    assert "session_cookie" not in payload
    assert "operator_name" not in payload


def _assert_no_game_files(db: Path) -> None:
    _no_accounts_or_game_db(db)
    assert (db.parent / "scientific_registry_synthetic.sqlite3").is_file()


def test_operator_reboot_rebind_and_export_synthetic_coded_session(tmp_path: Path):
    """Two real OS servers, then one real exported evaluation, no Chrome."""
    external = _external_directory(tmp_path)
    db = external / "Base persistente \u03a9" / "unused-fantasy.sqlite3"
    scientific_db = db.parent / "scientific_registry_synthetic.sqlite3"
    original_port = None

    # OS process #1: initial synthetic registry and original old bookmark.
    with science_server(db) as first:
        assert first.port is not None and first.origin is not None
        original_port = first.port
        bookmark = f"{first.origin}/?{CANONICAL_QUERY}"
        assert tuple(parse_qsl(urlsplit(bookmark).query)) == CANONICAL_PAIRS
        rc, initial = run_doctor(
            first.origin, guest_query=bookmark, emit_verified_guest_url=True,
        )
        assert rc == 0 and initial["status"] == "PASS"
        assert initial["verified_guest_url"] == bookmark
        _require_synthetic_stop(initial)
        digest_early_late = _source_digests(initial)
        assert scientific_db.is_file()
        db_sha_before = hashlib.sha256(scientific_db.read_bytes()).hexdigest()
        _assert_no_game_files(db)

    # Old localhost port is stopped: a bookmark cannot fake a live session.
    rc, unavailable = run_doctor(
        f"http://127.0.0.1:{original_port}",
        guest_query=bookmark, emit_verified_guest_url=True,
    )
    assert rc != 0 and unavailable["status"] == "FAIL"
    assert unavailable["error_code"] == "SERVER_UNAVAILABLE"
    assert "verified_guest_url" not in unavailable

    # OS process #2: same physical SQLite, new port and same seven-key recipe.
    with science_server(db, resume=bookmark) as second:
        assert second.port is not None and second.port != original_port
        assert second.origin is not None and second.resumed_url is not None
        rc, current = run_doctor(
            second.origin, guest_query=bookmark, emit_verified_guest_url=True,
        )
        assert rc == 0 and current["status"] == "PASS"
        _require_synthetic_stop(current)
        assert _source_digests(current) == digest_early_late
        assert current["verified_guest_url"] == second.resumed_url
        assert tuple(parse_qsl(
            urlsplit(current["verified_guest_url"]).query)) == CANONICAL_PAIRS
        assert urlsplit(current["verified_guest_url"]).netloc == (
            f"127.0.0.1:{second.port}")
        assert hashlib.sha256(scientific_db.read_bytes()).hexdigest() == db_sha_before

        # Real, separately executed operator CLI creates a blank session once;
        # every coded observation below is fabricated exclusively in this test.
        session = external / "sesi\u00f3n codificada \u03a9 sint\u00e9tica.json"
        rc, created = _protocol("--new-session", str(session))
        assert rc == 0 and created["status"] == "OPERATOR_SESSION_CREATED"
        assert created["participant_count"] is None
        assert session.is_file()
        original_bytes = session.read_bytes()
        assert original_bytes.startswith(b"{") and b"\x00" not in original_bytes
        assert not original_bytes.startswith((b"\xff\xfe", b"\xef\xbb\xbf"))

        rc, rubric = _protocol("--template")
        assert rc == 0 and len(rubric["tasks"]) == 12
        synthetic_data = _coded_synthetic_fixture(session, rubric)
        rc, expected = _protocol("--evaluate", str(session))
        assert rc == 0 and expected["status"] == "OPERATOR_EVALUATION_COMPLETE"
        assert expected["participant_count"] is None
        assert expected["participant_identity_collected"] is False
        assert expected["R5"] == "STOP_R5"
        assert expected["gate_eligibility"] == "OPERATOR_NOT_ASSESSED"
        assert expected["tasks_with_any_coded_observation"] == 3
        assert expected["rollup"]["technical"]["TECH_COMPLETED"] == 2
        assert expected["rollup"]["technical"]["TECH_BLOCKED"] == 1
        assert expected["rollup"]["scientific"]["SCI_CORRECT"] == 1
        assert expected["rollup"]["scientific"]["SCI_INCORRECT"] == 1
        assert expected["rollup"]["scientific"]["NOT_OBSERVED"] == 10
        assert len(synthetic_data["observations"]) == 12

        # NEW capability under contract: output goes to a separate UTF-8 file
        # via no-overwrite 'xb'; not into stdout, not into a Git checkout.
        exported_path = external / "resultado cierre \u03a9 sin participantes.json"
        assert not exported_path.exists()
        rc, receipt, raw = _protocol_with_raw(
            "--evaluate-to", session, exported_path)
        assert rc == 0, receipt
        assert receipt.get("status") == "OPERATOR_EVALUATION_EXPORTED"
        _assert_no_path_or_people(raw, session, exported_path)
        assert receipt.get("participant_count") is None
        assert exported_path.is_file()
        exported_bytes = exported_path.read_bytes()
        assert exported_bytes.startswith(b"{")
        assert not exported_bytes.startswith((b"\xff\xfe", b"\xfe\xff", b"\xef\xbb\xbf"))
        assert b"\x00" not in exported_bytes
        assert json.loads(exported_bytes.decode("utf-8")) == expected
        assert hashlib.sha256(scientific_db.read_bytes()).hexdigest() == db_sha_before
        _assert_no_game_files(db)

        # A second attempt must not overwrite any result or source bytes.
        source_before = session.read_bytes()
        rc, duplicate, duplicate_raw = _protocol_with_raw(
            "--evaluate-to", session, exported_path)
        assert rc != 0 and duplicate["status"] == "OPERATOR_REJECTED"
        assert duplicate["error_code"].startswith("OPERATOR_")
        _assert_no_path_or_people(duplicate_raw, session, exported_path)
        assert exported_path.read_bytes() == exported_bytes
        assert session.read_bytes() == source_before

        # Opt-in v2 instrument lives in separate supervisor/participant
        # directories, while the real science-only HTTP server stays alive.
        # These are invented fixture codes; NO person was observed.
        v2_private = external / "Supervisor v2"
        v2_public = external / "Participante v2"
        v2_private.mkdir()
        v2_public.mkdir()
        v2_source = v2_private / "observaciones ciegas v2.json"
        v2_handout = v2_public / "hoja sin clave v2.html"
        v2_rubric = v2_private / "rubrica de operador v2.json"
        v2_output = v2_private / "resultado clasificado v2.json"
        rc, v2_ready, ready_stdout = _protocol_with_raw(
            "--prepare-form", v2_source, v2_handout, v2_rubric)
        assert rc == 0 and v2_ready["status"] == "OPERATOR_FORM_PREPARED"
        assert v2_ready["correct_A_count"] == v2_ready["correct_B_count"] == 6
        _assert_no_path_or_people(
            ready_stdout, v2_source, v2_handout, v2_rubric)
        v2_body = json.loads(v2_source.read_text(encoding="utf-8"))
        v2_key = json.loads(v2_rubric.read_text(encoding="utf-8"))
        assert v2_body["schema"] == "pfl.beta_science_operator_observations.v2"
        assert v2_body["form_id"] == v2_key["form_id"]
        assert hashlib.sha256(v2_handout.read_bytes()).hexdigest() == (
            v2_body["handout_sha256"])
        assert "SCI_OP" not in v2_handout.read_text(encoding="utf-8")
        v2_correct = v2_key["tasks"][0]["correct_answer_code"]
        v2_root_bytes = v2_source.read_bytes()
        v2_revision1 = v2_private / "revision 1 completada.json"
        v2_revision2 = v2_private / "revision 2 bloqueada.json"
        rc, recorded1, recorded1_raw = _protocol_with_raw(
            "--record-form", v2_source, v2_revision1,
            "OP01", "TECH_COMPLETED", v2_correct, "UX_CLEAR")
        assert rc == 0 and recorded1["status"] == (
            "OPERATOR_FORM_OBSERVATION_RECORDED")
        _assert_no_path_or_people(
            recorded1_raw, v2_source, v2_revision1)
        assert recorded1["source_sha256"] == hashlib.sha256(
            v2_root_bytes).hexdigest()
        assert v2_source.read_bytes() == v2_root_bytes
        rc, recorded2, recorded2_raw = _protocol_with_raw(
            "--record-form", v2_revision1, v2_revision2,
            "OP09", "TECH_BLOCKED", "NOT_OBSERVED", "UX_BLOCKED")
        assert rc == 0 and recorded2["status"] == (
            "OPERATOR_FORM_OBSERVATION_RECORDED")
        _assert_no_path_or_people(
            recorded2_raw, v2_revision1, v2_revision2)
        assert recorded2["source_sha256"] == recorded1["destination_sha256"]
        assert v2_source.read_bytes() == v2_root_bytes
        rc, v2_receipt, v2_raw = _protocol_with_raw(
            "--evaluate-form", v2_revision2, v2_rubric, v2_output)
        assert rc == 0 and v2_receipt["status"] == (
            "OPERATOR_FORM_EVALUATION_EXPORTED")
        _assert_no_path_or_people(
            v2_raw, v2_revision2, v2_rubric, v2_output)
        v2_result = json.loads(v2_output.read_text(encoding="utf-8"))
        assert v2_result["coded_input_sha256"] == recorded2["destination_sha256"]
        assert v2_result["coded_input_bytes"] == len(v2_revision2.read_bytes())
        assert v2_result["instrument_binding"] == (
            "MATCHED_V2_FORM_AND_RUBRIC")
        assert v2_result["rollup"]["technical"]["TECH_COMPLETED"] == 1
        assert v2_result["rollup"]["technical"]["TECH_BLOCKED"] == 1
        assert v2_result["rollup"]["scientific"]["SCI_CORRECT"] == 1
        assert v2_result["rollup"]["scientific"]["NOT_OBSERVED"] == 11
        assert v2_result["participant_count"] is None
        assert hashlib.sha256(scientific_db.read_bytes()).hexdigest() == db_sha_before
        _assert_no_game_files(db)

    assert hashlib.sha256(scientific_db.read_bytes()).hexdigest() == db_sha_before
    _assert_no_game_files(db)


def test_evaluate_to_fail_closed_before_creating_any_output(tmp_path: Path):
    """Rejected, incomplete and privacy-invalid inputs cannot leave a report."""
    external = _external_directory(tmp_path)
    rc, blank = _protocol("--blank-session")
    assert rc == 0 and len(blank["observations"]) == 12
    rc, rubric = _protocol("--template")
    assert rc == 0 and len(rubric["tasks"]) == 12
    key = {task["task_id"]: task for task in rubric["tasks"]}

    scenarios: dict[str, tuple[dict, str]] = {}
    scenarios["all_missing"] = (blank, "OPERATOR_NO_OBSERVATIONS")
    partial = json.loads(json.dumps(blank))
    partial["observations"][0]["technical"] = "TECH_COMPLETED"
    partial["observations"].pop()
    scenarios["partial"] = (partial, "OPERATOR_SESSION_INCOMPLETE")
    blocked = json.loads(json.dumps(blank))
    for item in blocked["observations"]:
        if item["task_id"] == "OP09":
            item["technical"] = "TECH_BLOCKED"
            item["scientific"] = key["OP09"]["correct_answer_code"]
    scenarios["blocked_with_science"] = (blocked, "OPERATOR_INPUT_INVALID")
    pii = json.loads(json.dumps(blank))
    pii["observations"][0]["technical"] = "TECH_COMPLETED"
    pii["observations"][0]["email"] = "PRIVATE_CANARY@example.invalid"
    scenarios["extra_pii"] = (pii, "OPERATOR_INPUT_INVALID")
    duplicate = json.loads(json.dumps(blank))
    duplicate["observations"][1]["task_id"] = duplicate["observations"][0]["task_id"]
    scenarios["duplicate"] = (duplicate, "OPERATOR_INPUT_INVALID")
    invalid_answer = json.loads(json.dumps(blank))
    invalid_answer["observations"][0]["technical"] = "TECH_COMPLETED"
    invalid_answer["observations"][0]["scientific"] = "A"
    scenarios["participant_a_not_operator_code"] = (
        invalid_answer, "OPERATOR_INPUT_INVALID")

    for name, (body, expected_code) in scenarios.items():
        source = external / f"entrada {name} \u03a9 sint\u00e9tica.json"
        output = external / f"salida {name} \u03a9 no creada.json"
        source.write_bytes(json.dumps(body, ensure_ascii=True).encode("utf-8"))
        assert not output.exists()
        before = source.read_bytes()
        rc, rejected, raw = _protocol_with_raw("--evaluate-to", source, output)
        assert rc == 1
        assert rejected["status"] == "OPERATOR_REJECTED"
        assert rejected["error_code"] == expected_code
        assert rejected["participant_count"] is None
        assert not output.exists(), f"Rejected case {name} emitted an output"
        assert source.read_bytes() == before
        _assert_no_path_or_people(raw, source, output)
        assert "PRIVATE_CANARY" not in raw


def test_evaluate_to_output_path_security_and_no_overwrite(tmp_path: Path):
    """Valid input must not bypass output destination policy."""
    external = _external_directory(tmp_path)
    rc, rubric = _protocol("--template")
    assert rc == 0 and len(rubric["tasks"]) == 12
    source = external / "entrada v\u00e1lida con espacios \u03a9.json"
    rc, created = _protocol("--new-session", str(source))
    assert rc == 0 and created["status"] == "OPERATOR_SESSION_CREATED"
    _coded_synthetic_fixture(source, rubric)
    before_source = source.read_bytes()
    existing = external / "resultado existente \u03a9.json"
    existing.write_bytes(b"DO_NOT_OVERWRITE_SYNTHETIC_SENTINEL")
    missing_parent = external / "inexistente" / "sin salida.json"
    repo_target = ROOT / "__operator_export_must_never_create__.json"
    assert not repo_target.exists()
    targets = [
        ("existing", existing),
        ("same_input", source),
        ("missing_parent", missing_parent),
        ("repository", repo_target),
        ("directory", external),
    ]
    original_children = set(external.iterdir())
    for label, target in targets:
        rc, error, raw = _protocol_with_raw("--evaluate-to", source, target)
        assert rc != 0, f"{label} unexpectedly exported"
        assert error["status"] == "OPERATOR_REJECTED"
        assert error["error_code"].startswith("OPERATOR_")
        assert error["participant_count"] is None
        _assert_no_path_or_people(raw, source, target)
        assert source.read_bytes() == before_source
        assert existing.read_bytes() == b"DO_NOT_OVERWRITE_SYNTHETIC_SENTINEL"
        assert not missing_parent.parent.exists()
        assert not repo_target.exists()
        assert set(external.iterdir()) == original_children

    # NTFS Alternate Data Streams must never be used as a stealth report.
    # On non-Windows platforms this branch does not claim an ADS check.
    if os.name == "nt":
        anchor = external / "externo_ads_synthetic.txt"
        anchor.write_bytes(b"SYNTHETIC_BASE_UNCHANGED")
        ads = Path(str(anchor) + ":operator_export")
        assert not os.path.lexists(ads)
        rc, error, raw = _protocol_with_raw("--evaluate-to", source, ads)
        assert rc != 0
        assert error["status"] == "OPERATOR_REJECTED"
        assert error["error_code"] == "OPERATOR_OUTPUT_PATH_INVALID"
        assert anchor.read_bytes() == b"SYNTHETIC_BASE_UNCHANGED"
        assert not os.path.lexists(ads)
        _assert_no_path_or_people(raw, source, ads)
