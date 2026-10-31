"""Non-additive, provenance-aware population evidence for the local observatory.

Works only with already SHA-checked, cutoff-gated PFL readiness source rows.
No outcome file is opened. Missing institutional denominators, unresolved
pending states and censoring are NULL, never zero. The entries are distinct
objects; a source-local count is NOT a denominator of all registered cases.
"""
from __future__ import annotations

from .procedural_index_contract import GateError


def _candidate(identifier:str, institution:str, unit:str, source_status:str,
               observed:int|None, entry_rule:str, failure:str):
    if observed is not None and (type(observed) is not int or observed<0):
        raise GateError("BAD_OBSERVED_COUNT_NOT_CENSUS")
    return {
        "source_id":identifier,"institution":institution,"observable_unit":unit,
        "source_status":source_status,
        "observed_source_local_items":observed,
        "eligible_all_received_denominator":None,
        "register_completeness_independently_verified":False,
        "entry_rule_status":entry_rule,
        "principal_identification_block":failure,
        "known_terminal_case_count":None,
        "known_pending_case_count":None,
        "right_censored_case_count":None,
        "case_level_competing_risks_admitted":False,
        "date_of_first_publication_verified":False,
        "official_cross_institution_links_admitted":False,
        "source_count_not_eligible_risk_population":True,
    }


