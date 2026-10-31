"""R10 legal/selection discoveries under SHA and conservative as-of gates.

Only the *sanitized* metadata manifest is read; worker source matrices and
institutional PDF/HTML originals remain outside Git and unadmitted. Published
metadata does not convey source-distribution rights, first public availability,
complete denominators, process outcomes or historical publication vintages.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit

from .procedural_index_contract import utc

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/"data/source_manifests/r10_documentary_constraints_redacted_20261031.json"
PIN="c81f3524098e505f332af05163902e777feb322c0b76dee65543f4bee82e0a19"
REGIONAL_UPSTREAM="16a34a6e596b00212ca84f89bbc0e17f9b3b77b32d363387790ce60ab11583d2"
NATIONAL_UPSTREAM="d7ec41fd797ba91cb9f416bde1ea238e9f8b29a68847f984b5649783c0967f2d"
SAFE_BY=datetime(2026,11,1,tzinfo=timezone.utc)
EXPECTED_REGIONAL={
    "andalucia_ilpa_xii_jea":"POST_MESA_REFERRED_ONLY_NOT_ALL_RECEIVED",
    "andalucia_jea_rights":"NO_EXPLICIT_OPEN_ILPA_DISTRIBUTION_RIGHTS",
    "andalucia_agrupa_march2026":"REGISTRATION_CHANNEL_REGIME_BREAK_NOT_SOURCE_VINTAGE",
    "castilla_y_leon_xi_dissolution_feb2026":"PENDING_AT_DISSOLUTION_IS_SURVIVOR_SELECTED_STOCK",
    "castilla_y_leon_xii_continuity_april2026":"TRANSFER_NOTICE_NOT_COMPLETE_ORIGINAL_ENTRY_FRAME",
    "castilla_y_leon_rights_and_ILP_protocol":"GENERAL_PAGE_RIGHTS_NOT_DATASET_REUSE",
}
EXPECTED_NATIONAL={
    "R10_A_CTBG_APPEALS":"APPEALS_RECEIVED_DISTINCT_FROM_RESOLUTIONS_AND_INITIAL_REQUESTS",
    "R10_B_CNMC_PUBLIC_CONSULTATIONS":"PUBLISHED_CONTRIBUTIONS_CONDITIONED_ON_CONFIDENTIALITY",
    "R10_C_BASQUE_PARLIAMENT_REGISTER":"UPSTREAM_REGISTRY_LEGAL_BUT_NOT_PUBLIC_COMPLETE_DATASET",
}
REGIONAL_SHOW={
    "andalucia_ilpa_xii_jea","andalucia_agrupa_march2026",
    "castilla_y_leon_xi_dissolution_feb2026",
}
HOSTS={
    "juntaelectoral.parlamentodeandalucia.es","www.parlamentodeandalucia.es",
    "www.ccyl.es",
}


def _pairs(pairs):
    seen={}
    for k,v in pairs:
        if k in seen:
            raise ValueError("R10_DUPLICATED_JSON_KEY")
        seen[k]=v
    return seen


def _document(path:Path):
    if path.is_symlink() or not path.is_file() or not 4000<path.stat().st_size<9000:
        raise ValueError("R10_METADATA_NOT_FOUND_OR_OVERSIZED")
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=PIN:
        raise ValueError("R10_METADATA_SHA_DRIFT")
    return json.loads(raw.decode("utf8"),object_pairs_hook=_pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("R10_BAD_NUMBER")))


def _url_valid(url):
    if not isinstance(url,str) or not url.startswith("https://") or len(url)>1500:
        return False
    try:
        p=urlsplit(url)
        return (p.hostname in HOSTS and not p.username and not p.password
                and not p.fragment and p.port is None)
    except ValueError:
        return False


def _check(doc):
    if (type(doc)!=dict or set(doc)!={
            "schema","audit_day_utc","upstream_private_worker_matrices_sha256",
            "no_source_ids_or_outcome_values_exported",
            "real_source_originals_downloaded","AB_cycles_executed",
            "pre_AJ_outcome_category_headings_seen",
            "all_received_denominator_certified","historic_first_public_at_verified",
            "and_unverified_agrupa_effective_on",
            "and_measurement_channel_overlap_requires_controls",
            "regional_documentary_assets","distinct_institutional_entry_routes"}
            or doc["schema"]!="pfl.r10.documentary_constraints_redacted.v1"
            or doc["audit_day_utc"]!="2026-10-31"
            or doc["upstream_private_worker_matrices_sha256"]!={"regional":REGIONAL_UPSTREAM,"national":NATIONAL_UPSTREAM}
            or doc["no_source_ids_or_outcome_values_exported"] is not True
            or type(doc["real_source_originals_downloaded"]) is not int
            or doc["real_source_originals_downloaded"]!=0
            or type(doc["AB_cycles_executed"]) is not int or doc["AB_cycles_executed"]!=0
            or doc["pre_AJ_outcome_category_headings_seen"] is not True
            or doc["all_received_denominator_certified"] is not False
            or doc["historic_first_public_at_verified"] is not False
            or doc["and_unverified_agrupa_effective_on"]!="2026-03-20"
            or doc["and_measurement_channel_overlap_requires_controls"] is not True):
        raise ValueError("R10_METADATA_PROMOTED_OR_SCHEMA_CHANGED")
    regions=doc["regional_documentary_assets"]
    nations=doc["distinct_institutional_entry_routes"]
    if (type(regions)!=list or len(regions)!=6
            or {r["source_id"] for r in regions}!=set(EXPECTED_REGIONAL)
            or type(nations)!=list or len(nations)!=3
            or {r["source_id"] for r in nations}!=set(EXPECTED_NATIONAL)):
        raise ValueError("R10_METADATA_SCOPE_CHANGED")
    result_regions=[]
    for r in regions:
        if (type(r)!=dict or set(r)!={
                "source_id","institution","official_document_url","scope_failure_code",
                "documentary_only","no_original_get","all_received_register_count",
                "data_distribution_licence","known_case_decisions","first_public_at"}
                or r["scope_failure_code"]!=EXPECTED_REGIONAL[r["source_id"]]
                or r["documentary_only"] is not True or r["no_original_get"] is not True
                or r["all_received_register_count"] is not None
                or r["data_distribution_licence"] is not None
                or r["known_case_decisions"] is not None
                or r["first_public_at"] is not None
                or not _url_valid(r["official_document_url"])):
            raise ValueError("R10_REGIONAL_SOURCE_OR_RIGHTS_DRIFT")
        if r["source_id"] in REGIONAL_SHOW:
            result_regions.append({
                "source_id":r["source_id"],"institution":r["institution"],
                "scope_failure":r["scope_failure_code"],
                "original_acquired":False,"licence_verified":False,
                "all_received_denominator":None,
            })
    result_nations=[]
    for r in nations:
        if (type(r)!=dict or set(r)!={
                "source_id","institution","entry_unit","selection_failure_code",
                "rights_to_acquire_case_source","all_received_register_count",
                "real_original_sha256","independent_entry_denominator","first_public_at"}
                or r["selection_failure_code"]!=EXPECTED_NATIONAL[r["source_id"]]
                or r["rights_to_acquire_case_source"] is not False
                or r["all_received_register_count"] is not None
                or r["real_original_sha256"] is not None
                or r["independent_entry_denominator"] is not None
                or r["first_public_at"] is not None):
            raise ValueError("R10_NATIONAL_SOURCE_OR_RIGHTS_DRIFT")
        result_nations.append({
            "source_id":r["source_id"],"institution":r["institution"],
            "entry_unit":r["entry_unit"],"scope_failure":r["selection_failure_code"],
            "original_acquired":False,"licence_verified":False,
            "all_received_denominator":None,
        })
    return result_regions,result_nations


def status(*,as_of:str|None=None,path:Path|None=None):
    cut=utc(as_of) if as_of is not None else None
    base={
        "schema":"pfl.r10.documentary_limits.v1","as_of":as_of,
        "historical_first_public_at":None,
        "science_denominator":None,
        "right_censored_real_cases":None,
        "terminal_real_events":None,
        "new_originals_acquired":0,
        "AB_cycles":0,
        "source_groups_additive":False,
    }
    if cut is not None and cut<SAFE_BY:
        return {**base,"status":"R10_DOCUMENTARY_NOT_KNOWN_AT_CUT",
                "regional_total":None,"national_routes_total":None,
                "regional_routes":[],"national_routes":[],
                "manifest_sha256":None,"local_documentary_safe_by":None,
                "administrative_register_regime_change":None,
                "outcome_headings_seen_before_AJ":None}
    try:
        regions,nations=_check(_document(path or MANIFEST))
    except (ValueError,OSError,TypeError,KeyError,AttributeError):
        return {**base,"status":"R10_DOCUMENTARY_QUARANTINED",
                "regional_total":None,"national_routes_total":None,
                "regional_routes":[],"national_routes":[],
                "manifest_sha256":None,"local_documentary_safe_by":None,
                "administrative_register_regime_change":None,
                "outcome_headings_seen_before_AJ":None}
    return {**base,"status":"R10_DOCUMENTARY_ONLY_NO_RISK_FRAME",
            "regional_total":6,"national_routes_total":3,
            "regional_routes":regions,"national_routes":nations,
            "manifest_sha256":PIN,"local_documentary_safe_by":SAFE_BY.isoformat(),
            "administrative_register_regime_change":{
                "institution":"Parlamento de Andalucía",
                "reported_channel_rule_effective_on":"2026-03-20",
                "date_from_indexed_official_document_not_sha_replayed":True,
                "electronically_registered_and_paper_parallel_until_verified":True,
                "historical_first_public_at":None,
                "is_observed_change_in_political_behavior":False,
            },
            "outcome_headings_seen_before_AJ":True,
            "pre_mesa_and_post_referral_populations_must_not_be_summed":True,
            "dissolution_pending_stock_not_total_prior_initiatives":True,
            "ctbg_resolution_not_necessarily_one_claim":True,
            "cnmc_published_document_not_one_received_submitted_comment":True,
        }
