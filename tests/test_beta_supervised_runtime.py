"""Integrated synthetic *operator-harness* test; no human participants.

Reuse the existing bounded real-process science-only fixture and HTTP client.
All observations below are artificial closed-code data, not a human study.
No accounts, private originals, browser, external network or public hosting.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import parse_qsl, urlencode, urlsplit

from run_demo import GUEST_QUERY_KEYS, resume_guest_query
from test_beta_live_science_doctor_runtime import (
    CANONICAL_PAIRS,
    CANONICAL_QUERY,
    ENV,
    ROOT,
    _require_synthetic_stop,
    _source_digests,
    run_doctor,
    science_server,
)
from test_beta_science_only import _request


PROTOCOL = ROOT / "scripts" / "beta_science_operator_protocol.py"
EXPECTED_OPERATOR_VIEWS = (
    "sources", "compare", "chain", "chronicle",
    "episodes", "admission", "intake", "quality",
)


def _protocol(*args: str) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, "-B", str(PROTOCOL), *map(str, args)],
        cwd=ROOT, env=ENV, stdin=subprocess.DEVNULL,
        capture_output=True, text=True, encoding="utf-8",
        timeout=12, check=False,
    )
    assert not result.stderr, "The operator CLI must not emit a traceback or paths"
    assert len(result.stdout) < 35_000
    assert result.stdout.count("\n") == 1
    return result.returncode, json.loads(result.stdout)


def _verify_live_public_cuts(port: int) -> dict[str, str]:
    """Independently recompute exact UTF-8 SHA and canonical snapshot scope."""
    result = {}
    filters = dict(CANONICAL_PAIRS)
    for cut in ("early", "late"):
        route = "/api/scientific-registry?" + urlencode({
            "cut": cut,
            "valid_at": filters["valid_at"],
            "family": filters["family"],
            "published_until": filters["published_until"],
        })
        status, data = _request(port, route)
        assert status == 200
        assert data["cut"] == cut
        assert data["family"] == "CHAIN"
        assert data["valid_at"] == "2026-10-10"
        assert data["published_until"] == "2026-09-19T12:00:00Z"
        assert data["R5"] == "STOP_R5"
        assert data["release_gates_passed"] == 0
        assert data["scientific_ab_cycles"] == 0
        assert data["real_source_ingestion_allowed"] is False
        registry = data["registry"]
        assert registry["source_bytes_exposed"] is False
        assert registry["private_source_ids_exposed"] is False
        assert registry["visible_distribution_count"] == len(registry["distributions"]) == 1
        receipt = data["snapshot_receipt"]
        actual_bytes = receipt["canonical_json"].encode("utf-8")
        assert len(actual_bytes) == receipt["bytes"]
        sha = hashlib.sha256(actual_bytes).hexdigest()
        assert sha == receipt["sha256"] == data["snapshot_receipt_sha256"]
        expected_scope = {
            "schema": "pfl.synthetic_scientific_registry_snapshot.v1",
            "cut": cut, "as_of": data["as_of"],
            "valid_at": data["valid_at"], "family": data["family"],
            "published_until": data["published_until"],
            "distributions": registry["distributions"],
            "snapshot": data["snapshot"],
        }
        assert json.loads(actual_bytes) == expected_scope
        assert actual_bytes == json.dumps(
            expected_scope, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
        result[cut] = sha
    return result


def _assert_guest_runtime(port: int) -> dict[str, str]:
    code, readiness = _request(port, "/api/beta-readiness")
    assert code == 200 and readiness["schema"] == "pfl.beta_readiness.v1"
    assert readiness["ok"] is True
    assert readiness["local_runtime"]["scope"] == "LOOPBACK_SYNTHETIC_SCIENCE_ONLY"
    assert readiness["local_runtime"]["full_user_journey_attested"] is False
    assert readiness["scientific_admission"]["r5_status"] == "STOP_R5"
    assert readiness["public_release"]["eligible"] is False

    for cut in ("early", "late"):
        code, lab = _request(port, f"/api/scientific-integration-lab?cut={cut}&scenario=baseline")
        assert code == 200 and lab["schema"] == "pfl.synthetic_scientific_integration_lab.v1"
        assert lab["cut"] == cut and lab["R5"] == "STOP_R5"
        assert lab["scientific_AB_cycles"] == lab["release_gates_passed"] == 0
        assert lab["real_corpus_ingestion_allowed"] is False
        sets = lab["warehouse"]["b0_b3_witness_sets"]["sets_by_knowledge_cut"][cut]["sets"]
        assert len(sets) == 20
        assert len({entry["case"] for entry in sets}) == 20
    assert _request(port, "/api/scientific-registry?cut=bogus")[0] == 400
    for forbidden in ("/api/register", "/api/login", "/api/scientific-registry"):
        status, body = _request(port, forbidden, method="POST", body=b"{}")
        assert status == 404 and body["error"] == "SCIENCE_ONLY_WRITE_UNAVAILABLE"
    return _verify_live_public_cuts(port)


def _no_accounts_or_game_db(db: Path) -> None:
    assert not db.exists(), "science-only must not create a Fantasy game DB"
    assert not (db.parent / "accounts.sqlite3").exists()
    assert not (db.parent / "accounts").exists()


def test_supervised_synthetic_runtime_two_processes_and_operator_contract(tmp_path):
    db = tmp_path / "operator-synthetic" / "unused-fantasy.sqlite3"
    registry_db = db.parent / "scientific_registry_synthetic.sqlite3"
    assert not db.exists()
    assert PROTOCOL.is_file()

    # CLI is read-only. These task definitions are a blank instrument, NOT
    # answers or evidence that a participant performed a technical task.
    code, self_check = _protocol("--self-check")
    assert code == 0 and self_check["status"] == "OPERATOR_INSTRUMENT_VALID"
    assert self_check["participants_observed"] is False
    assert self_check["participant_count"] is None
    code, template = _protocol("--template")
    assert code == 0 and template["status"] == "OPERATOR_TEMPLATE_ONLY"
    code, sheet = _protocol("--participant-sheet")
    assert code == 0 and sheet["schema"] == "pfl.beta_science_operator_participant_sheet.v1"
    specs = template["tasks"]
    assert len(specs) == len(sheet["tasks"]) == 12
    code, blank_session = _protocol("--blank-session")
    assert code == 0
    assert set(blank_session) == {"schema", "observations"}
    assert blank_session["schema"] == "pfl.beta_science_operator_observations.v1"
    assert [item["task_id"] for item in blank_session["observations"]] == [
        item["task_id"] for item in specs
    ]
    assert all(
        item["technical"] == item["scientific"] == item["usability"] == "NOT_OBSERVED"
        for item in blank_session["observations"]
    )
    for rubric, blank in zip(specs, sheet["tasks"], strict=True):
        assert rubric["task_id"] == blank["task_id"]
        assert set(blank) == {
            "task_id", "operator_action", "scientific_question", "scientific_options",
        }
        assert rubric["correct_answer_code"] not in json.dumps(blank)
        assert "scientific_explanation" not in blank
        assert [choice["code"] for choice in blank["scientific_options"]] == ["A", "B"]
        assert "participant_option_to_scientific_code" not in blank
    correct_labels = [
        next(label for label, code in rubric["participant_option_to_scientific_code"].items()
             if code == rubric["correct_answer_code"])
        for rubric in specs
    ]
    assert correct_labels.count("A") == correct_labels.count("B") == 6
    machine_ids = {machine for task in specs for machine in task["technical_task_ids"]}
    assert machine_ids == {
        "LAB_B0_B3", "LAB_S3_TEMPORAL", "LAB_S7_20",
        "LAB_S8_DESCRIPTORS", "S9_EIGHT_TABS", "S9_FAMILY_SCOPE",
        "S9_TEMPORAL_COMPARE", "S9_SINGLE_EXPORT_OFFLINE",
        "S9_PAIR_EXPORT_OFFLINE", "RESTART_DOCTOR_GUEST_LINK",
    }

    with science_server(db) as first:
        assert first.port is not None and first.origin is not None
        old_origin, old_port = first.origin, first.port
        old_bookmark = old_origin + "/?" + CANONICAL_QUERY
        assert tuple(parse_qsl(urlsplit(old_bookmark).query)) == CANONICAL_PAIRS
        digests_before = _assert_guest_runtime(old_port)
        code, diagnosis = run_doctor(
            old_origin, guest_query=old_bookmark, emit_verified_guest_url=True,
        )
        assert code == 0 and diagnosis["status"] == "PASS"
        assert diagnosis["verified_guest_url"] == old_bookmark
        _require_synthetic_stop(diagnosis)
        assert _source_digests(diagnosis) == (
            digests_before["early"], digests_before["late"],
        )
        assert registry_db.is_file()
        sqlite_before = hashlib.sha256(registry_db.read_bytes()).hexdigest()
        _no_accounts_or_game_db(db)

    # A bookmarked URL is a selection recipe, never a liveness certificate.
    code, dead = run_doctor(
        old_origin, guest_query=old_bookmark, emit_verified_guest_url=True,
    )
    assert code != 0 and dead["status"] == "FAIL"
    assert dead["error_code"] == "SERVER_UNAVAILABLE"
    assert "verified_guest_url" not in dead

    with science_server(db, resume=old_bookmark) as second:
        assert second.port is not None and second.origin is not None
        assert second.port != old_port, "An actual new bound port must be observed"
        digests_after = _assert_guest_runtime(second.port)
        code, rebound = run_doctor(
            second.origin, guest_query=old_bookmark, emit_verified_guest_url=True,
        )
        assert code == 0 and rebound["status"] == "PASS"
        _require_synthetic_stop(rebound)
        assert digests_after == digests_before
        assert _source_digests(rebound) == (
            digests_after["early"], digests_after["late"],
        )
        assert rebound["verified_guest_url"] == second.resumed_url
        current_link = urlsplit(rebound["verified_guest_url"])
        assert current_link.scheme == "http"
        assert current_link.netloc == f"127.0.0.1:{second.port}"
        assert current_link.path == "/" and current_link.fragment == ""
        assert tuple(parse_qsl(current_link.query)) == CANONICAL_PAIRS
        assert tuple(dict(CANONICAL_PAIRS)) == (
            "pfl_guest", "cut", "valid_at", "family",
            "published_until", "scenario", "view",
        )
        assert tuple(GUEST_QUERY_KEYS) == tuple(dict(CANONICAL_PAIRS))
        # Authoritative launcher validates each of the eight closed tab
        # selectors. Native clicks are separately covered by the existing
        # S9 Chrome test; this test does NOT claim to have run Chrome.
        for view in EXPECTED_OPERATOR_VIEWS:
            pairs = tuple((key, view if key == "view" else value)
                          for key, value in CANONICAL_PAIRS)
            recipe = urlencode(pairs)
            assert resume_guest_query("?" + recipe) == recipe
            assert tuple(parse_qsl(recipe)) == pairs
        assert hashlib.sha256(registry_db.read_bytes()).hexdigest() == sqlite_before
        _no_accounts_or_game_db(db)

    # The operative Windows-safe creation path writes UTF-8 once outside Git,
    # rather than relying on PowerShell redirection (which can write UTF-16LE).
    coded = tmp_path / "HARNESS_SYNTHETIC_NOT_HUMAN_observations.json"
    created_rc, created = _protocol("--new-session", str(coded))
    assert created_rc == 0 and created["status"] == "OPERATOR_SESSION_CREATED"
    assert created["participants_observed"] is False
    assert "path" not in created and "participant_id" not in created
    raw = coded.read_bytes()
    assert raw and not raw.startswith(b"\xff\xfe")
    assert json.loads(raw) == blank_session
    empty_rc, empty = _protocol("--evaluate", str(coded))
    assert empty_rc != 0 and empty["status"] == "OPERATOR_REJECTED"
    assert empty["error_code"] == "OPERATOR_NO_OBSERVATIONS"
    repeat_rc, repeat = _protocol("--new-session", str(coded))
    assert repeat_rc != 0 and repeat["error_code"] == "OPERATOR_SESSION_EXISTS"
    assert coded.read_bytes() == raw

    # All entries below are deliberately fabricated by the test harness.
    # Unobserved UX/scientific answers are NEVER imputed as human responses.
    synthetic_input = json.loads(raw)
    for item in synthetic_input["observations"]:
        if item["task_id"] == "OP11":
            item["technical"] = "TECH_COMPLETED"
        elif item["task_id"] == "OP09":
            item["technical"] = "TECH_BLOCKED"
    coded.write_text(json.dumps(synthetic_input, ensure_ascii=True), encoding="utf-8")
    code, evaluated = _protocol("--evaluate", str(coded))
    assert code == 0 and evaluated["status"] == "OPERATOR_EVALUATION_COMPLETE"
    assert evaluated["participant_count"] is None
    assert evaluated["participant_identity_collected"] is False
    assert evaluated["R5"] == "STOP_R5"
    assert evaluated["gate_eligibility"] == "OPERATOR_NOT_ASSESSED"
    assert evaluated["tasks_defined"] == len(specs) == len(evaluated["tasks"])
    assert evaluated["tasks_with_any_coded_observation"] == 2
    assert evaluated["rollup"]["technical"]["TECH_COMPLETED"] == 1
    assert evaluated["rollup"]["technical"]["TECH_BLOCKED"] == 1
    assert evaluated["rollup"]["technical"]["NOT_OBSERVED"] == len(specs) - 2
    assert evaluated["rollup"]["scientific"]["NOT_OBSERVED"] == len(specs)
    assert evaluated["rollup"]["usability"]["NOT_OBSERVED"] == len(specs)

    # Fault injection: a TECH_BLOCKED task cannot carry a purported scientific
    # answer even when its closed code is syntactically valid.
    blocked = next(item for item in synthetic_input["observations"]
                   if item["task_id"] == "OP09")
    blocked["scientific"] = next(task for task in specs
                                 if task["task_id"] == "OP09")["scientific_options"][0]["code"]
    coded.write_text(json.dumps(synthetic_input, ensure_ascii=True), encoding="utf-8")
    code, rejected = _protocol("--evaluate", str(coded))
    assert code != 0
    assert rejected["status"] == "OPERATOR_REJECTED"
    assert rejected["error_code"] == "OPERATOR_INPUT_INVALID"
    assert rejected["participant_count"] is None
    _no_accounts_or_game_db(db)
    assert hashlib.sha256(registry_db.read_bytes()).hexdigest() == sqlite_before
