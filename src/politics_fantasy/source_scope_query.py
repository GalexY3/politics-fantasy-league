"""Read-only source-selective projection of an already cutoff-gated manifest.

This is not a search over private documents. A source not yet known at the
requested cut has the same reply as a nonexistent source: no source identifiers,
counts, hashes, exclusions or even a future-catalogue membership flag leak.
"""
from __future__ import annotations

from .procedural_index_contract import GateError, ID


def filter_denominator_source(aggregate: dict, source_id: str | None) -> dict:
    if not isinstance(aggregate,dict) or aggregate.get("schema")!="pfl.denominator_evidence_nonadditive.v1":
        raise GateError("UNTRUSTED_DENOMINATOR_AGGREGATE")
    if source_id is None:
        return aggregate
    if not isinstance(source_id,str) or not ID.fullmatch(source_id):
        raise GateError("INVALID_PUBLIC_SOURCE_ID")
    rows=aggregate.get("reported_sources")
    if not isinstance(rows,list) or len(rows)>100:
        raise GateError("UNTRUSTED_DENOMINATOR_SOURCE_ROWS")
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
