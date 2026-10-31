"""Read-only, aggregate institutional population-readiness report for PFL.

Only compositions of *already reviewed* source manifests and local-as-of
metadata are shown; this endpoint cannot admit outcomes, assert population
completeness or issue cross-institutional joins. Each source has a distinct
unit/grain and must NOT be summed to an alleged Spanish risk set.
"""
from __future__ import annotations

from .parcan_cohort_status import status as canarian_status
from .procedural_coverage import coverage_status
from .siap_coverage import status as siap_status

GATES = (
    "ASSET_RIGHTS_AND_ORIGINAL_HASH",
    "STABLE_INSTITUTION_SCOPED_KEYS",
    "COMPLETE_PAGINATION_AND_SELECTION_SCOPE",
    "INDEPENDENT_ENTRY_REGISTRY_DENOMINATOR",
    "DATE_OF_COMMON_RISK_ENTRY_EVENT",
    "DATED_DOCUMENTED_TRANSITIONS",
    "TERMINAL_AND_PENDING_STATE_TAXONOMY",
    "HISTORICAL_SOURCE_VINTAGE_AVAILABILITY",
    "OBSERVABLE_RIGHT_CENSORING_AND_REGIME_CHANGES",
)


def report(*, as_of: str | None = None) -> dict:
    """Conservative matrix; no fake 0s for sources not yet observed locally."""
    parcan = canarian_status(as_of=as_of)
    editorial = coverage_status(as_of=as_of)
    siap = siap_status(as_of=as_of)
    local_parcan = parcan.get("observed_rows") if parcan.get("ok") else None
    local_siap = siap.get("observed_links")
    # We do not expose future hashes, counts or missing receipts in earlier
    # snapshots. The source type itself is static and cannot leak outcomes.
    source_rows = [
        {
            "source_id": "PARCAN_SOURCE_LOCAL",
            "institution": "Parlamento de Canarias",
            "unit": "CURRENT_CAPTURE_SOURCE_LOCAL_INITIATIVE_ID",
            "observed_metadata_rows": local_parcan,
            "source_distributions_visible": len(parcan.get("source_cohorts", [])) if local_parcan is not None else None,
            "index_pages_captured": None,
            "index_pages_required": None,
            "rights_scope": "PDDL_DISTRIBUTION_LABEL; PERSONAL_AND_OUTCOME_USE_UNRESOLVED",
            "provenance_status": parcan.get("status"),
            "index_total_concordant": (
                editorial.get("status") == "CONCORDANT_SOURCE_COUNTERS_NOT_CENSUS"
                if editorial.get("status") not in {"SOURCE_NOT_KNOWN_AT_REQUESTED_CUT", "CROSSVIEW_QUARANTINED"}
                else None),
            "independent_entry_denominator": None,
            "outcomes_and_transitions_available_for_inference": False,
            "first_public_at_attested": False,
        },
        {
            "source_id": "PARLAMENT_CATALUNYA_SIAP",
            "institution": "Parlament de Catalunya",
            "unit": "SOURCE_INDEX_PAGE_LINK_NOT_ENTRY_EVENT",
            "observed_metadata_rows": local_siap,
            "source_distributions_visible": None,
            "index_pages_captured": siap.get("source_pages_captured"),
            "index_pages_required": siap.get("source_index_pages"),
            "rights_scope": "GENERAL_INFORMATION_NOTICE; PERSONAL_AND_BULK_USE_UNRESOLVED",
            "provenance_status": siap.get("status"),
            "index_total_concordant": None,
            "independent_entry_denominator": None,
            "outcomes_and_transitions_available_for_inference": False,
            "first_public_at_attested": False,
        },
        {
            "source_id": "CONGRESO_XV_CANDIDATE_INDICES",
            "institution": "Congreso de los Diputados",
            "unit": "WEB_DISCOVERY_ONLY_NO_ADMITTED_ORIGINAL",
            "observed_metadata_rows": None,
            "source_distributions_visible": None,
            "index_pages_captured": None,
            "index_pages_required": None,
            "rights_scope": "REUSE_BY_ASSET_UNRESOLVED",
            "provenance_status": "DISCOVERY_NOT_ORIGINAL_CAPTURE",
            "index_total_concordant": None,
            "independent_entry_denominator": None,
            "outcomes_and_transitions_available_for_inference": False,
            "first_public_at_attested": False,
        },
    ]
    return {
        "schema": "pfl.spanish_procedural_population_readiness.v1",
        "as_of": as_of,
        "institutional_sources": source_rows,
        "source_groups": len(source_rows),
        "risk_set_denominator": None,
        "reusable_scientific_cohort": False,
        "stage": "DISCOVERY_AND_PROVENANCE_ONLY",
        "coverage_gates": [{"gate": k, "scientific_admission": "NOT_ATTESTED"} for k in GATES],
        "observed_metadata_cannot_be_added_across_institutions": True,
        "current_capture_not_historical_publication": True,
        "unknown_is_not_zero": True,
        "censored_cases_estimated": None,
        "terminal_events_observed_for_scientific_use": None,
        "dated_transitions_observed_for_scientific_use": None,
        "historical_first_public_at_per_revision_verified": False,
        "cross_institution_joins_admitted": False,
        "boe_is_population_denominator": False,
        "validated_feedback_mechanisms": 0,
        "real_person_scoring": False,
        "scientific_cycles": 0,
    }
