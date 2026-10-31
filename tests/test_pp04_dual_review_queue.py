"""Only fabricated candidates: a similarity queue is NEVER an authenticated link."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pp04_dual_review_queue.py"
spec = importlib.util.spec_from_file_location("pp04_dual_review_queue", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def pan(count=198):
    return [{
        "source_local_ordinal_not_official_id": i,
        "first_public_at": None, "actual_approval_outcome": None,
        "IAEN_link": None, "official_crosswalk_id": None,
        "title_pdf_page": 37 + (i % 30),
        "title_first_line_unverified": f"LEY DE ASUNTO TOTALMENTE FICTICIO {i} DE 2024",
    } for i in range(1, count+1)]


def iaen(count=198):
    return [{
        "source_local_ordinal": i, "first_public_at": None,
        "publisher_stable_id_verified": False,
        "policy_outcome_causally_attributed": False,
        "source_listing_heading": "APPROVED_AS_REPORTED" if i % 2 else "PENDING_APPROVAL_UNSPLIT",
        "source_pdf_page": 40 + (i % 20),
        "title_candidate": f"Ley de asunto totalmente ficticio {i} de 2024",
    } for i in range(1, count+1)]


def review(n, decision="SAME_DOCUMENTARY_INITIATIVE", kind="OFFICIAL_EXPLICIT_ITEM_ID",
           digest="a"*64):
    return {
        "reviewer_pseudonym": f"R{n}", "pan_ordinal": 1, "iaen_ordinal": 2,
        "decision": decision, "evidence_kind": kind,
        "pan_page": 37, "iaen_page": 40, "evidence_ref_hash": digest,
    }


def test_exact_matching_strings_remain_unverified_and_unknown():
    items = mod.project_pan(pan())
    rows = mod.project_iaen(iaen())
    proposals = mod.candidates(items, rows, topk=2)
    assert len(proposals) == 198
    assert len(proposals[0]["options_unverified"]) == 2
    assert all(p["decision"] == "UNKNOWN" and p["source_confirmed_crosswalk"] is None
               and p["requires_independent_documentary_adjudication"] for p in proposals)
    assert all(x["authenticated"] is False for p in proposals for x in p["options_unverified"])
    assert all("source_listing_heading" not in p and "outcome" not in p
               for p in proposals)


def test_report_approved_heading_is_not_predictor_or_match_feature():
    rows = iaen()
    original = mod.project_iaen(rows)
    for r in rows:
        r["source_listing_heading"] = (
            "PENDING_APPROVAL_UNSPLIT"
            if r["source_listing_heading"] == "APPROVED_AS_REPORTED"
            else "APPROVED_AS_REPORTED")
    altered = mod.project_iaen(rows)
    assert altered == original


def test_false_crosswalk_in_source_fails_closed():
    source = pan()
    source[0]["IAEN_link"] = "FAKE_PREAPPROVED_LINK"
    with pytest.raises(mod.ReviewGateError, match="PAN_HISTORICAL_LINK"):
        mod.project_pan(source)
    altered = iaen()
    altered[0]["first_public_at"] = "2024-01-01"
    with pytest.raises(mod.ReviewGateError, match="IAEN_ROW"):
        mod.project_iaen(altered)


def test_198_source_local_denominator_is_not_relaxed_to_197():
    with pytest.raises(mod.ReviewGateError, match="PAN_PROVISIONAL_DENOMINATOR"):
        mod.project_pan(pan(count=197))
    with pytest.raises(mod.ReviewGateError, match="IAEN_PLANNED_REVIEW_FRAME"):
        mod.project_iaen(iaen(count=199))


def test_title_normalization_does_not_masquerade_as_authentication():
    assert mod.keytext("Ley Orgánica del Ámbito Público") == "LEY ORGANICA DEL AMBITO PUBLICO"
    with pytest.raises(mod.ReviewGateError, match="REVIEW_TITLE"):
        mod.keytext("")


def test_two_reviewers_with_only_same_title_are_not_sufficient():
    first = review(1, kind="TITLE_SIMILARITY_ONLY")
    second = review(2, kind="TITLE_SIMILARITY_ONLY")
    decision = mod.independent_review_gate((first, second))
    assert decision["status"] == "UNKNOWN_OR_REVIEW_DISAGREEMENT"
    assert decision["authenticated_source_link"] is False
    assert decision["R5"] == "STOP"


def test_two_independent_strong_reviewers_still_only_queue_external_authentication():
    result = mod.independent_review_gate((review(1), review(2)))
    assert result["status"] == "CONCURRING_REVIEW_READY_FOR_EXTERNAL_ORIGINAL_CHECK"
    assert result["authenticated_source_link"] is False
    assert result["AB_scientific_cycles"] == 0


def test_conflicting_independent_evidence_or_same_reviewer_rejected():
    differing_digest = mod.independent_review_gate((review(1), review(2, digest="b"*64)))
    assert differing_digest["status"] == "UNKNOWN_OR_REVIEW_DISAGREEMENT"
    different_claim = mod.independent_review_gate((review(1), review(2, decision="UNKNOWN")))
    assert different_claim["status"] == "UNKNOWN_OR_REVIEW_DISAGREEMENT"
    with pytest.raises(mod.ReviewGateError, match="REVIEWERS_MUST_DIFFER"):
        mod.independent_review_gate((review(1), review(1)))


def test_reject_private_derived_source_hash_drift(tmp_path):
    p = tmp_path / mod.PAN_DERIVED_FILE
    p.write_text(json.dumps(pan()[0]), encoding="utf-8")
    with pytest.raises(mod.ReviewGateError, match="SHA_CHANGED"):
        mod.load_pinned(p, mod.PAN_DERIVED_FILE, mod.PAN_DERIVED_SHA)


def test_cannot_write_derivatives_inside_any_git_checkout(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    dest = repo / "private"
    dest.mkdir()
    with pytest.raises(mod.ReviewGateError, match="INSIDE_GIT_TREE"):
        mod.ensure_outside_git(dest)


def test_duplicate_strings_do_not_promote_a_many_to_one_match():
    p = mod.project_pan(pan())
    r = mod.project_iaen(iaen())
    # Both IAEN candidates have the same visible first line: ambiguity is
    # represented as multiple REVIEW_SUGGESTION_ONLY options.
    altered = list(r)
    altered[1] = {**altered[1], "text": altered[0]["text"], "key": altered[0]["key"]}
    proposals = mod.candidates(p, tuple(altered), topk=3)
    opts = proposals[0]["options_unverified"]
    assert opts[0]["string_similarity_not_probability"] == opts[1]["string_similarity_not_probability"]
    assert not opts[0]["authenticated"] and not opts[1]["authenticated"]
