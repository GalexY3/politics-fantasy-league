"""AB10 P02: synthetic reviewer role/assignment adversarial fixtures."""
from copy import deepcopy

import pytest

from politics_fantasy.synthetic_review_assignment import (
    ASSIGNMENT_SCHEMA, RESPONSE_SCHEMA,
    ReviewAssignmentError, adjudicate, validate_assignment,
)


def manifest():
    return {
        "schema": ASSIGNMENT_SCHEMA,
        "pair": {"pan_id": "SYN:PLAN1", "report_id": "SYN:IAEN1"},
        "source": {"pan_sha256": "a" * 64, "report_sha256": "b" * 64,
                   "revision": "SYN:REV1"},
        "slots": [
            {"slot_id": "SLOT_1", "actor_id": "SYN:ACTOR1",
             "assigned_pan_id": "SYN:PLAN1", "assigned_report_id": "SYN:IAEN1"},
            {"slot_id": "SLOT_2", "actor_id": "SYN:ACTOR2",
             "assigned_pan_id": "SYN:PLAN1", "assigned_report_id": "SYN:IAEN1"},
        ],
        "user_rights_verified": False,
        "authenticated_crosswalk": False,
    }


def response(slot, decision="SAME"):
    return {
        "schema": RESPONSE_SCHEMA,
        "slot_id": f"SLOT_{slot}", "actor_id": f"SYN:ACTOR{slot}",
        "pan_id": "SYN:PLAN1", "report_id": "SYN:IAEN1",
        "source_revision": "SYN:REV1", "pan_sha256": "a" * 64,
        "report_sha256": "b" * 64, "decision": decision,
        "evidence_sha256": "c" * 64,
    }


def test_two_distinct_declared_slots_agree_but_never_authenticate_policy_link():
    result = adjudicate(manifest(), [response(1), response(2)])
    assert result["review_state"] == "NEEDS_OFFICIAL_ORIGINAL_CHECK"
    assert result["authenticated_legal_link"] is False
    assert result["verified_reviewer_independence"] is False
    assert result["rights_verified"] is False
    assert result["R5"] == "STOP"
    assert result["receipt_sha256"] == adjudicate(manifest(), [response(2), response(1)])["receipt_sha256"]


def test_attack_same_actor_uses_two_pseudonyms_and_fails():
    bad = manifest()
    bad["slots"][1]["actor_id"] = "SYN:ACTOR1"
    with pytest.raises(ReviewAssignmentError, match="SAME_ACTOR_IN_TWO_SLOTS"):
        adjudicate(bad, [response(1), response(2)])


def test_attack_pair_not_assigned_to_actor_fails():
    bad = response(2)
    bad["pan_id"] = "SYN:ANOTHERPLAN"
    with pytest.raises(ReviewAssignmentError, match="PAIR_NOT_ASSIGNED"):
        adjudicate(manifest(), [response(1), bad])


def test_attack_different_source_sha_fails():
    bad = response(2)
    bad["report_sha256"] = "d" * 64
    with pytest.raises(ReviewAssignmentError, match="SOURCE_EDITION_MISMATCH"):
        adjudicate(manifest(), [response(1), bad])


def test_attack_disagreement_never_yields_source_confirmed_link():
    result = adjudicate(manifest(), [response(1), response(2, decision="DIFFERENT")])
    assert result["review_state"] == "UNKNOWN_OR_REVIEW_DISAGREEMENT"
    assert result["authenticated_legal_link"] is False


def test_attack_duplicate_submission_for_same_slot_is_rejected():
    with pytest.raises(ReviewAssignmentError, match="DUPLICATE_OR_MISSING_SLOT"):
        adjudicate(manifest(), [response(1), response(1)])


def test_control_unknown_is_not_a_fabricated_negative_or_failure():
    result = adjudicate(manifest(), [response(1, "UNKNOWN"), response(2, "UNKNOWN")])
    assert result["review_state"] == "UNKNOWN_OR_REVIEW_DISAGREEMENT"


def test_control_two_distinct_pan_items_can_reference_same_proposed_report():
    left = adjudicate(manifest(), [response(1), response(2)])
    other = manifest()
    other["pair"]["pan_id"] = "SYN:PLAN2"
    for x in other["slots"]:
        x["assigned_pan_id"] = "SYN:PLAN2"
    votes = [response(1), response(2)]
    for vote in votes:
        vote["pan_id"] = "SYN:PLAN2"
    right = adjudicate(other, votes)
    assert left["report_id"] == right["report_id"]
    assert left["receipt_sha256"] != right["receipt_sha256"]
    assert right["authenticated_legal_link"] is False


def test_extra_fields_and_unverified_rights_cannot_be_promoted():
    for field, value in (("user_rights_verified", True),
                         ("authenticated_crosswalk", True)):
        bad = manifest()
        bad[field] = value
        with pytest.raises(ReviewAssignmentError, match="REAL_SOURCE_PROMOTION"):
            validate_assignment(bad)
    bad = response(1)
    bad["publisher_identity_confirmed"] = True
    with pytest.raises(ReviewAssignmentError, match="UNEXPECTED_OR_MISSING_FIELDS"):
        adjudicate(manifest(), [bad, response(2)])


def test_revision_mismatch_and_unassigned_actor_are_rejected():
    wrong = response(2)
    wrong["source_revision"] = "SYN:REV2"
    with pytest.raises(ReviewAssignmentError, match="REVISION_MISMATCH"):
        adjudicate(manifest(), [response(1), wrong])
    bad_actor = response(2)
    bad_actor["actor_id"] = "SYN:ACTOR3"
    with pytest.raises(ReviewAssignmentError, match="ACTOR_UNASSIGNED"):
        adjudicate(manifest(), [response(1), bad_actor])


def test_baseline_existing_pp04c_only_checks_pseudonyms_not_actor_assignment():
    from scripts.pp04_dual_review_queue import independent_review_gate
    def legacy(n):
        return {
            "reviewer_pseudonym": f"R{n}", "pan_ordinal": 1, "iaen_ordinal": 1,
            "decision": "SAME_DOCUMENTARY_INITIATIVE",
            "evidence_kind": "OFFICIAL_EXPLICIT_ITEM_ID",
            "pan_page": 40, "iaen_page": 51, "evidence_ref_hash": "c" * 64,
        }
    old = independent_review_gate((legacy(1), legacy(2)))
    assert old["status"] == "CONCURRING_REVIEW_READY_FOR_EXTERNAL_ORIGINAL_CHECK"
    assert old["authenticated_source_link"] is False
    bad = manifest()
    bad["slots"][1]["actor_id"] = "SYN:ACTOR1"
    with pytest.raises(ReviewAssignmentError, match="SAME_ACTOR"):
        adjudicate(bad, [response(1), response(2)])
