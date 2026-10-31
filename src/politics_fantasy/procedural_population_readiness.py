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
from .denominator_evidence_status import derive_denominator_evidence
from .procedural_discovery_r10 import status as discovery_r10_status
from .procedural_discovery_r11 import status as discovery_r11_status
from .procedural_discovery_r12 import status as discovery_r12_status
from .procedural_discovery_r13 import status as discovery_r13_status
from .procedural_discovery_r14 import status as discovery_r14_status
from .procedural_discovery_r16 import status as discovery_r16_status

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
    discovery_r10 = discovery_r10_status(as_of=as_of)
    discovery_r11 = discovery_r11_status(as_of=as_of)
    discovery_r12 = discovery_r12_status(as_of=as_of)
    discovery_r13 = discovery_r13_status(as_of=as_of)
    discovery_r14 = discovery_r14_status(as_of=as_of)
    discovery_r16 = discovery_r16_status(as_of=as_of)
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
    # Internal *registry slots* are not the same as information available to
    # a historical observer. Keep three internal slots for the denominator
    # validator (which never promotes a census), but disclose only sources
    # that had affirmative metadata evidence at the requested cut. In
    # particular, the XV Congress placeholder must not appear in 2010.
    visible_source_rows = [
        s for s in source_rows
        if ((s["source_id"] == "PARCAN_SOURCE_LOCAL" and local_parcan is not None)
            or (s["source_id"] == "PARLAMENT_CATALUNYA_SIAP" and local_siap is not None)
            or (s["source_id"] == "CONGRESO_XV_CANDIDATE_INDICES" and
                discovery["status"] == "DOCUMENTARY_CANDIDATES_BLOCKED_FROM_SOURCE_ADMISSION"))
    ]
    return {
        "schema": "pfl.spanish_procedural_population_readiness.v1",
        "as_of": as_of,
        "institutional_sources": visible_source_rows,
        "source_groups": len(visible_source_rows),
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
        "r10_documentary_status": discovery_r10["status"],
        "r10_regional_documentary_assets": discovery_r10.get("regional_total"),
        "r10_national_documentary_routes": discovery_r10.get("national_routes_total"),
        "r10_regional_highlights": discovery_r10.get("regional_routes",[]),
        "r10_national_highlights": discovery_r10.get("national_routes",[]),
        "r10_asof_safe_by": discovery_r10.get("local_documentary_safe_by"),
        "r10_registration_channel_break": discovery_r10.get("administrative_register_regime_change"),
        "r10_pre_AJ_outcome_category_exposure": discovery_r10.get("outcome_headings_seen_before_AJ"),
        "r11_documentary_status": discovery_r11["status"],
        "r11_documentary_source_count": discovery_r11.get("documentary_source_count"),
        "r11_municipal_documentary_routes": discovery_r11.get("municipal_source_count"),
        "r11_economic_documentary_routes": discovery_r11.get("economic_source_count"),
        "r11_documentary_routes": discovery_r11.get("source_routes",[]),
        "r11_documentary_safe_by": discovery_r11.get("local_audit_safe_by"),
        "r11_rights_by_use_block": discovery_r11.get("rights_by_mere_use_block"),
        "r11_2026_procurement_feed_gap_documented": discovery_r11.get("publisher_2026_feed_gap_known"),
        "r12_documentary_status": discovery_r12["status"],
        "r12_documentary_routes_count": discovery_r12.get("source_count"),
        "r12_normative_route_count": discovery_r12.get("normative_route_count"),
        "r12_appeal_route_count": discovery_r12.get("appeals_route_count"),
        "r12_documentary_routes": discovery_r12.get("source_routes",[]),
        "r12_documentary_safe_by": discovery_r12.get("source_documentary_safe_by"),
        "r12_outcome_selected_csv_not_all_resources": discovery_r12.get("licensed_tarcja_csv_does_not_license_intake"),
        "r12_pan_is_not_incoming_case_register": discovery_r12.get("pan_is_not_intake_denominator"),
        "r12_no_case_vintage_pairs": discovery_r12.get("historical_original_case_vintage_pairs_verified"),
        "r12_revision_instrument_scope": (
            "SYNTHETIC_CAPTURE_AWARE_ROLE_SEPARATE_REPLAY_NOT_REAL_HISTORICAL_WITNESS"
            if discovery_r12["status"]=="R12_DOCUMENTARY_ONLY_NO_ADMISSIBLE_POPULATION"
            else None),
        "r13_documentary_status": discovery_r13["status"],
        "r13_documentary_sources_count": discovery_r13.get("documentary_source_count"),
        "r13_senate_age_routes_count": discovery_r13.get("senate_age_source_count"),
        "r13_legal_transparency_routes_count": discovery_r13.get("review_saip_source_count"),
        "r13_documentary_sources": discovery_r13.get("source_rows",[]),
        "r13_documentary_safe_by": discovery_r13.get("documentary_safe_by"),
        "r13_senate_report_not_petition_count": discovery_r13.get("senate_report_not_petition_count"),
        "r13_saip_not_gaip_denominator": discovery_r13.get("saip_not_all_gaip_claims"),
        "r13_restore_points_are_not_two_originals": discovery_r13.get("restore_point_index_not_real_capture_pair"),
        "r13_contractual_rights_by_access": discovery_r13.get("rights_by_access_may_block_ingestion"),
        "r13_synthetic_cohort_conservation_scope": (
            "SYNTHETIC_REGISTRATION_AT_CUT_PENDENCY_WITH_POSITIVE_WITNESS_NOT_REAL_CENSUS"
            if discovery_r13["status"]=="R13_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED"
            else None),
        "r14_documentary_status": discovery_r14["status"],
        "r14_new_documentary_routes_count": discovery_r14.get("new_documentary_routes_count"),
        "r14_documentary_routes": discovery_r14.get("source_rows",[]),
        "r14_documentary_safe_by": discovery_r14.get("documentary_safe_by"),
        "r14_saip_enrichment_not_additive": discovery_r14.get("existing_saip_enrichment"),
        "r14_documentary_manifest_sha256": discovery_r14.get("manifest_sha256"),
        "r16_documentary_status": discovery_r16["status"],
        "r16_documentary_sources_count": discovery_r16.get("documentary_source_count"),
        "r16_documentary_routes": discovery_r16.get("source_rows",[]),
        "r16_documentary_safe_by": discovery_r16.get("documentary_safe_by"),
        "r16_documentary_manifest_sha256": discovery_r16.get("manifest_sha256"),
        "r16_source_groups_are_not_entry_population": True,
        "denominator_evidence": derive_denominator_evidence(
            real_sources=source_rows,
            as_of=as_of, explicit_current_mode=(as_of is None),
            r9_documentary_status=discovery_r9["status"],
            r9_regional_highlights=discovery_r9.get("regional_highlights",[]),
            r9_national_highlights=discovery_r9.get("national_highlights",[]),
            r10_documentary_status=discovery_r10["status"],
            r10_regional_routes=discovery_r10.get("regional_routes",[]),
            r10_national_routes=discovery_r10.get("national_routes",[]),
            r11_documentary_status=discovery_r11["status"],
            r11_documentary_routes=discovery_r11.get("source_routes",[]),
            r12_documentary_status=discovery_r12["status"],
            r12_documentary_routes=discovery_r12.get("source_routes",[]),
            r13_documentary_status=discovery_r13["status"],
            r13_documentary_routes=discovery_r13.get("source_rows",[]),
            r14_documentary_status=discovery_r14["status"],
            r14_documentary_routes=discovery_r14.get("source_rows",[]),
            r16_documentary_status=discovery_r16["status"],
            r16_documentary_routes=discovery_r16.get("source_rows",[])),
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
