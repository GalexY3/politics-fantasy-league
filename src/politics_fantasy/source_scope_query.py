"""Read-only source-selective projection of an already cutoff-gated manifest.

This is not a search over private documents. A source not yet known at the
requested cut has the same reply as a nonexistent source: no source identifiers,
counts, hashes, exclusions or even a future-catalogue membership flag leak.
"""
from __future__ import annotations

from .procedural_index_contract import GateError, ID

SOURCE_FIELDS={
    "source_id","institution","observable_unit","source_status",
    "observed_source_local_items","eligible_all_received_denominator",
    "register_completeness_independently_verified","entry_rule_status",
    "principal_identification_block","known_terminal_case_count",
    "known_pending_case_count","right_censored_case_count",
    "case_level_competing_risks_admitted","date_of_first_publication_verified",
    "official_cross_institution_links_admitted",
    "source_count_not_eligible_risk_population",
}
AGG_FIELDS={
    "schema","eligible_risk_denominator","reported_sources","source_groups_visible",
    "source_groups_additive","index_discovery_without_original_not_counted_as_frame",
    "real_case_outcomes_observed_for_analysis",
    "case_level_right_censoring_observed_for_analysis",
    "risk_by_institution_estimable","post_admission_selection_is_not_pre_mesa_rejection",
    "independent_count_not_derived_from_same_backend",
    "editorial_total_equals_rows_proves_census",
    "boe_only_approved_laws_not_full_intake","first_public_at_historical",
    "synthetic_denominator_comparisons_are_not_empirical","scientific_cycles",
}


def _validate(aggregate: dict) -> list[dict]:
    # This is a *projection* boundary: never allow caller-injected fields to
    # ride along into a public HTTP reply, even if the chosen ID is different.
    if type(aggregate) is not dict or set(aggregate)!=AGG_FIELDS:
        raise GateError("UNTRUSTED_DENOMINATOR_AGGREGATE")
    rows=aggregate["reported_sources"]
    if (type(rows) is not list or len(rows)>100
            or type(aggregate["source_groups_visible"]) is not int):
        raise GateError("UNTRUSTED_DENOMINATOR_SOURCE_ROWS")
    for key in ("eligible_risk_denominator",
                "real_case_outcomes_observed_for_analysis",
                "case_level_right_censoring_observed_for_analysis",
                "independent_count_not_derived_from_same_backend",
                "first_public_at_historical"):
        if aggregate[key] is not None:
            raise GateError("UNATTESTED_DENOMINATOR_AGGREGATE_PROMOTION")
    if (aggregate["scientific_cycles"]!=0
            or aggregate["source_groups_additive"] is not False
            or aggregate["risk_by_institution_estimable"] is not False):
        raise GateError("UNATTESTED_DENOMINATOR_AGGREGATE_PROMOTION")
    ids=set()
    for row in rows:
        if type(row) is not dict or set(row)!=SOURCE_FIELDS:
            raise GateError("UNTRUSTED_DENOMINATOR_SOURCE_FIELDS")
        source_id=row["source_id"]
        if not isinstance(source_id,str) or not ID.fullmatch(source_id):
            raise GateError("UNTRUSTED_DENOMINATOR_SOURCE_ID")
        if source_id in ids:
            raise GateError("DUPLICATE_INSTITUTIONAL_SOURCE_ID")
        ids.add(source_id)
        observed=row["observed_source_local_items"]
        if observed is not None and (type(observed) is not int or observed<0):
            raise GateError("BAD_SOURCE_LOCAL_OBSERVATION")
        if (any(row[k] is not None for k in (
                "eligible_all_received_denominator","known_terminal_case_count",
                "known_pending_case_count","right_censored_case_count"))
                or any(row[k] is not False for k in (
                    "register_completeness_independently_verified",
                    "case_level_competing_risks_admitted",
                    "date_of_first_publication_verified",
                    "official_cross_institution_links_admitted"))
                or row["source_count_not_eligible_risk_population"] is not True):
            raise GateError("UNATTESTED_DENOMINATOR_SOURCE_PROMOTION")
    if aggregate["source_groups_visible"]!=len(rows):
        raise GateError("UNTRUSTED_DENOMINATOR_SOURCE_ROWS")
    return rows


def filter_denominator_source(aggregate: dict, source_id: str | None) -> dict:
    if (not isinstance(aggregate,dict)
            or aggregate.get("schema")!="pfl.denominator_evidence_nonadditive.v1"):
        raise GateError("UNTRUSTED_DENOMINATOR_AGGREGATE")
    rows=_validate(aggregate)
    if source_id is None:
        return aggregate
    if not isinstance(source_id,str) or not ID.fullmatch(source_id):
        raise GateError("INVALID_PUBLIC_SOURCE_ID")
    matches=[x for x in rows if isinstance(x,dict) and x.get("source_id")==source_id]
    if len(matches)>1:
        raise GateError("DUPLICATE_INSTITUTIONAL_SOURCE_ID")
    selected=matches[:1]
    return {
        **{key:value for key,value in aggregate.items()
           if key not in {"reported_sources","source_groups_visible"}},
        "reported_sources":selected,
        "source_groups_visible":len(selected),
        "selection_status":("SOURCE_VISIBLE_WITH_LIMITATIONS" if selected
                            else "SOURCE_NOT_KNOWN_AT_CUT_OR_UNAVAILABLE"),
        "eligible_risk_denominator":None,
        "real_case_outcomes_observed_for_analysis":None,
        "case_level_right_censoring_observed_for_analysis":None,
    }
