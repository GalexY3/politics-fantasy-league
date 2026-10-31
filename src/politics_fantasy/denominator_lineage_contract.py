"""Conservative cross-source denominator lineage checks.

Editorial count agreement is not independent population confirmation.
The comparison accepts untrusted documentary claims, and has no API that
promotes them into an authenticated risk set. It needs a separate trusted
server-side registry of complete originals, rights and population rules.
"""
from __future__ import annotations

from dataclasses import dataclass

from .procedural_index_contract import GateError, NAMESPACE, ID, SHA, day, utc

ENTRY_RULES={"ALL_RECEIVED_REGISTRATION","PRESENTATION_FIRST","ADMISSION_FIRST"}
UNIT_KINDS={
    "REGISTRY_INITIAL_WRITING","JURISDICTIONAL_MATTER","PARLIAMENTARY_INITIATIVE",
    "PUBLISHED_EXPEDIENTE","OFFICIAL_AGREEMENT","INSTITUTIONAL_CONSULTATION",
    "INDIVIDUAL_COMPLAINT","SOURCE_INDEX_LINK",
}
CLAIM_BASES={"EDITORIAL_PAGE_COUNT","CATALOGUE_REPORTED_COUNT",
             "RETROSPECTIVE_SUMMARY","REGISTRY_PUBLISHED_TOTAL"}


@dataclass(frozen=True)
class PopulationTarget:
    institution: str
    family: str
    legislature_or_regime: str
    entry_rule: str
    unit: str
    window_first_day: str
    window_last_day: str

    def __post_init__(self):
        if (not isinstance(self.institution,str) or not NAMESPACE.fullmatch(self.institution)
                or not isinstance(self.family,str) or not NAMESPACE.fullmatch(self.family)
                or not isinstance(self.legislature_or_regime,str)
                or not ID.fullmatch(self.legislature_or_regime)
                or self.entry_rule not in ENTRY_RULES or self.unit not in UNIT_KINDS
                or day(self.window_first_day) > day(self.window_last_day)):
            raise GateError("INVALID_POPULATION_TARGET")


@dataclass(frozen=True)
class SourceTotalClaim:
    source_id: str
    target: PopulationTarget
    reported_count: int
    reporting_issuer: str
    backend_lineage: str | None
    claim_basis: str
    original_sha256_claim: str | None = None
    historical_first_public_at: None = None

    def __post_init__(self):
        if (not isinstance(self.source_id,str) or not ID.fullmatch(self.source_id)
                or not isinstance(self.target,PopulationTarget)
                or type(self.reported_count) is not int
                or not 0 <= self.reported_count <= 10_000_000
                or not isinstance(self.reporting_issuer,str)
                or not NAMESPACE.fullmatch(self.reporting_issuer)
                or (self.backend_lineage is not None
                    and (not isinstance(self.backend_lineage,str)
                         or not NAMESPACE.fullmatch(self.backend_lineage)))
                or self.claim_basis not in CLAIM_BASES
                or (self.original_sha256_claim is not None
                    and (not isinstance(self.original_sha256_claim,str)
                         or not SHA.fullmatch(self.original_sha256_claim)))
                or self.historical_first_public_at is not None):
            raise GateError("INVALID_OR_PROMOTED_SOURCE_TOTAL_CLAIM")


def compare_total_claims(*, first: SourceTotalClaim, second: SourceTotalClaim,
                         query_as_of: str | None = None,
                         locally_known_safe_by: str | None = None) -> dict:
    """Compare claims only; not a certificate of independent coverage.

    Even two publishers that claim distinct backend lineages are NOT
    authenticated, and equal numbers prove neither eligibility nor rights.
    """
    if not isinstance(first,SourceTotalClaim) or not isinstance(second,SourceTotalClaim):
        raise GateError("COMPARISON_REQUIRES_TWO_SOURCE_CLAIMS")
    if first.source_id == second.source_id:
        raise GateError("SELF_WITNESS_REPLAY")
    if (query_as_of is None) != (locally_known_safe_by is None):
        raise GateError("INCOMPLETE_TIME_ENVELOPE")
    if query_as_of is not None:
        cut=utc(query_as_of)
        earliest=utc(locally_known_safe_by)
        if cut<earliest:
            return {
                "schema":"pfl.denominator_independence_comparison.v1",
                "status":"SOURCE_CLAIMS_NOT_KNOWN_AT_CUT",
                "frame_compatible":None,"editorial_counts_equal":None,
                "source_claims_visible":False,
                "counter_claims":None,"backend_relation":None,
                "independent_denominator_certified":False,
                "eligible_risk_population":None,
                "first_public_at":None,"scientific_cycles":0,
            }
    compatible=first.target==second.target
    if not compatible:
        verdict="INCOMPATIBLE_UNITS_SCOPE_OR_ENTRY_RULE"
        lineage=None
    elif first.reporting_issuer==second.reporting_issuer:
        verdict="SAME_ISSUER_NOT_EXTERNAL_CORROBORATION"
        lineage="SAME_REPORTING_ISSUER"
    elif first.backend_lineage is None or second.backend_lineage is None:
        verdict="UNKNOWN_BACKEND_DEPENDENCE"
        lineage="UNATTESTED"
    elif first.backend_lineage==second.backend_lineage:
        verdict="SAME_BACKEND_RESTATEMENT"
        lineage="SHARED_EDITORIAL_ROOT"
    else:
        verdict="DIFFERENT_DECLARED_SYSTEMS_STILL_UNCERTIFIED"
        lineage="SEPARATION_CLAIM_NOT_AUTHENTICATED"
    return {
        "schema":"pfl.denominator_independence_comparison.v1",
        "status":verdict,
        "frame_compatible":compatible,
        "editorial_counts_equal":first.reported_count==second.reported_count,
        "source_claims_visible":True,
        "counter_claims":(first.reported_count,second.reported_count),
        "backend_relation":lineage,
        "independent_denominator_certified":False,
        "eligible_risk_population":None,
        "verified_case_level_linkage":False,
        "historical_publication_verified":False,
        "rights_to_use_cases_verified":False,
        "first_public_at":None,
        "scientific_cycles":0,
        "note":"Count concordance or provenance labels are not independent registry evidence.",
    }
