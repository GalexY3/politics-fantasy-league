"""Synthetic pre-access contract for PAN / IAEN document relationships.

This module never reads a PAN, an IAEN, a BOE disposition or a real-world
policy outcome. It checks how a future, rights-approved acquisition *would*
represent different calendar years and explicit source-local references.
No source data, legal permission, publication witness or causal finding may be
inferred from successful checks on synthetic objects.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit

from .procedural_index_contract import GateError, SHA, day, utc, legal_civil_date
from .synthetic_registration_graph import SYNTHETIC_ID


REPORT_CLASSES = (
    "PLANNED_ITEMS", "UNPLANNED_ADOPTIONS", "EXPOST_PRIOR_NORMS",
)
MAX_ITEMS = 250
MAX_REPORT_ROWS = 500


def _synth(value: object) -> bool:
    return type(value) is str and SYNTHETIC_ID.fullmatch(value) is not None


def _digest(value: object) -> bool:
    return type(value) is str and SHA.fullmatch(value) is not None


@dataclass(frozen=True)
class FictionalAnnualHeader:
    """A deliberately fictitious plan/report, not evidence of an original."""

    document_id: str
    issuer_namespace: str
    kind: str
    label_year: int
    activity_year: int
    approved_on: str
    captured_at: str
    sha256_claim: str
    legal_calendar_zone: str
    original_authenticated: bool = False
    rights_verified: bool = False
    terms_accepted: bool = False
    first_public_at: None = None

    def __post_init__(self) -> None:
        if (not _synth(self.document_id) or not _synth(self.issuer_namespace)
                or self.kind not in ("PAN", "IAEN") or type(self.kind) is not str
                or not _digest(self.sha256_claim)):
            raise GateError("PAN_IAEN_SYNTHETIC_HEADER_REQUIRED")
        if (type(self.label_year) is not int or type(self.activity_year) is not int
                or not 2017 <= self.activity_year <= 2100
                or self.label_year != self.activity_year):
            raise GateError("PAN_IAEN_INVALID_REPORT_LABEL_YEAR")
        if (self.original_authenticated is not False
                or self.rights_verified is not False
                or self.terms_accepted is not False
                or self.first_public_at is not None):
            raise GateError("PAN_IAEN_UNAUTHORIZED_REAL_SOURCE_CLAIM")
        approval = day(self.approved_on)
        if (self.kind == "IAEN" and approval.year <= self.activity_year):
            raise GateError("PAN_IAEN_IAEN_APPROVAL_NOT_AFTER_ACTIVITY")
        observed = utc(self.captured_at)
        if legal_civil_date(self.captured_at, self.legal_calendar_zone) < approval:
            raise GateError("PAN_IAEN_CAPTURE_BEFORE_APPROVAL_DATE")


@dataclass(frozen=True)
class FictionalPlanItem:
    """Namespaced entry explicitly attached to one fictional plan edition."""

    item_id: str
    issuer_namespace: str
    plan_document_id: str
    plan_document_sha256_claim: str
    captured_at: str
    first_public_at: None = None
    original_authenticated: bool = False

    def __post_init__(self) -> None:
        if not all(_synth(x) for x in (
                self.item_id, self.issuer_namespace, self.plan_document_id)):
            raise GateError("PAN_IAEN_SYNTHETIC_IDS_ONLY")
        if not _digest(self.plan_document_sha256_claim):
            raise GateError("PAN_IAEN_SYNTHETIC_ITEM_SHA_REQUIRED")
        if (self.first_public_at is not None
                or self.original_authenticated is not False):
            raise GateError("PAN_IAEN_UNAUTHORIZED_REAL_SOURCE_CLAIM")
        utc(self.captured_at)


@dataclass(frozen=True)
class FictionalReportRow:
    """A synthetic report section: planned vs extra vs ex-post stay separate."""

    row_id: str
    section: str
    report_document_id: str
    report_document_sha256_claim: str
    captured_at: str
    referenced_plan_item_id: str | None = None
    referenced_item_issuer: str | None = None
    referenced_plan_document_id: str | None = None
    referenced_plan_document_issuer: str | None = None
    referenced_plan_document_sha256_claim: str | None = None
    first_public_at: None = None
    original_authenticated: bool = False

    def __post_init__(self) -> None:
        if (not _synth(self.row_id)
                or not _synth(self.report_document_id)
                or type(self.section) is not str
                or self.section not in REPORT_CLASSES
                or not _digest(self.report_document_sha256_claim)):
            raise GateError("PAN_IAEN_SYNTHETIC_REPORT_ROW_REQUIRED")
        if (self.first_public_at is not None
                or self.original_authenticated is not False):
            raise GateError("PAN_IAEN_UNAUTHORIZED_REAL_SOURCE_CLAIM")
        if self.section == "PLANNED_ITEMS":
            if not (_synth(self.referenced_plan_item_id)
                    and _synth(self.referenced_item_issuer)
                    and _synth(self.referenced_plan_document_id)
                    and _synth(self.referenced_plan_document_issuer)
                    and _digest(self.referenced_plan_document_sha256_claim)):
                raise GateError("PAN_IAEN_SYNTHETIC_IDS_ONLY")
        elif (self.referenced_plan_item_id is not None
              or self.referenced_item_issuer is not None
              or self.referenced_plan_document_id is not None
              or self.referenced_plan_document_issuer is not None
              or self.referenced_plan_document_sha256_claim is not None):
            raise GateError("PAN_IAEN_NONPLAN_SECTION_CANNOT_CLAIM_PLAN_ITEM")
        utc(self.captured_at)


def audit_fictional_pan_iaen(
    *, plan: FictionalAnnualHeader, report: FictionalAnnualHeader,
    planned_items: tuple[FictionalPlanItem, ...],
    report_rows: tuple[FictionalReportRow, ...], as_of: str,
) -> dict:
    """Require year, edition, namespace and time before any fictional crosswalk.

    The output never endorses an actual pair of government files, sample,
    license, effectiveness or statistical holdout.
    """
    if (type(plan) is not FictionalAnnualHeader
            or type(report) is not FictionalAnnualHeader
            or plan.kind != "PAN" or report.kind != "IAEN"):
        raise GateError("PAN_IAEN_DOCUMENT_ROLES_REQUIRED")
    if (type(planned_items) is not tuple or type(report_rows) is not tuple
            or len(planned_items) > MAX_ITEMS or len(report_rows) > MAX_REPORT_ROWS
            or any(type(x) is not FictionalPlanItem for x in planned_items)
            or any(type(x) is not FictionalReportRow for x in report_rows)):
        raise GateError("PAN_IAEN_BOUNDED_SYNTHETIC_RECORDS_REQUIRED")
    if (report.activity_year != plan.activity_year
            or report.label_year != plan.label_year
            or plan.issuer_namespace != report.issuer_namespace
            or plan.legal_calendar_zone != report.legal_calendar_zone):
        raise GateError("PAN_IAEN_YEAR_PAIR_MISMATCH")
    if day(plan.approved_on) > day(report.approved_on):
        raise GateError("PAN_IAEN_PLAN_APPROVED_AFTER_IAEN")
    at = utc(as_of)
    # A future derivative must not affect an earlier historical audit, even
    # through a rejecting source/edition claim. Its constructor still rejects
    # intrinsically malformed synthetic records before this function runs.
    known_items = tuple(x for x in planned_items if utc(x.captured_at) <= at)
    known_rows = tuple(x for x in report_rows if utc(x.captured_at) <= at)
    for item in known_items:
        if (item.plan_document_id != plan.document_id
                or item.plan_document_sha256_claim != plan.sha256_claim):
            raise GateError("PAN_IAEN_INVALID_PLAN_ITEM_DOCUMENT_WITNESS")
        if utc(item.captured_at) < utc(plan.captured_at):
            raise GateError("PAN_IAEN_ITEM_DERIVATIVE_BEFORE_PLAN_CAPTURE")
    for row in known_rows:
        if (row.report_document_id != report.document_id
                or row.report_document_sha256_claim != report.sha256_claim):
            raise GateError("PAN_IAEN_INVALID_REPORT_ROW_DOCUMENT_WITNESS")
        if utc(row.captured_at) < utc(report.captured_at):
            raise GateError("PAN_IAEN_ROW_DERIVATIVE_BEFORE_REPORT_CAPTURE")

    plan_visible = utc(plan.captured_at) <= at
    report_visible = utc(report.captured_at) <= at
    visible_items = known_items if plan_visible else ()
    visible_rows = known_rows if report_visible else ()
    item_keys = [(x.issuer_namespace, x.item_id) for x in visible_items]
    row_keys = [x.row_id for x in visible_rows]
    if len(item_keys) != len(set(item_keys)):
        raise GateError("PAN_IAEN_DUPLICATE_PLANNED_ITEM_KEY")
    if len(row_keys) != len(set(row_keys)):
        raise GateError("PAN_IAEN_DUPLICATE_REPORT_ROW_ID")

    known_items = set(item_keys)
    matched = set()
    observed_crossrefs = 0
    unresolved = 0
    for row in visible_rows:
        if row.section != "PLANNED_ITEMS":
            continue
        key = row.referenced_item_issuer, row.referenced_plan_item_id
        edition_match = (
            row.referenced_plan_document_id == plan.document_id
            and row.referenced_plan_document_issuer == plan.issuer_namespace
            and row.referenced_plan_document_sha256_claim == plan.sha256_claim
        )
        if key in known_items and edition_match:
            observed_crossrefs += 1
            matched.add(key)
        else:
            # A missing document witness is UNKNOWN, not noncompliance.
            unresolved += 1

    return {
        "schema": "pfl.synthetic_pan_iaen_preaccess.v1",
        "evidence_class": "SYNTHETIC_DOCUMENTARY_METADATA_ONLY",
        "plan_year": plan.activity_year,
        "report_label_year": report.label_year,
        "report_evaluated_year": report.activity_year,
        "report_approval_year": day(report.approved_on).year,
        "as_of": as_of,
        "visible_plan": plan_visible,
        "visible_report": report_visible,
        "visible_planned_items": len(visible_items),
        "visible_report_rows": len(visible_rows),
        "visible_unplanned_report_rows": sum(
            x.section == "UNPLANNED_ADOPTIONS" for x in visible_rows),
        "visible_expost_report_rows": sum(
            x.section == "EXPOST_PRIOR_NORMS" for x in visible_rows),
        "explicit_source_local_plan_references": observed_crossrefs,
        "unresolved_cross_references": unresolved,
        "planned_items_without_report_reference_are_unknown": len(known_items - matched),
        "nonreference_implies_noncompliance": False,
        "real_historical_first_public_at": None,
        "source_local_crosswalk_independently_authenticated": False,
        "rights_by_asset_verified": False,
        "legal_terms_accepted": False,
        "complete_entry_population_attested": False,
        "real_policy_outcomes_admitted": False,
        "eligible_for_real_ingestion": False,
        "usable_as_confirmatory_holdout": False,
        "AB_scientific_cycles": 0,
    }


def validate_preaccess_source_manifest(data: dict) -> dict:
    """Validate an inert documentary gate, not truth, permissions or originals.

    Refuse an inconsistent proposed PAN/IAEN year pair, silent restoration of
    exposed holdouts, or a catalog's promotion to rights/real-data admission.
    This function intentionally cannot return an affirmative ingestion permit.
    """
    if type(data) is not dict or data.get("schema") != "pfl.public_policy_source_gate.v1":
        raise GateError("PAN_IAEN_UNKNOWN_MANIFEST_SCHEMA")

    def exact_keys(item: object, allowed: set[str]) -> None:
        if type(item) is not dict or set(item) != allowed:
            raise GateError("PAN_IAEN_MANIFEST_UNEXPECTED_FIELD")

    exact_keys(data, {
        "schema", "generated_on", "scope", "evidence_class", "AB_scientific_cycles",
        "R5", "canonical_parent_commit", "reused_policy_trace_commit",
        "prior_inventories", "primary_candidate", "alternatives",
        "regional_documentary_alternatives", "next_admissible_action", "do_not",
    })
    if data.get("R5") != "STOP" or data.get("AB_scientific_cycles") != 0:
        raise GateError("PAN_IAEN_MANIFEST_SCIENTIFIC_GATE_CANNOT_PROMOTE")
    candidate = data.get("primary_candidate")
    if type(candidate) is not dict:
        raise GateError("PAN_IAEN_MANIFEST_CANDIDATE_REQUIRED")
    exact_keys(candidate, {
        "id", "status", "unit_proposed", "not_equivalent_to", "possible_pair",
        "plan_page", "report_listing_page", "another_confirmed_pair",
        "prior_incorrect_pairing", "index_update_date_is_not_report_approval_or_first_public_at",
        "exposure_notice", "legal_basis", "rights_page",
        "rights_general_terms_bind_by_use", "rights_by_exact_asset_verified",
        "rights_acceptance_user_approved", "original_plan_bytes_read",
        "original_report_bytes_read", "individual_items_read",
        "individual_outcome_rows_read", "independent_denominator",
        "first_public_at_per_item", "historical_vintages_verified",
        "negative_pending_unplanned_coverage_verified", "crosswalk_verified",
        "reopen_when", "falsifier",
    })

    def expect_pair(pair: object, planned_year: int) -> None:
        expected = {
            "plan_year", "report_label_year", "activity_evaluated_year",
            "report_approval_year", "report_approval_on", "editorial_confirmation_url",
            "verified_individual_crosswalk",
        }
        exact_keys(pair, expected | ({"relationship"} if planned_year == 2024
                                      else {"report_listing_page"}))
        if type(pair) is not dict or any(
            type(pair.get(k)) is not int for k in (
                "plan_year", "report_label_year", "activity_evaluated_year",
                "report_approval_year",
            )
        ):
            raise GateError("PAN_IAEN_MANIFEST_YEAR_RELATION_FALSE")
        if (pair["plan_year"] != planned_year
                or pair["report_label_year"] != planned_year
                or pair["activity_evaluated_year"] != planned_year):
            raise GateError("PAN_IAEN_MANIFEST_YEAR_RELATION_FALSE")
        try:
            approval = day(pair["report_approval_on"])
        except (KeyError, ValueError, TypeError) as exc:
            raise GateError("PAN_IAEN_MANIFEST_REPORT_APPROVAL_MISMATCH") from exc
        if (pair["report_approval_year"] != planned_year + 1
                or approval.year != pair["report_approval_year"]):
            raise GateError("PAN_IAEN_MANIFEST_REPORT_APPROVAL_MISMATCH")
        if pair.get("verified_individual_crosswalk") is not False:
            raise GateError("PAN_IAEN_MANIFEST_FAKE_CROSSWALK_OR_DENOMINATOR")
        link = pair.get("editorial_confirmation_url")
        if (type(link) is not str or not link.startswith("https://")
                or urlsplit(link).hostname != "www.lamoncloa.gob.es"):
            raise GateError("PAN_IAEN_MANIFEST_EDITORIAL_REFERENCE_REQUIRED")

    expect_pair(candidate.get("possible_pair"), 2024)
    expect_pair(candidate.get("another_confirmed_pair"), 2025)
    # The plan's catalog page names the report by the *activity* year, not by
    # the later approval year. Reject the historical erroneous manifest URL.
    for planned_year, section in ((2024, candidate), (2025, candidate["another_confirmed_pair"])):
        listing = section.get("report_listing_page")
        if type(listing) is not str or not listing.endswith(f"plan-anual-{planned_year}"):
            raise GateError("PAN_IAEN_MANIFEST_REPORT_LISTING_LABEL_DRIFT")

    for field in ("rights_by_exact_asset_verified", "rights_acceptance_user_approved",
                  "original_plan_bytes_read", "original_report_bytes_read",
                  "individual_items_read", "individual_outcome_rows_read", "crosswalk_verified",
                  "negative_pending_unplanned_coverage_verified",
                  "historical_vintages_verified"):
        if candidate.get(field) is not False:
            if field.startswith("rights_") or field.startswith("original_") or field in (
                    "individual_items_read", "individual_outcome_rows_read"):
                raise GateError("PAN_IAEN_MANIFEST_UNAUTHORIZED_RIGHTS_PROMOTION")
            raise GateError("PAN_IAEN_MANIFEST_FAKE_CROSSWALK_OR_DENOMINATOR")
    if candidate.get("independent_denominator") is not None or candidate.get("first_public_at_per_item") is not None:
        raise GateError("PAN_IAEN_MANIFEST_FAKE_CROSSWALK_OR_DENOMINATOR")
    if candidate.get("status") != "DOCUMENTED_PREACCESS_BLOCKED_R5":
        raise GateError("PAN_IAEN_MANIFEST_SCIENTIFIC_GATE_CANNOT_PROMOTE")
    exposure = candidate.get("exposure_notice")
    if type(exposure) is not dict:
        raise GateError("PAN_IAEN_MANIFEST_OUTCOME_EXPOSURE_CONTRADICTION")
    exact_keys(exposure, {"2024", "2025", "interpretation"})
    for year in ("2024", "2025"):
        record = exposure.get(year)
        exact_keys(record, {"aggregate_outcome_snippet_seen", "confirmatory_holdout_unexposed"})
        if (type(record) is not dict
                or record.get("aggregate_outcome_snippet_seen") is not True
                or record.get("confirmatory_holdout_unexposed") is not False):
            raise GateError("PAN_IAEN_MANIFEST_OUTCOME_EXPOSURE_CONTRADICTION")

    alternatives = data.get("regional_documentary_alternatives")
    if type(alternatives) is not list or len(alternatives) != 2:
        raise GateError("PAN_IAEN_MANIFEST_REGION_GATE_REQUIRED")
    for asset in alternatives:
        if (type(asset) is not dict
                or asset.get("status") != "PREACCESS_STOP"
                or asset.get("source_rights_and_terms_human_approved") is not False
                or asset.get("original_opened") is not False):
            raise GateError("PAN_IAEN_MANIFEST_UNAUTHORIZED_RIGHTS_PROMOTION")
        expected = {
            "id", "catalog_claimed_license", "use_by_access_conditions_reported",
            "source_rights_and_terms_human_approved", "original_opened", "status",
        }
        exact_keys(asset, expected | ({"exact_asset_catalog_url"}
                                    if asset.get("id") == "ANDALUSIA_PAN2018_CSV"
                                    else {"dataset_catalog_url"}))

    return {
        "schema": "pfl.pan_iaen_source_manifest_review.v1",
        "evidence_class": "DOCUMENTARY_GATE_STRUCTURAL_CONSISTENCY_ONLY",
        "year_mapping_documented": True,
        "report_labels_checked": [2024, 2025],
        "outcome_2024_2025_blind_holdout": False,
        "real_ingestion_admitted": False,
        "rights_per_asset_approved": False,
        "registered_population_authenticated": False,
        "AB_scientific_cycles": 0,
        "R5": "STOP",
    }
