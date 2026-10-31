"""SHA-pinned R11 documentary lead classification for the local observatory.

Declared catalogue CC BY or publisher open data is not delegated authority to
accept binding usage terms, inspect original personal data, certify an intake
registry or use outcome data. This adapter reads ONLY a sanitized manifest,
not worker scratch, source case data or future editorial counts.
"""
from __future__ import annotations

from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit

from .procedural_index_contract import utc

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/"data/source_manifests/r11_scoped_documentary_gates_20261031.json"
PIN="e53ac2e61bb8d2cce67afdc1f035dd6b92deabaf0ba6c70611f2a0b41c599c66"
REGIONAL_SOURCE_SHA="ef8815c545e14634a0198ec0a61642344723812a8ae35aea836b39672de6e830"
ECONOMIC_SOURCE_SHA="18fa7bb8d486c87378160a0b999da7c63025a12042d8fd42f55b864d62c7b0b7"
SAFE_BY=datetime(2026,11,1,tzinfo=timezone.utc)
ROUTES={
    "R11-A":("MUNICIPAL_METADATA","FORMAL_ACCESS_REQUEST_CASE",
        "CC_BY_4_CATALOGUE_WITH_BINDING_PORTAL_TERMS",
        "ALL_RECEIVED_CLAIM_NOT_INDEPENDENTLY_RECONCILED"),
    "R11-REGISTRY-COMPARATOR":("MUNICIPAL_METADATA","GENERAL_ADMINISTRATIVE_WRITING",
        "CC_BY_4_WITH_BINDING_PORTAL_TERMS",
        "NO_OFFICIAL_CROSSWALK_TO_AIP_OR_CITIZEN_PROPOSALS"),
    "R11-B":("MUNICIPAL_METADATA","PLATFORM_PUBLISHED_PROPOSAL",
        "CC_BY_4_WITH_BINDING_PORTAL_TERMS",
        "DRAFT_OR_UNPUBLISHED_ENTRY_UNIVERSE_UNVERIFIED"),
    "R11-C":("MUNICIPAL_METADATA","CANODROM_PARTICIPATION_SPACE_PROPOSAL",
        "ODBL_DBCL_PLUS_ACCESS_TERMS",
        "NOT_CITYWIDE_FORMAL_INITIATIVE_REGISTER"),
    "R11_A_PLACSP":("ECONOMIC_ADMINISTRATIVE_METADATA","PUBLIC_TENDER_REVISION",
        "MINISTRY_REUSE_TERMS_BY_USE",
        "REPEATED_ATOM_VERSIONS_AND_2026_COVERAGE_OUTAGE"),
    "R11_B_BDNS":("ECONOMIC_ADMINISTRATIVE_METADATA","PUBLIC_SUBSIDY_CALL",
        "SNPSAP_REUSE_AND_PRIVACY_TERMS",
        "CANONICAL_INSTRUMENTAL_AND_PUBLIC_GRANTS_DIFFER"),
    "R11_C_COOPERATION_REGISTERS":("ECONOMIC_ADMINISTRATIVE_METADATA",
        "SIGNED_REGISTERED_AGREEMENT","RIOJA_CC_BY_AND_DISTRIBUTION_REVIEW",
        "ONE_ROW_PER_PARTICIPANT_AND_NO_FAILED_PROPOSAL_REGISTER"),
}
HOSTS={
    "datos.madrid.es","decidim.canodrom.barcelona",
    "www.hacienda.gob.es","www.infosubvenciones.es","datos.gob.es",
}


def _pairs(pairs):
    out={}
    for k,v in pairs:
        if k in out:
            raise ValueError("R11_DUPLICATE_JSON_KEY")
        out[k]=v
    return out


def _load(path:Path):
    if path.is_symlink() or not path.is_file() or not 3000<path.stat().st_size<10000:
        raise ValueError("R11_SOURCE_METADATA_FILE_INVALID")
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=PIN:
        raise ValueError("R11_REDACTED_MATRIX_SHA_DRIFT")
    return json.loads(raw.decode("utf8"),object_pairs_hook=_pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("R11_BAD_NUMBER")))


def _url_ok(s:str):
    if not isinstance(s,str) or len(s)>1500 or not s.startswith("https://"):
        return False
    try:
        u=urlsplit(s)
        return u.hostname in HOSTS and not u.username and not u.password and u.port is None and not u.fragment
    except ValueError:
        return False