def derive_denominator_evidence(*, real_sources:list[dict],
                                r9_documentary_status:str,
                                r9_regional_highlights:list[dict],
                                r9_national_highlights:list[dict],
                                r10_documentary_status:str="R10_DOCUMENTARY_NOT_KNOWN_AT_CUT",
                                r10_regional_routes:list[dict]|None=None,
                                r10_national_routes:list[dict]|None=None,
                                r11_documentary_status:str="R11_DOCUMENTARY_NOT_KNOWN_AT_CUT",
                                r11_documentary_routes:list[dict]|None=None,
                                r12_documentary_status:str="R12_NOT_KNOWN_AT_CUT",
                                r12_documentary_routes:list[dict]|None=None,
                                r13_documentary_status:str="R13_NOT_KNOWN_AT_CUT",
                                r13_documentary_routes:list[dict]|None=None,
                                r14_documentary_status:str="R14_NOT_KNOWN_AT_CUT",
                                r14_documentary_routes:list[dict]|None=None) -> dict:
    if (not isinstance(real_sources,list) or len(real_sources)!=3
            or [x.get("source_id") for x in real_sources]!=[
                "PARCAN_SOURCE_LOCAL","PARLAMENT_CATALUNYA_SIAP",
                "CONGRESO_XV_CANDIDATE_INDICES"]):
        raise GateError("REAL_SOURCE_REGISTRY_UNRECOGNIZED")
    a,b,_=real_sources
    # Even the *reason* for exclusion and the count of source catalogues can
    # reveal knowledge obtained at a later capture. Do not output a document
    # at an old cut merely because its source name is hard-coded in Python.
    groups=[]
    if a["observed_metadata_rows"] is not None:
        groups.append(_candidate("PARCAN_SOURCE_LOCAL",a["institution"],a["unit"],
                       a["provenance_status"],a["observed_metadata_rows"],
                       "F_CREACION_IS_NOT_PUBLICATION_OR_PRE_MESA_REGISTRATION",
                       "NO_INDEPENDENT_ALL_RECEIVED_FRAME_OR_OUTCOMES"))
    if b["observed_metadata_rows"] is not None:
        groups.append(_candidate("PARLAMENT_CATALUNYA_SIAP",b["institution"],b["unit"],
                       b["provenance_status"],b["observed_metadata_rows"],
                       "INDEX_LINK_NOT_REGISTERED_INTAKE",
                       "ONLY_ONE_OF_44_PAGES_AND_NO_ENTRY_BOOK"))
    # A Congress discovery without any admitted original is not even a
    # source-local frame, so it must not be counted in this table.
    if r9_documentary_status=="R9_DISCOVERY_ONLY_RIGHTS_AND_DENOMINATORS_BLOCKED":
        if not isinstance(r9_regional_highlights,list) or not isinstance(r9_national_highlights,list):
            raise GateError("R9_SOURCE_DOCUMENTARY_SCOPE_UNEXPECTED")
        for e in r9_regional_highlights:
            if not e.get("documentary_only") or e.get("source_eligible") is not False:
                raise GateError("R9_SOURCE_SCOPING_PROMOTION")
            groups.append(_candidate(e["source_id"],e["institution"],
                e["documentary_limit"],"DOCUMENTARY_ONLY_NO_RAW",None,
                "REGISTRATION_OR_ADMISSION_ENTRY_RULE_UNATTESTED",
                "LICENCE_REGISTRY_TOTAL_OR_VINTAGES_UNVERIFIED"))
        for e in r9_national_highlights:
            if e.get("source_eligible") is not False:
                raise GateError("R9_NATIONAL_SOURCE_PROMOTION")
            groups.append(_candidate(e["source_id"],e["institution"],
                e["documentary_unit"],"DOCUMENTARY_ONLY_NO_RAW",None,
                "INSTITUTIONAL_INTAKE_GRAIN_DISTINCT",
                "NO_CROSS_INSTITUTION_OR_SAME_PUBLISHER_INDEPENDENT_CENSUS"))
    elif r9_documentary_status not in {
            "R9_DISCOVERY_NOT_KNOWN_AT_CUT","R9_DOCUMENTARY_SOURCE_QUARANTINED"}:
        raise GateError("UNKNOWN_R9_DISCOVERY_STATUS")
    if r10_documentary_status=="R10_DOCUMENTARY_ONLY_NO_RISK_FRAME":
        if (not isinstance(r10_regional_routes,list) or len(r10_regional_routes)!=3
                or not isinstance(r10_national_routes,list) or len(r10_national_routes)!=3):
            raise GateError("R10_DOCUMENTARY_ROUTE_SCOPE_INVALID")
        for e in r10_regional_routes:
            if (e.get("original_acquired") is not False
                    or e.get("licence_verified") is not False
                    or e.get("all_received_denominator") is not None):
                raise GateError("R10_DOCUMENTARY_CANNOT_PROMOTE_SOURCE")
            groups.append(_candidate(e["source_id"],e["institution"],
                e["scope_failure"],"DOCUMENTARY_ONLY_NO_RAW",None,
                "ENTRY_STAGE_OR_REGIME_DEPENDENT",
                "NO_INDEPENDENT_REGISTER_TOTAL_OR_HISTORICAL_ORIGINALS"))
        for e in r10_national_routes:
            if (e.get("original_acquired") is not False
                    or e.get("licence_verified") is not False
                    or e.get("all_received_denominator") is not None):
                raise GateError("R10_DOCUMENTARY_CANNOT_PROMOTE_SOURCE")
            groups.append(_candidate(e["source_id"],e["institution"],
                e["entry_unit"],"DOCUMENTARY_ONLY_NO_RAW",None,
                "INSTITUTIONAL_UNIT_DISTINCT_FROM_PARLIAMENTARY_REGISTRATION",
                "REUSE_OR_COMPLETE_ENTRY_POPULATION_NOT_CERTIFIED"))
    elif r10_documentary_status not in {
            "R10_DOCUMENTARY_NOT_KNOWN_AT_CUT","R10_DOCUMENTARY_QUARANTINED"}:
        raise GateError("R10_DOCUMENTARY_STATUS_INVALID")
    if r11_documentary_status=="R11_DOCUMENTARY_RIGHTS_AND_RISK_FRAME_BLOCKED":
        if not isinstance(r11_documentary_routes,list) or len(r11_documentary_routes)!=7:
            raise GateError("R11_SOURCE_ROUTE_COUNT_MISMATCH")
        for row in r11_documentary_routes:
            if (row.get("dataset_acquired") is not False
                    or row.get("independent_denominator") is not None
                    or row.get("terminal_case_count") is not None
                    or row.get("first_public_at") is not None):
                raise GateError("R11_SOURCE_PROMOTION_FORBIDDEN")
            groups.append(_candidate(
                row["route_id"],row["institution"],row["institutional_entry_unit"],
                "DOCUMENTARY_ONLY_NO_ORIGINAL_OR_ACCEPTED_TERMS",None,
                "REPORTED_PUBLISHER_FRAME_ONLY",
                row["classification"]))
    elif r11_documentary_status not in {
            "R11_DOCUMENTARY_NOT_KNOWN_AT_CUT","R11_DOCUMENTARY_QUARANTINED"}:
        raise GateError("R11_DOCUMENTARY_STATUS_INVALID")
    if r12_documentary_status=="R12_DOCUMENTARY_ONLY_NO_ADMISSIBLE_POPULATION":
        if type(r12_documentary_routes) is not list or len(r12_documentary_routes)!=6:
            raise GateError("R12_DOCUMENTARY_EXPECTED_SIX_DISTINCT_SOURCES")
        for row in r12_documentary_routes:
            if (row.get("original_available") is not False
                    or row.get("independent_entry_denominator") is not None
                    or row.get("terminal_case_count") is not None
                    or row.get("first_public_at") is not None):
                raise GateError("R12_DOCUMENTARY_CANNOT_BECOME_RISK_FRAME")
            groups.append(_candidate(
                row["source_id"],row["source_id"],row["documentary_unit"],
                "DOCUMENTARY_SCOPE_ONLY_NO_CASE_OR_ARCHIVAL_ORIGINAL",None,
                "PLANNED_INVITATION_SELECTED_STAGE_OR_APPEAL_DECISION",
                row["risk_frame_limitation"]))
    elif r12_documentary_status not in {"R12_NOT_KNOWN_AT_CUT","R12_SOURCE_QUARANTINED"}:
        raise GateError("R12_DOCUMENTARY_STATUS_INVALID")
    if r13_documentary_status=="R13_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED":
        if type(r13_documentary_routes) is not list or len(r13_documentary_routes)!=8:
            raise GateError("R13_EIGHT_DOCUMENTARY_LEADS_NOT_CASE_COUNTS")
        for row in r13_documentary_routes:
            if (row.get("source_originals_acquired")!=0
                    or row.get("complete_registered_risk_denominator") is not None
                    or row.get("pending_or_censored_cases") is not None
                    or row.get("terminal_outcomes") is not None
                    or row.get("historical_first_public_at") is not None):
                raise GateError("R13_DOCUMENTARY_SOURCE_OUTCOME_PROMOTION")
            groups.append(_candidate(
                row["source_id"],row["source_id"],row["unit"],
                "DOCUMENTARY_DISCOVERY_ONLY_NO_ADMISSIBLE_ORIGINAL",None,
                "PETITION_REPORT_SAIP_FILING_OR_SELECTED_REVIEW_NOT_ADDITIVE",
                row["identification_limit"]))
    elif r13_documentary_status not in {"R13_NOT_KNOWN_AT_CUT","R13_SOURCE_QUARANTINED"}:
        raise GateError("R13_DOCUMENTARY_STATUS_INVALID")
    if r14_documentary_status=="R14_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED":
        if type(r14_documentary_routes) is not list or len(r14_documentary_routes)!=4:
            raise GateError("R14_EXPECTED_FOUR_NEW_DOCUMENTARY_ROUTES")
        for row in r14_documentary_routes:
            if (row.get("source_originals_acquired") != 0
                    or row.get("independent_entry_denominator") is not None
                    or row.get("real_terminal_decisions") is not None
                    or row.get("real_pending_or_censored") is not None
                    or row.get("first_public_at") is not None):
                raise GateError("R14_DOCUMENTARY_SOURCE_OUTCOME_PROMOTION")
            groups.append(_candidate(
                row["source_id"],row["institution"],row["documentary_unit"],
                "DOCUMENTARY_METADATA_ONLY_NO_AUTHORIZED_ORIGINAL",None,
                "SAIP_SCOPE_MUNICIPAL_REGISTER_OR_AGGREGATES_NOT_ADDITIVE",
                row["limitation"]))
    elif r14_documentary_status not in {"R14_NOT_KNOWN_AT_CUT","R14_SOURCE_QUARANTINED"}:
        raise GateError("R14_DOCUMENTARY_STATUS_INVALID")
    return {
        "schema":"pfl.denominator_evidence_nonadditive.v1",
        "eligible_risk_denominator":None,
        "reported_sources":groups,
        "source_groups_visible":len(groups),
        "source_groups_additive":False,
        "index_discovery_without_original_not_counted_as_frame":True,
        "real_case_outcomes_observed_for_analysis":None,
        "case_level_right_censoring_observed_for_analysis":None,
        "risk_by_institution_estimable":False,
        "post_admission_selection_is_not_pre_mesa_rejection":True,
        "independent_count_not_derived_from_same_backend":None,
        "editorial_total_equals_rows_proves_census":False,
        "boe_only_approved_laws_not_full_intake":True,
        "first_public_at_historical":None,
        "synthetic_denominator_comparisons_are_not_empirical":True,
        "scientific_cycles":0,
    }
