"""R18: fail-closed continuation of a research programme after local R5 stops.

This module schedules *candidate work*, never certifies data, increments an
AB-H ledger, opens an original, calls a network service or grants permission.
STOP_R5 blocks empirical analysis of the affected source, not independent
documentary review, ontology work or offline synthetic QA on another route.
"""
from __future__ import annotations

import json
from pathlib import Path


SCHEMA = "pfl.research_continuation.v1"
TRACKS = frozenset({"AB_R_CANDIDATE", "AB_P_CANDIDATE", "NONCYCLE_RESEARCH"})
STATES = frozenset({"QUEUED", "BLOCKED_R5", "PARKED", "COMPLETED_NONCYCLE"})


class ContinuationError(ValueError):
    """Invalid or unsafe candidate continuation programme."""


def _pairs_unique(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ContinuationError("DUPLICATE_PROGRAM_KEY")
        result[key] = value
    return result


def load_program(path: str | Path) -> dict:
    """Read an explicit local, synthetic/documentary-only work queue."""
    raw = Path(path).read_bytes()
    if len(raw) > 120_000:
        raise ContinuationError("PROGRAM_TOO_LARGE")
    try:
        doc = json.loads(raw, object_pairs_hook=_pairs_unique)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContinuationError("INVALID_PROGRAM_JSON") from exc
    return validate_program(doc)


def validate_program(program: object) -> dict:
    if type(program) is not dict or set(program) != {
        "schema", "grant", "r5_status", "candidates", "policy"
    } or program["schema"] != SCHEMA:
        raise ContinuationError("INVALID_CONTINUATION_SCHEMA")
    grant = program["grant"]
    if (type(grant) is not dict or set(grant) != {
            "authorized", "valid", "invalid", "planning_only", "available"
        } or any(type(x) is not int or x < 0 for x in grant.values())
        or grant["authorized"] != 20
        or grant["valid"] + grant["invalid"] + grant["planning_only"] + grant["available"] != 20):
        raise ContinuationError("BUDGET_INTEGRITY_FAILURE")
    if program["r5_status"] != "STOP_R5":
        raise ContinuationError("UNAUTHORIZED_GATE_PROMOTION")
    if program["policy"] != "LOCAL_STOP_ROUTE_ONWARD_WITHOUT_AB_PROMOTION":
        raise ContinuationError("UNAUTHORIZED_STOP_POLICY")
    candidates = program["candidates"]
    if type(candidates) is not list or len(candidates) != 20:
        raise ContinuationError("EXACTLY_TWENTY_DISTINCT_CANDIDATES_REQUIRED")
    ids: set[str] = set()
    for n, candidate in enumerate(candidates, 1):
        if type(candidate) is not dict or set(candidate) != {
                "id", "track", "status", "domain", "research_question",
                "required_new_evidence", "falsifier", "stop_reason", "reopen_when"
            }:
            raise ContinuationError("INVALID_CANDIDATE_SCHEMA")
        if candidate["id"] != f"R18-C{n:02}" or candidate["id"] in ids:
            raise ContinuationError("CANDIDATE_IDENTIFIER_INVALID")
        ids.add(candidate["id"])
        if (type(candidate["track"]) is not str
                or type(candidate["status"]) is not str
                or candidate["track"] not in TRACKS or candidate["status"] not in STATES):
            raise ContinuationError("INVALID_CANDIDATE_CLASSIFICATION")
        for key in ("domain", "research_question", "required_new_evidence",
                    "falsifier", "reopen_when"):
            if (type(candidate[key]) is not str or not 12 <= len(candidate[key]) <= 500):
                raise ContinuationError("MISSING_OR_VAGUE_CANDIDATE_CONTRACT")
        if candidate["status"] in {"BLOCKED_R5", "PARKED"}:
            if type(candidate["stop_reason"]) is not str or len(candidate["stop_reason"]) < 12:
                raise ContinuationError("BLOCK_WITHOUT_WRITTEN_REASON")
        elif candidate["stop_reason"] is not None:
            raise ContinuationError("STOP_REASON_ON_ACTIVE_CANDIDATE")
    return program


def reconcile_with_authorization(program: dict, authorization: dict) -> dict:
    """Require live ledger equality; never write the authoritative AB-H grant."""
    p = validate_program(program)
    if type(authorization) is not dict or any(
        type(authorization.get(k)) is not int for k in (
            "authorized", "executed_valid", "invalid", "planning_only", "remaining"
        )
    ):
        raise ContinuationError("MISSING_CANONICAL_AUTHORIZATION_LEDGER")
    canonical = {
        "authorized": authorization["authorized"],
        "valid": authorization["executed_valid"],
        "invalid": authorization["invalid"],
        "planning_only": authorization["planning_only"],
        "available": authorization["remaining"],
    }
    if canonical != p["grant"]:
        raise ContinuationError("NONAUTHORITATIVE_QUEUE_GRANT_DRIFT")
    return continuation_status(p)


def continuation_status(program: dict) -> dict:
    """Never turn STOP into a successful AB cycle or turn QUEUED into DONE."""
    p = validate_program(program)
    by_status = {state: sum(c["status"] == state for c in p["candidates"])
                 for state in sorted(STATES)}
    available = [c for c in p["candidates"] if c["status"] == "QUEUED"]
    return {
        "schema": "pfl.research_continuation_status.v1",
        "local_stop_does_not_stop_other_work": True,
        "empirical_r5_gate": "STOP_R5",
        "grant": dict(p["grant"]),
        "candidate_statuses": by_status,
        "candidates_are_executed_AB_cycles": False,
        "next_candidate": available[0]["id"] if available else None,
        "remaining_candidate_ids": [c["id"] for c in available],
        "rights_to_fetch_originals": False,
        "real_outcomes_authorized": False,
        "scientific_conclusions_from_this_queue": 0,
    }