def _valid(obj):
    if (type(obj)!=dict or set(obj)!={
            "schema","discovery_day_utc","upstream_private_worker_sha256",
            "reuser_terms_accepted","real_original_datasets_acquired",
            "real_case_outcomes_read","scientific_cycles_executed",
            "admissible_population_complete","historical_public_witness_verified",
            "publisher_same_origin_counts_independent",
            "case_identifiers_or_person_data_exported","source_routes"}
            or obj["schema"]!="pfl.r11.scoped_documentary_gates_redacted.v1"
            or obj["discovery_day_utc"]!="2026-10-31"
            or obj["upstream_private_worker_sha256"]!={"municipal":REGIONAL_SOURCE_SHA,
                                                      "economic":ECONOMIC_SOURCE_SHA}
            or obj["reuser_terms_accepted"] is not False
            or type(obj["real_original_datasets_acquired"]) is not int
            or obj["real_original_datasets_acquired"]!=0
            or type(obj["real_case_outcomes_read"]) is not int or obj["real_case_outcomes_read"]!=0
            or type(obj["scientific_cycles_executed"]) is not int
            or obj["scientific_cycles_executed"]!=0
            or obj["admissible_population_complete"] is not False
            or obj["historical_public_witness_verified"] is not False
            or obj["publisher_same_origin_counts_independent"] is not False
            or obj["case_identifiers_or_person_data_exported"] is not False):
        raise ValueError("R11_INVALID_RIGHTS_OR_CORPUS_PROMOTION")
    rows=obj["source_routes"]
    if (type(rows)!=list or len(rows)!=7
            or {x["route_id"] for x in rows}!=set(ROUTES)):
        raise ValueError("R11_ROUTES_INCOMPLETE_OR_DUPLICATED")
    public=[]
    for r in rows:
        if (type(r)!=dict or set(r)!={
                "route_id","origin","institution","primary_catalogue_url",
                "institutional_entry_unit","rights_evaluation","independent_frame_block",
                "originals_acquired","reuser_conditions_accepted",
                "case_level_denominator_verified","outcomes_evaluated",
                "historical_first_public_at"}):
            raise ValueError("R11_SOURCE_FIELD_DRIFT")
        kind,unit,rights,reason=ROUTES[r["route_id"]]
        if (r["origin"],r["institutional_entry_unit"],
            r["rights_evaluation"],r["independent_frame_block"])!=(kind,unit,rights,reason):
            raise ValueError("R11_SOURCE_MISCLASSIFIED")
        if (not isinstance(r["institution"],str) or not 4<len(r["institution"])<250
                or not _url_ok(r["primary_catalogue_url"])
                or type(r["originals_acquired"]) is not int or r["originals_acquired"]!=0
                or r["reuser_conditions_accepted"] is not False
                or r["case_level_denominator_verified"] is not None
                or r["outcomes_evaluated"] is not None
                or r["historical_first_public_at"] is not None):
            raise ValueError("R11_SOURCE_RIGHTS_OR_ORIGINAL_PROMOTION")
        public.append({
            "route_id":r["route_id"],"institution":r["institution"],
            "institutional_entry_unit":unit,
            "classification":reason,"rights_gate":rights,
            "dataset_acquired":False,
            "independent_denominator":None,
            "terminal_case_count":None,
            "pending_case_count":None,
            "right_censored_case_count":None,
            "first_public_at":None,
        })
    return public


def status(*,as_of:str|None=None,path:Path|None=None):
    t=utc(as_of) if as_of is not None else None
    base={
        "schema":"pfl.r11.documentary_source_scope.v1","as_of":as_of,
        "real_case_rows_admitted":0,"real_originals_downloaded":0,
        "scientific_cycles":0,"eligible_scientific_denominator":None,
        "real_terminal_outcomes":None,"real_pending_events":None,
        "historical_first_public_at":None,
        "source_groups_additive":False,
    }
    blocked={
        "documentary_source_count":None,"municipal_source_count":None,
        "economic_source_count":None,"source_routes":[],
        "source_matrix_sha256":None,"local_audit_safe_by":None,
        "rights_by_mere_use_block":None,
        "publisher_2026_feed_gap_known":None,
    }
    if t is not None and t<SAFE_BY:
        return {**base,**blocked,"status":"R11_DOCUMENTARY_NOT_KNOWN_AT_CUT"}
    try:
        sources=_valid(_load(path or MANIFEST))
    except (ValueError,OSError,TypeError,KeyError,AttributeError):
        return {**base,**blocked,"status":"R11_DOCUMENTARY_QUARANTINED"}
    return {**base,"status":"R11_DOCUMENTARY_RIGHTS_AND_RISK_FRAME_BLOCKED",
            "documentary_source_count":7,"municipal_source_count":4,
            "economic_source_count":3,
            "source_routes":sources,"source_matrix_sha256":PIN,
            "local_audit_safe_by":SAFE_BY.isoformat(),
            "rights_by_mere_use_block":True,
            "publisher_2026_feed_gap_known":True,
            "provenance_not_case_level_source":True,
            "editorial_counts_cannot_certify_independence":True,
            "boe_is_downstream_not_intake_denominator":True,
            "rights_to_reidentify_people":False,
            "published_tenders_are_not_all_internal_drafts":True}
