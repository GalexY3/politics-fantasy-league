"""Synthetic-only pre-access guards for Spanish PAN/IAEN documentary pairs."""
from dataclasses import replace
from hashlib import sha256
import json

import pytest

from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.pan_iaen_preaccess_gate import (
    FictionalAnnualHeader, FictionalPlanItem, FictionalReportRow,
    audit_fictional_pan_iaen, REPORT_CLASSES,
)


SHA_PAN = sha256(b"SYNTHETIC PAN DOCUMENT").hexdigest()
SHA_REPORT = sha256(b"SYNTHETIC IAEN DOCUMENT").hexdigest()
CAPTURE = "2026-06-01T12:00:00Z"
PREVIEW = "2025-04-16T12:00:00Z"
ZONE = "Europe/Madrid"


def fixture():
    plan = FictionalAnnualHeader(
        document_id="SYNTHETIC:PAN_DOC", issuer_namespace="SYNTHETIC:AGE",
        kind="PAN", label_year=2024, activity_year=2024,
        approved_on="2024-03-26", captured_at=CAPTURE,
        sha256_claim=SHA_PAN, legal_calendar_zone=ZONE,
    )
    report = FictionalAnnualHeader(
        document_id="SYNTHETIC:IAEN_DOC", issuer_namespace="SYNTHETIC:AGE",
        kind="IAEN", label_year=2024, activity_year=2024,
        approved_on="2025-04-15", captured_at=CAPTURE,
        sha256_claim=SHA_REPORT, legal_calendar_zone=ZONE,
    )
    items = (
        FictionalPlanItem(
            item_id="SYNTHETIC:ITEM1", issuer_namespace="SYNTHETIC:MINISTRY_A",
            plan_document_id=plan.document_id,
            plan_document_sha256_claim=SHA_PAN, captured_at=CAPTURE,
        ),
        FictionalPlanItem(
            item_id="SYNTHETIC:ITEM1", issuer_namespace="SYNTHETIC:MINISTRY_B",
            plan_document_id=plan.document_id,
            plan_document_sha256_claim=SHA_PAN, captured_at=CAPTURE,
        ),
    )
    rows = (
        FictionalReportRow(
            row_id="SYNTHETIC:R1", section="PLANNED_ITEMS",
            report_document_id=report.document_id,
            report_document_sha256_claim=SHA_REPORT,
            referenced_plan_item_id="SYNTHETIC:ITEM1",
            referenced_item_issuer="SYNTHETIC:MINISTRY_A",
            referenced_plan_document_id=plan.document_id,
            referenced_plan_document_issuer=plan.issuer_namespace,
            referenced_plan_document_sha256_claim=plan.sha256_claim,
            captured_at=CAPTURE,
        ),
        FictionalReportRow(
            row_id="SYNTHETIC:R2", section="UNPLANNED_ADOPTIONS",
            report_document_id=report.document_id,
            report_document_sha256_claim=SHA_REPORT,
            captured_at=CAPTURE,
        ),
        FictionalReportRow(
            row_id="SYNTHETIC:R3", section="EXPOST_PRIOR_NORMS",
            report_document_id=report.document_id,
            report_document_sha256_claim=SHA_REPORT,
            captured_at=CAPTURE,
        ),
    )
    return plan, report, items, rows


def audit(plan=None, report=None, items=None, rows=None,
          as_of="2026-06-02T12:00:00Z"):
    p, r, i, x = fixture()
    return audit_fictional_pan_iaen(
        plan=p if plan is None else plan,
        report=r if report is None else report,
        planned_items=i if items is None else items,
        report_rows=x if rows is None else rows,
        as_of=as_of,
    )


def test_report_label_is_activity_year_not_approval_year():
    result = audit()
    assert result["plan_year"] == 2024
    assert result["report_label_year"] == 2024
    assert result["report_approval_year"] == 2025
    assert result["visible_planned_items"] == 2
    assert result["explicit_source_local_plan_references"] == 1
    assert result["planned_items_without_report_reference_are_unknown"] == 1
    assert result["visible_unplanned_report_rows"] == 1
    assert result["visible_expost_report_rows"] == 1


def test_false_pair_pan2024_with_iaen_label2025_fails_even_if_approved_2025():
    plan, report, _, _ = fixture()
    fake = replace(report, label_year=2025, activity_year=2025,
                   approved_on="2026-05-05")
    with pytest.raises(GateError, match="PAN_IAEN_YEAR_PAIR_MISMATCH"):
        audit(plan=plan, report=fake)


def test_report_approval_year_can_be_later_than_label_without_false_join():
    _, report, _, _ = fixture()
    with pytest.raises(GateError, match="IAEN_APPROVAL_NOT_AFTER_ACTIVITY"):
        replace(report, approved_on="2024-11-01")
    assert audit()["report_approval_year"] == 2025


def test_plan_edition_approved_after_its_annual_evaluation_cannot_be_linked():
    plan, report, _, _ = fixture()
    # A late-created plan document cannot already have been evaluated in 2025.
    forged = replace(plan, approved_on="2026-05-01")
    with pytest.raises(GateError, match="PLAN_APPROVED_AFTER_IAEN"):
        audit(plan=forged, report=report)


