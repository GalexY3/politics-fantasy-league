"""R9 SHA-pinned, privacy-redacted institutional discovery, *not* source data.

These two manifests were derived by a deterministic whitelist from locally
hash-verified workers' scratch documents. PPLI/register IDs and all reported
new-case numbers were deliberately omitted. R9 discovered source structures,
not raw historical revisions, an all-received risk set or reusable outcomes.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit

from .procedural_index_contract import utc

ROOT=Path(__file__).resolve().parents[2]
REGIONAL=ROOT/"data/source_manifests/r9_regional_documentary_redacted_20261031.json"
NATIONAL=ROOT/"data/source_manifests/r9_national_documentary_redacted_20261031.json"
REGIONAL_SHA="ceac91495ce9f6c8a4e16bbb8ca2dfd5aed968e981513e081687319c4e6b59fc"
NATIONAL_SHA="7f3f224f63422e6e29de50539ae84dba44495d0b2585ab5795502bb465288d4a"
UPSTREAM_REGION_SHA="6a64b4b356f5798f859f8c4ebdb288f4f5ad048a1d3e8a4fdff9aeba2ad438a1"
UPSTREAM_NATIONAL_SHA="c2546633789b56723e5dc815cc227da7e3b2cbe536c8dc75819edb950320e32c"
SAFE_BY=datetime(2026,11,1,tzinfo=timezone.utc)
REGION_IDS={
    "galicia_ix_ppli_retrospective","galicia_x_ppli_retrospective",
    "galicia_xi_partial_semester_reports","galicia_legal_process_and_nonparliamentary_false_positive",
    "valencia_ilp_html_list","valencia_register_vs_initiatives_functions",
    "castilla_la_mancha_seres","basque_parliament_ilp_open_xml_unverified",
}
NATIONAL_IDS={
    "TC_STATISTICAL_SERIES","TC_MEMORIA_2025_HTML","TC_REGISTRY_INITIAL_WRITINGS_2025",
    "TC_MEMORIA_2025_PDF_NOT_READ","DP_ANNUAL_REPORT_2025_PORTAL",
    "DP_STATISTICAL_ANNEX_2025_PDF_NOT_READ","DP_ANNUAL_REPORT_2024_PORTAL",
    "DP_GENERAL_TERMS","DP_REPORT_NEWS_SAME_ISSUER_2025",
    "JEC_PUBLIC_DOCTRINE_AGREEMENTS","JEC_PUBLIC_PORTAL_COPYRIGHT",
}
HOSTS={
    "www.parlamentodegalicia.gal","www.lex.gal","abertos.xunta.gal",
    "www.cortsvalencianes.es","sede.cortsvalencianes.es",
    "sede.cortesclm.es","www.cortesclm.es",
    "legal.legebiltzarra.eus","egoitza.legebiltzarra.eus",
    "www.boe.es","opendata.euskadi.eus",
    "www.tribunalconstitucional.es","www.defensordelpueblo.es",
    "www.juntaelectoralcentral.es",
}
REGIONAL_VISIBLE={
    "galicia_ix_ppli_retrospective","galicia_x_ppli_retrospective",
    "galicia_xi_partial_semester_reports","valencia_ilp_html_list",
}
NATIONAL_VISIBLE={
    "TC_STATISTICAL_SERIES","TC_REGISTRY_INITIAL_WRITINGS_2025",
    "DP_ANNUAL_REPORT_2025_PORTAL","JEC_PUBLIC_DOCTRINE_AGREEMENTS",
}


def _pairs(pairs):
    obj={}
    for k,v in pairs:
        if k in obj:
            raise ValueError("DUPLICATED_R9_MATRIX_KEY")
        obj[k]=v
    return obj


def _load(path:Path,pin:str,lower:int,upper:int):
    if path.is_symlink() or not path.is_file() or not lower<path.stat().st_size<upper:
        raise ValueError("UNTRUSTED_R9_MATRIX_FILE")
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=pin:
        raise ValueError("R9_MATRIX_SHA_DRIFT")
    return json.loads(raw.decode("utf8"),object_pairs_hook=_pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("BAD_JSON_NUMBER")))


def _url_ok(uri:str):
    if not isinstance(uri,str) or not 0<len(uri)<1500:
        return False
    try:
        x=urlsplit(uri)
        return (x.scheme=="https" and x.hostname in HOSTS and not x.username
                and not x.password and x.port is None and not x.fragment)
    except ValueError:
        return False


def _basic(obj,*,schema,source_sha,n):
    if (type(obj)!=dict or set(obj)!={
            "schema","audit_day_utc","source_worker_matrix_sha256",
            "preserved_full_matrix_outside_git",
            "source_local_ids_or_outcomes_published",
            "real_source_originals_downloaded","scientific_cycles","entries"}
            or obj["schema"]!=schema or obj["audit_day_utc"]!="2026-10-31"
            or obj["source_worker_matrix_sha256"]!=source_sha
            or obj["preserved_full_matrix_outside_git"] is not True
            or obj["source_local_ids_or_outcomes_published"] is not False
            or type(obj["real_source_originals_downloaded"]) is not int
            or obj["real_source_originals_downloaded"]!=0
            or type(obj["scientific_cycles"]) is not int or obj["scientific_cycles"]!=0
            or not isinstance(obj["entries"],list) or len(obj["entries"])!=n):
        raise ValueError("R9_SCIENTIFIC_PROMOTION_OR_WRONG_SCHEMA")
    return obj["entries"]


def _regional(obj):
    entries=_basic(obj,schema="pfl.r9.regional_documentary_redacted.v1",
                   source_sha=UPSTREAM_REGION_SHA,n=8)
    ids=set()
    out=[]
    for row in entries:
        if (type(row)!=dict or set(row)!={
                "id","institution","family","official_urls","documentary_risk",
                "rights_for_bulk_reuse_proven","all_received_denominator",
                "source_original_sha256","individual_source_local_ids_republished",
                "historical_source_vintages_certified","outcomes_for_inference_admitted"}):
            raise ValueError("R9_REGION_SOURCE_SCHEMA_DRIFT")
        ident=row["id"]
        if ident not in REGION_IDS or ident in ids:
            raise ValueError("R9_REGION_SOURCE_MISSING_DUPLICATE")
        ids.add(ident)
        if (row["rights_for_bulk_reuse_proven"] is not False
                or row["all_received_denominator"] is not None
                or row["source_original_sha256"] is not None
                or row["individual_source_local_ids_republished"] is not False
                or row["historical_source_vintages_certified"] is not False
                or row["outcomes_for_inference_admitted"] is not False
                or not isinstance(row["official_urls"],list)
                or not 1<=len(row["official_urls"])<=5
                or not all(_url_ok(url) for url in row["official_urls"])
                or not isinstance(row["institution"],str)
                or not isinstance(row["documentary_risk"],str)):
            raise ValueError("R9_REGION_RIGHTS_OR_SOURCE_PROMOTION")
        if ident in REGIONAL_VISIBLE:
            out.append({
                "source_id":ident,
                "institution":row["institution"],
                "documentary_limit":row["documentary_risk"],
                "documentary_only":True,
                "original_replayed":False,
                "source_eligible":False,
                "risk_population_denominator":None,
            })
    if ids!=REGION_IDS:
        raise ValueError("R9_REGIONAL_SOURCE_COVERAGE_DRIFT")
    return out


def _national(obj):
    entries=_basic(obj,schema="pfl.r9.national_documentary_redacted.v1",
                   source_sha=UPSTREAM_NATIONAL_SHA,n=11)
    ids=set()
    out=[]
    for row in entries:
        if (type(row)!=dict or set(row)!={
                "id","institution","unit","official_metadata_url","source_grain",
                "rights_for_bulk_reuse_proven","all_received_denominator",
                "source_original_sha256","historical_source_vintages_certified",
                "case_outcomes_for_inference_admitted","intake_count_from_unreplayed_original"}):
            raise ValueError("R9_NATIONAL_SOURCE_SCHEMA_DRIFT")
        ident=row["id"]
        if ident not in NATIONAL_IDS or ident in ids:
            raise ValueError("R9_NATIONAL_SOURCE_MISSING_DUPLICATE")
        ids.add(ident)
        if (row["rights_for_bulk_reuse_proven"] is not False
                or row["all_received_denominator"] is not None
                or row["source_original_sha256"] is not None
                or row["historical_source_vintages_certified"] is not False
                or row["case_outcomes_for_inference_admitted"] is not False
                or row["intake_count_from_unreplayed_original"] is not None
                or not _url_ok(row["official_metadata_url"])
                or not isinstance(row["institution"],str)
                or not isinstance(row["unit"],str)):
            raise ValueError("R9_NATIONAL_RIGHTS_OR_SOURCE_PROMOTION")
        if ident in NATIONAL_VISIBLE:
            out.append({
                "source_id":ident,
                "institution":row["institution"],
                "documentary_unit":row["unit"],
                "source_eligible":False,
                "source_original_replayed":False,
                "risk_population_denominator":None,
                "reported_intake_count":None,
            })
    if ids!=NATIONAL_IDS:
        raise ValueError("R9_NATIONAL_SOURCE_COVERAGE_DRIFT")
    return out


def status(*,as_of:str|None=None,regional_path:Path|None=None,national_path:Path|None=None):
    t=utc(as_of) if as_of is not None else None
    base={
        "schema":"pfl.r9.documentary_population_opportunities.v1",
        "as_of":as_of,"R9_real_originals_acquired":0,
        "institutional_population_denominator":None,
        "registered_source_local_cases_admitted":None,
        "new_outcomes_admitted":False,
        "first_public_at":None,
        "historical_asof_supported":False,
        "scientific_cycles":0,
        "cross_institutional_joins_admitted":False,
    }
    if t is not None and t<SAFE_BY:
        return {**base,"status":"R9_DISCOVERY_NOT_KNOWN_AT_CUT",
                "regional_source_count":None,"national_source_count":None,
                "regional_highlights":[],"national_highlights":[],
                "observed_source_matrix_sha256":None,"source_metadata_safe_by":None,
                "pre_registration_outcome_header_exposure":None}
    try:
        regions=_regional(_load(regional_path or REGIONAL,REGIONAL_SHA,4000,12000))
        nationals=_national(_load(national_path or NATIONAL,NATIONAL_SHA,4000,12000))
    except (ValueError,OSError,TypeError,KeyError,AttributeError):
        return {**base,"status":"R9_DOCUMENTARY_SOURCE_QUARANTINED",
                "regional_source_count":None,"national_source_count":None,
                "regional_highlights":[],"national_highlights":[],
                "observed_source_matrix_sha256":None,"source_metadata_safe_by":None,
                "pre_registration_outcome_header_exposure":None}
    return {**base,"status":"R9_DISCOVERY_ONLY_RIGHTS_AND_DENOMINATORS_BLOCKED",
            "regional_source_count":8,"national_source_count":11,
            "regional_highlights":regions,"national_highlights":nationals,
            "observed_source_matrix_sha256":{
                "regional_redacted":REGIONAL_SHA,"national_redacted":NATIONAL_SHA,
            },"source_metadata_safe_by":SAFE_BY.isoformat(),
            "pre_registration_outcome_header_exposure":True,
            "interpretation":("Published documentary descriptions are not a cohort. Galicia "
                              "retrospective ILP headers contain preliminary outcome-category "
                              "exposure before AJ freeze; do not repurpose the same source as "
                              "confirmatory holdout. TC, Ombudsman and JEC are distinct units. "
                              "No original acquired or bulk reuse rights established."),
            "unreplayed_editorial_numbers_excluded_from_observatory":True,
            "original_register_identifiers_not_republished":True}
