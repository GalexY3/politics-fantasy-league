"""Source-scoped longitudinal readiness, not a real case or outcome API.

The only input evidence is the existing cutoff-checked, SHA-checked local
readiness projection. Unknown and *future* sources have identical replies.
No provider URL, person, source-local record ID or outcome can be retrieved.
"""
from __future__ import annotations

from .procedural_index_contract import GateError, ID
from .source_scope_query import filter_denominator_source


def registration_readiness(*, readiness: dict, source_id: str) -> dict:
    if (type(readiness) is not dict
            or readiness.get("schema") != "pfl.spanish_procedural_population_readiness.v1"
            or readiness.get("reusable_scientific_cohort") is not False
            or type(source_id) is not str or not ID.fullmatch(source_id)):
        raise GateError("UNTRUSTED_REGISTRATION_READINESS_INPUT")
    selected = filter_denominator_source(readiness["denominator_evidence"], source_id)
    rows = selected["reported_sources"]
    # Identical result (including *all* missing values and diagnostics) for
    # an as-yet-undiscovered source and a source that does not exist.
    hidden = {
        "schema": "pfl.registration_readiness_nonadditive.v1",
        "as_of": readiness.get("as_of"),
        "status": "SOURCE_NOT_KNOWN_AT_CUT_OR_UNAVAILABLE",
        "source": None, "population": None, "rights": None,
        "states": None, "clocks": None, "official_links": None,
        "science": {
            "R5_passed": False, "AB_cycles": 0,
            "real_survival_or_feedback_effects": None,
            "scientific_cohort": False,
        },
    }
    if not rows:
        return hidden
    row = rows[0]
    if (row.get("eligible_all_received_denominator") is not None
            or row.get("known_pending_case_count") is not None
            or row.get("known_terminal_case_count") is not None
            or row.get("right_censored_case_count") is not None
            or row.get("case_level_competing_risks_admitted") is not False
            or row.get("official_cross_institution_links_admitted") is not False
            or row.get("date_of_first_publication_verified") is not False):
        raise GateError("UNATTESTED_REGISTRATION_EVIDENCE_PROMOTION")

    # SAIP appeared in R13; R14 may ENRICH that very same source, but must
    # never add another group to the source registry or imply N independence.
    enrichment = None
    if source_id == "GENCAT_SAIP_INITIAL_FILINGS":
        if readiness.get("r14_documentary_status") == "R14_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED":
            enrichment = readiness.get("r14_saip_enrichment_not_additive")
            if (type(enrichment) is not dict
                    or enrichment.get("existing_source_id") != source_id
                    or enrichment.get("rights_by_csv_json_xml_and_restore_verified") is not False
                    or enrichment.get("original_snapshots_compared") != 0):
                raise GateError("UNTRUSTED_SAIP_ENRICHMENT")
    r14_ids = {
        x.get("source_id"): x for x in readiness.get("r14_documentary_routes", [])
        if type(x) is dict
    } if readiness.get("r14_documentary_status") == "R14_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED" else {}
    r16_ids = {
        x.get("source_id"): x for x in readiness.get("r16_documentary_routes", [])
        if type(x) is dict
    } if readiness.get("r16_documentary_status") == "R16_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED" else {}
    rights_scope = (
        r14_ids[source_id]["rights_scope"] if source_id in r14_ids
        else r16_ids[source_id]["rights_scope"] if source_id in r16_ids
        else "GENERAL_TERMS_BIND_ON_ACCESS_ASSET_RIGHTS_UNVERIFIED"
        if source_id == "GENCAT_SAIP_INITIAL_FILINGS" and enrichment is not None
        else "ASSET_LEVEL_RIGHTS_NOT_INDEPENDENTLY_CERTIFIED"
    )
    if source_id in r14_ids:
        if (r14_ids[source_id].get("source_originals_acquired") != 0
                or r14_ids[source_id].get("independent_entry_denominator") is not None):
            raise GateError("R14_ASSET_SOURCE_PROMOTION")
    if source_id in r16_ids:
        if (r16_ids[source_id].get("source_originals_acquired")!=0
                or r16_ids[source_id].get("distribution_rights_certified") is not False
                or r16_ids[source_id].get("independent_entry_denominator") is not None
                or r16_ids[source_id].get("real_terminal_decisions") is not None):
            raise GateError("R16_ASSET_SOURCE_PROMOTION")
    # No asset is made legally acquired by an editorial catalogue licence.
    asset_status = (
        {fmt: "UNVERIFIED_BY_DISTRIBUTION_NO_ORIGINAL_GET"
         for fmt in ("CSV", "JSON", "XML", "RESTORE")}
        if enrichment is not None else
        {fmt: "CATALOGUE_LICENSE_CLAIM_NOT_EXACT_CASE_DISTRIBUTION_PERMISSION"
         for fmt in ("CSV","ODS","XLS","XML")}
        if source_id == "CTPDA_ANDALUCIA_SELECTED_REVIEW_RESOLUTIONS"
           and source_id in r16_ids else {}
    )
    safe_by = (
        readiness.get("r14_documentary_safe_by")
        if (enrichment is not None or source_id in r14_ids)
        else readiness.get("r16_documentary_safe_by")
        if source_id in r16_ids else None
    )
    # Importantly, this is a documentary *knowledge* cutoff, never public
    # first availability of an individual case or a historic source vintage.
    return {
        **hidden,
        "status": "SOURCE_VISIBLE_WITHOUT_CERTIFIED_REGISTRATION_POPULATION",
        "source": {
            "source_id": row["source_id"],
            "institution": row["institution"],
            "observable_unit": row["observable_unit"],
            "source_status": row["source_status"],
            "identification_block": row["principal_identification_block"],
            "source_groups_additive": False,
        },
        "population": {
            "observed_source_local_items_not_denominator": row["observed_source_local_items"],
            "independent_all_received_denominator": None,
            "registered_at_risk_unit_certified": False,
            "eligible_survival_population": None,
            "publisher_catalogue_total_is_not_independent": True,
            "frame_scope_and_entry_rule": row["entry_rule_status"],
            "all_channels_and_inadmissions_verified": False,
            "pagination_verified_for_complete_register": False,
        },
        "rights": {
            "scope": rights_scope,
            "by_distribution": asset_status,
            "exact_original_and_historic_restore_rights_verified": False,
            "terms_or_consent_accepted_by_this_system": False,
            "real_original_ingestion_authorized": False,
        },
        "states": {
            "negative_dispositions_observed": None,
            "pending_known": None,
            "right_censored_known": None,
            "terminal_known": None,
            "unknown_count": None,
            "absence_cannot_infer_pending_rejection_or_censoring": True,
            "competing_risk_cohort_estimable": False,
        },
        "clocks": {
            "documentary_knowledge_safe_by": safe_by,
            "source_event_at": None,
            "editorial_revision_at": None,
            "local_capture_completed_at": None,
            "first_public_at": None,
            "first_public_independent_witness_authenticated": False,
            "two_historical_originals_replayed": False,
            "restore_index_date_is_not_availability": True,
            "saip_catalogue_schema": ({
                "publisher_declared_columns": enrichment["source_declared_columns"],
                "columns_indexed": enrichment["column_names_visible_in_index"],
                "columns_not_verified": enrichment["column_names_not_verified"],
                "editorial_restore_entries": enrichment["restore_point_metadata_entries_visible"],
                "original_restore_pairs": enrichment["original_snapshots_compared"],
            } if enrichment is not None else None),
            "r16_procedural_editorial_conflict": (
                r16_ids[source_id]["editorial_conflict"]
                if source_id in r16_ids else None),
        },
        "official_links": {
            "confirmed_dual_id_edges": None,
            "case_file_to_register_crosswalk_verified": False,
            "cross_institutional_linkage_authorized": False,
            "ambiguous_orphan_links_are_not_negative_events": True,
            "name_title_date_fuzzy_join_forbidden": True,
            "many_to_many_requires_deduplication_by_stage": True,
        },
    }