def test_same_item_id_in_different_ministries_is_not_a_join():
    result = audit()
    assert result["explicit_source_local_plan_references"] == 1
    assert result["planned_items_without_report_reference_are_unknown"] == 1
    _, _, _, rows = fixture()
    spoof = replace(rows[0], referenced_item_issuer="SYNTHETIC:MINISTRY_C")
    result = audit(rows=(spoof, *rows[1:]))
    assert result["explicit_source_local_plan_references"] == 0
    assert result["unresolved_cross_references"] == 1
    assert result["planned_items_without_report_reference_are_unknown"] == 2


def test_reference_to_old_plan_edition_cannot_match_reissued_plan():
    plan, report, items, rows = fixture()
    new_digest = sha256(b"DIFFERENT SYNTHETIC PAN EDITION").hexdigest()
    revised_plan = replace(plan, document_id="SYNTHETIC:PAN_EDITION_2",
                           sha256_claim=new_digest)
    revised_items = tuple(replace(x,
                                  plan_document_id=revised_plan.document_id,
                                  plan_document_sha256_claim=new_digest)
                          for x in items)
    result = audit(plan=revised_plan, report=report,
                   items=revised_items, rows=rows)
    assert result["explicit_source_local_plan_references"] == 0
    assert result["unresolved_cross_references"] == 1
    assert result["planned_items_without_report_reference_are_unknown"] == 2


def test_unplanned_and_expost_must_not_become_pan_matches():
    _, _, _, rows = fixture()
    for section in ("UNPLANNED_ADOPTIONS", "EXPOST_PRIOR_NORMS"):
        with pytest.raises(GateError, match="NONPLAN_SECTION_CANNOT_CLAIM_PLAN_ITEM"):
            replace(rows[0], section=section)
    assert set(REPORT_CLASSES) == {"PLANNED_ITEMS", "UNPLANNED_ADOPTIONS", "EXPOST_PRIOR_NORMS"}


def test_missing_report_line_is_unknown_not_policy_failure():
    _, _, _, rows = fixture()
    result = audit(rows=rows[1:])
    assert result["explicit_source_local_plan_references"] == 0
    assert result["planned_items_without_report_reference_are_unknown"] == 2
    assert result["nonreference_implies_noncompliance"] is False
    assert result["real_policy_outcomes_admitted"] is False


def test_capture_asof_hides_unavailable_report_and_rows():
    r = audit(as_of=PREVIEW)
    assert r["visible_report"] is False
    assert r["explicit_source_local_plan_references"] == 0
    assert r["real_historical_first_public_at"] is None


def test_future_inconsistent_witness_cannot_rewrite_earlier_snapshot():
    p, r, items, rows = fixture()
    old = audit(as_of="2026-06-02T12:00:00Z")
    future_row = replace(rows[0], row_id="SYNTHETIC:FUTURE_REPORT_ROW",
                         captured_at="2026-07-01T12:00:00Z",
                         report_document_sha256_claim="0" * 64)
    future_item = replace(items[0], item_id="SYNTHETIC:FUTURE_ITEM",
                          captured_at="2026-07-01T12:00:00Z",
                          plan_document_sha256_claim="0" * 64)
    # Uncaptured declarations have no power over an earlier as-of result.
    assert audit(items=(*items, future_item), rows=(*rows, future_row),
                 as_of="2026-06-02T12:00:00Z") == old
    # Once their capture is known, their incompatible references quarantine.
    with pytest.raises(GateError, match="INVALID_PLAN_ITEM_DOCUMENT_WITNESS|INVALID_REPORT_ROW_DOCUMENT_WITNESS"):
        audit(items=(*items, future_item), rows=(*rows, future_row),
              as_of="2026-07-02T12:00:00Z")


def test_spoofed_original_rights_person_and_wrong_document_reference_fail_closed():
    plan, report, items, rows = fixture()
    for field, value in (("rights_verified", True), ("original_authenticated", True),
                         ("first_public_at", "2024-03-26T00:00:00Z")):
        with pytest.raises(GateError, match="UNAUTHORIZED_REAL_SOURCE_CLAIM"):
            replace(plan, **{field: value})
    with pytest.raises(GateError, match="INVALID_REPORT_ROW_DOCUMENT_WITNESS"):
        audit(rows=(replace(rows[0], report_document_sha256_claim="0" * 64), *rows[1:]))
    with pytest.raises(GateError, match="INVALID_PLAN_ITEM_DOCUMENT_WITNESS"):
        audit(items=(replace(items[0], plan_document_id="SYNTHETIC:OTHER"), items[1]))
    with pytest.raises(GateError, match="SYNTHETIC_IDS_ONLY"):
        replace(rows[0], referenced_plan_item_id="REAL-NAME")


def test_duplicate_references_cannot_inflate_plan_coverage():
    _, _, _, rows = fixture()
    with pytest.raises(GateError, match="DUPLICATE_REPORT_ROW_ID"):
        audit(rows=(*rows, rows[0]))


def test_result_is_nonconfirmatory_without_person_ids_or_outcomes():
    r = audit()
    assert r["rights_by_asset_verified"] is False
    assert r["legal_terms_accepted"] is False
    assert r["complete_entry_population_attested"] is False
    assert r["AB_scientific_cycles"] == 0
    assert r["eligible_for_real_ingestion"] is False
    assert r["usable_as_confirmatory_holdout"] is False
    assert "SYNTHETIC:ITEM1" not in json.dumps(r)
    assert "SYNTHETIC:MINISTRY_A" not in json.dumps(r)
