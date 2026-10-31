"""AB10 P02: synthetic double-review assignment integrity (NOT authentication).

SYN actor IDs are fixture-only. No personal information, source originals,
cryptographic proof of a person's identity, or real legal linkage is handled.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re


class ReviewAssignmentError(ValueError):
    pass


SHA = re.compile(r"^[0-9a-f]{64}$")
SYN = re.compile(r"^SYN:[A-Z][A-Z0-9_-]{1,40}$")
ASSIGNMENT_SCHEMA = "pfl.ab10.synthetic_review_assignment.v1"
RESPONSE_SCHEMA = "pfl.ab10.synthetic_review_response.v1"
DECISIONS = {"SAME", "DIFFERENT", "UNKNOWN"}


def _exact(obj: object, fields: set[str]) -> dict:
    if type(obj) is not dict or set(obj) != fields:
        raise ReviewAssignmentError("SYN_REVIEW_UNEXPECTED_OR_MISSING_FIELDS")
    return obj


def _id(value: object) -> bool:
    return type(value) is str and SYN.fullmatch(value) is not None


def _hash(value: object) -> bool:
    return type(value) is str and SHA.fullmatch(value) is not None


def validate_assignment(data: object) -> dict:
    obj = _exact(data, {"schema", "pair", "source", "slots",
                        "user_rights_verified", "authenticated_crosswalk"})
    if (obj["schema"] != ASSIGNMENT_SCHEMA
            or obj["user_rights_verified"] is not False
            or obj["authenticated_crosswalk"] is not False):
        raise ReviewAssignmentError("SYN_REVIEW_REAL_SOURCE_PROMOTION")
    pair = _exact(obj["pair"], {"pan_id", "report_id"})
    source = _exact(obj["source"], {"pan_sha256", "report_sha256", "revision"})
    if (not all(_id(pair[x]) for x in pair)
            or not all(_hash(source[x]) for x in ("pan_sha256", "report_sha256"))
            or not _id(source["revision"])):
        raise ReviewAssignmentError("SYN_REVIEW_BAD_SOURCE_BINDING")
    slots = obj["slots"]
    if type(slots) is not list or len(slots) != 2:
        raise ReviewAssignmentError("SYN_REVIEW_EXACTLY_TWO_SLOTS")
    bound_actors = []
    for index, slot in enumerate(slots):
        _exact(slot, {"slot_id", "actor_id", "assigned_pan_id", "assigned_report_id"})
        if (slot["slot_id"] != f"SLOT_{index + 1}"
                or not _id(slot["actor_id"])
                or slot["assigned_pan_id"] != pair["pan_id"]
                or slot["assigned_report_id"] != pair["report_id"]):
            raise ReviewAssignmentError("SYN_REVIEW_SLOT_OR_PAIR_NOT_ASSIGNED")
        bound_actors.append(slot["actor_id"])
    if len(set(bound_actors)) != 2:
        raise ReviewAssignmentError("SYN_REVIEW_SAME_ACTOR_IN_TWO_SLOTS")
    return obj


def _response(obj: object) -> dict:
    response = _exact(obj, {"schema", "slot_id", "actor_id", "pan_id",
                             "report_id", "source_revision",
                             "pan_sha256", "report_sha256",
                             "decision", "evidence_sha256"})
    if (response["schema"] != RESPONSE_SCHEMA
            or response["slot_id"] not in ("SLOT_1", "SLOT_2")
            or not _id(response["actor_id"])
            or not _id(response["pan_id"])
            or not _id(response["report_id"])
            or not _id(response["source_revision"])
            or response["decision"] not in DECISIONS
            or not all(_hash(response[x]) for x in (
                "pan_sha256", "report_sha256", "evidence_sha256"))):
        raise ReviewAssignmentError("SYN_REVIEW_UNTRUSTED_RESPONSE")
    return response


def adjudicate(assignment: object, submissions: object) -> dict:
    """Two sealed responses; never reveal a result before both are valid.

    This verifies caller-declared actor assignments. A hostile caller able to
    alter both manifest and responses can spoof actors; it is NOT authN/authZ.
    """
    manifest = validate_assignment(assignment)
    if type(submissions) not in (list, tuple) or len(submissions) != 2:
        raise ReviewAssignmentError("SYN_REVIEW_TWO_RESPONSES_REQUIRED")
    responses = [_response(s) for s in submissions]
    if {x["slot_id"] for x in responses} != {"SLOT_1", "SLOT_2"}:
        raise ReviewAssignmentError("SYN_REVIEW_DUPLICATE_OR_MISSING_SLOT")
    source = manifest["source"]
    pair = manifest["pair"]
    allowed = {x["slot_id"]: x for x in manifest["slots"]}
    for r in responses:
        if r["actor_id"] != allowed[r["slot_id"]]["actor_id"]:
            raise ReviewAssignmentError("SYN_REVIEW_ACTOR_UNASSIGNED")
        if r["pan_id"] != pair["pan_id"] or r["report_id"] != pair["report_id"]:
            raise ReviewAssignmentError("SYN_REVIEW_PAIR_NOT_ASSIGNED")
        for x in ("pan_sha256", "report_sha256"):
            if r[x] != source[x]:
                raise ReviewAssignmentError("SYN_REVIEW_SOURCE_EDITION_MISMATCH")
        if r["source_revision"] != source["revision"]:
            raise ReviewAssignmentError("SYN_REVIEW_REVISION_MISMATCH")
    ordered = sorted(responses, key=lambda x: x["slot_id"])
    state = ("NEEDS_OFFICIAL_ORIGINAL_CHECK"
             if (all(r["decision"] == "SAME" for r in ordered)
                 and ordered[0]["evidence_sha256"] == ordered[1]["evidence_sha256"])
             else "UNKNOWN_OR_REVIEW_DISAGREEMENT")
    receipt_input = {
        "assignment": manifest, "responses": ordered, "state": state,
    }
    digest = sha256(json.dumps(receipt_input, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "schema": "pfl.ab10.synthetic_two_review_receipt.v1",
        "source_revision": source["revision"],
        "pan_id": pair["pan_id"],
        "report_id": pair["report_id"],
        "receipt_sha256": digest,
        "review_state": state,
        "verified_reviewer_independence": False,
        "authenticated_legal_link": False,
        "rights_verified": False,
        "real_source_data_read": False,
        "scientific_cycle_executed": False,
        "R5": "STOP",
    }
