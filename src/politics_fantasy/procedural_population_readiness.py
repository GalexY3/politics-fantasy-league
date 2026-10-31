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
from .procedural_discovery_r7 import status as discovery_status
from .procedural_discovery_r8 import status as discovery_r8_status
from .retained_integrity_status import status as integrity_status
from .procedural_discovery_r9 import status as discovery_r9_status

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
    discovery = discovery_status(as_of=as_of)
    discovery_r8 = discovery_r8_status(as_of=as_of)
    integrity = integrity_status(as_of=as_of)
    discovery_r9 = discovery_r9_status(as_of=as_of)
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
        "documentary_candidate_sources": discovery.get("candidate_sources", []),
        "documentary_candidate_sources_count": discovery.get("documentary_sources_count"),
        "documentary_candidate_status": discovery.get("status"),
        "documentary_catalogue_safe_by": discovery.get("local_audit_safe_by"),
        "documentary_candidates_are_not_registered_processes": True,
        "documentary_source_direct_bulk_download_permitted": False,
        "r8_documentary_status": discovery_r8.get("status"),
        "r8_regional_routes": discovery_r8.get("regional_routes", []),
        "r8_national_core_routes": discovery_r8.get("national_core_routes", []),
        "r8_regional_source_count": discovery_r8.get("regional_source_count"),
        "r8_national_documentary_assets_count": discovery_r8.get("national_documentary_assets_count"),
        "r8_audit_safe_by": discovery_r8.get("local_audit_safe_by"),
        "r8_sources_are_not_entry_records": True,
        "r8_consejo_de_estado_is_not_congreso_risk_set": True,
        "retained_original_integrity": {
            "status": integrity["status"],
            "official_originals_byte_checked": integrity.get("originals_verified"),
            "private_derivatives_byte_checked": integrity.get("private_derivatives_verified"),
            "local_audit_safe_by": integrity.get("local_audit_safe_by"),
            "actual_source_census_verified": False,
            "additional_processing_rights_granted": False,
            "historical_first_publication_derived": False,
        },
        "r9_documentary_status": discovery_r9["status"],
        "r9_regional_sources_documented": discovery_r9.get("regional_source_count"),
        "r9_national_assets_documented": discovery_r9.get("national_source_count"),
        "r9_regional_highlights": discovery_r9.get("regional_highlights",[]),
        "r9_national_highlights": discovery_r9.get("national_highlights",[]),
        "r9_documentary_safe_by": discovery_r9.get("source_metadata_safe_by"),
        "r9_pre_AJ_outcome_header_exposure": discovery_r9.get("pre_registration_outcome_header_exposure"),
        "r9_no_independent_national_or_regional_denominator": (
            True if discovery_r9["status"]=="R9_DISCOVERY_ONLY_RIGHTS_AND_DENOMINATORS_BLOCKED"
            else None),
        "risk_set_denominator": None,
        "reusable_scientific_cohort": False,
        "stage": "DISCOVERY_AND_PROVENANCE_ONLY",
        "linkage_and_identification": {
            "register_to_expediente": "NOT_ATTESTED_WITH_OFFICIAL_DUAL_ID_AND_RAW_RECEIPT",
            "independent_register_denominator": None,
            "event_by_cut_bounds": None,
            "event_by_cut_status": "NOT_IDENTIFIABLE_ON_CURRENT_REAL_SOURCES",
            "selection_bias_unresolved": True,
            "synthetic_tools_are_not_observations": True,
            "unlinked_records_are_not_rejections": True,
            "missing_outcomes_are_not_zero": True,
        },
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
