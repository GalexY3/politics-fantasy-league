"""R18 governance instrumentation, not AB-R/P or observed political outcomes."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from politics_fantasy.research_continuation import (
    ContinuationError, continuation_status, load_program, validate_program,
    reconcile_with_authorization,
)


PROGRAM = (Path(__file__).resolve().parents[1]
           / "research/PFL_SYSTEM20_20261031/R18_CONTINUATION_QUEUE.json")


def test_twenty_independent_candidate_routes_are_not_spent_cycles():
    program = load_program(PROGRAM)
    report = continuation_status(program)
    assert len(program["candidates"]) == 20
    assert report["grant"] == dict(authorized=20, valid=0, invalid=0,
                                   planning_only=0, available=20)
    assert report["empirical_r5_gate"] == "STOP_R5"
    assert not report["candidates_are_executed_AB_cycles"]
    assert not report["rights_to_fetch_originals"]
    assert not report["real_outcomes_authorized"]
    assert report["candidate_statuses"]["BLOCKED_R5"] == 1
    assert report["candidate_statuses"]["PARKED"] == 9
    assert report["candidate_statuses"]["QUEUED"] == 6
    assert report["candidate_statuses"]["COMPLETED_NONCYCLE"] == 4
    assert report["next_candidate"] == "R18-C15"


def test_status_never_changes_the_ledger_or_eligible_work():
    program = load_program(PROGRAM)
    before = copy.deepcopy(program)
    assert continuation_status(program) == continuation_status(program)
    assert program == before


def test_queue_fails_closed_if_real_authorization_ledger_changes():
    program = load_program(PROGRAM)
    auth_file = (Path(__file__).resolve().parents[1]
                 / "research/PFL_SYSTEM20_20261031/AUTHORIZATION.json")
    canonical = json.loads(auth_file.read_text(encoding="utf-8"))
    report = reconcile_with_authorization(program, canonical)
    assert report["grant"]["available"] == 20
    shifted = dict(canonical, executed_valid=1, remaining=19)
    with pytest.raises(ContinuationError, match="NONAUTHORITATIVE_QUEUE_GRANT_DRIFT"):
        reconcile_with_authorization(program, shifted)
    with pytest.raises(ContinuationError, match="MISSING_CANONICAL_AUTHORIZATION_LEDGER"):
        reconcile_with_authorization(program, {"authorized": 20})


def test_blocked_stops_are_local_and_queued_product_or_lab_continues():
    program = load_program(PROGRAM)
    report = continuation_status(program)
    assert "R18-C01" not in report["remaining_candidate_ids"]
    assert "R18-C02" not in report["remaining_candidate_ids"]
    assert {"R18-C15", "R18-C19"}.issubset(
        report["remaining_candidate_ids"])
    assert {"R18-C03", "R18-C04", "R18-C13", "R18-C14"}.isdisjoint(report["remaining_candidate_ids"])
    assert report["local_stop_does_not_stop_other_work"] is True


@pytest.mark.parametrize("mutation, expected", [
    (lambda d: d.update(r5_status="GO"), "UNAUTHORIZED_GATE_PROMOTION"),
    (lambda d: d["grant"].update(valid=1), "BUDGET_INTEGRITY_FAILURE"),
    (lambda d: d["grant"].update(available=19), "BUDGET_INTEGRITY_FAILURE"),
    (lambda d: d["candidates"].pop(), "EXACTLY_TWENTY_DISTINCT_CANDIDATES_REQUIRED"),
    (lambda d: d["candidates"][1].update(id="R18-C01"), "CANDIDATE_IDENTIFIER_INVALID"),
    (lambda d: d["candidates"][0].update(stop_reason=None), "BLOCK_WITHOUT_WRITTEN_REASON"),
    (lambda d: d["candidates"][3].update(stop_reason="already done"),
     "STOP_REASON_ON_ACTIVE_CANDIDATE"),
    (lambda d: d["candidates"][10].update(track="AB_R_VALIDATED"),
     "INVALID_CANDIDATE_CLASSIFICATION"),
    (lambda d: d["candidates"][10].update(status=[]),
     "INVALID_CANDIDATE_CLASSIFICATION"),
    (lambda d: d["candidates"][0].update(falsifier="none"),
     "MISSING_OR_VAGUE_CANDIDATE_CONTRACT"),
    (lambda d: d.update(extra="hidden"), "INVALID_CONTINUATION_SCHEMA"),
])
def test_adversarial_evidence_and_cycle_misclassification(mutation, expected):
    program = copy.deepcopy(load_program(PROGRAM))
    mutation(program)
    with pytest.raises(ContinuationError, match=expected):
        validate_program(program)


def test_duplicate_json_key_fails_closed_even_when_python_dict_would_hide_it(tmp_path):
    src = PROGRAM.read_text(encoding="utf-8")
    tampered = src.replace('"r5_status": "STOP_R5",',
                           '"r5_status": "GO", "r5_status": "STOP_R5",', 1)
    path = tmp_path / "untrusted.json"
    path.write_text(tampered, encoding="utf-8")
    with pytest.raises(ContinuationError, match="DUPLICATE_PROGRAM_KEY"):
        load_program(path)


def test_noncyle_closure_does_not_autocharge_abh_grant():
    program = copy.deepcopy(load_program(PROGRAM))
    program["candidates"][14]["status"] = "COMPLETED_NONCYCLE"
    report = continuation_status(program)
    assert report["grant"]["available"] == 20
    assert report["grant"]["valid"] == 0
    assert report["next_candidate"] == "R18-C16"
    assert report["candidate_statuses"]["COMPLETED_NONCYCLE"] == 5


def test_all_routes_locally_blocked_never_coerce_an_abh_cycle():
    program = copy.deepcopy(load_program(PROGRAM))
    for candidate in program["candidates"]:
        candidate.update(status="PARKED", stop_reason="No new admissible signed evidence at this gate")
    report = continuation_status(program)
    assert report["next_candidate"] is None
    assert not report["remaining_candidate_ids"]
    assert report["grant"]["available"] == 20
