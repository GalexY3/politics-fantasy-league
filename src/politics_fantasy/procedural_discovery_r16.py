"""R16 official procedural descriptions: registration/admission/review are distinct.

Read *only* SHA-pinned, sanitized, locally reviewed documentary metadata.
There are no downloads or case/outcome reads. A dataset's CC BY label is not
an all-received registry, acceptance of portal conditions, nor clearance for
personal microdata. R16 adds three source families, not three risk cohorts.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit
import json

from .procedural_index_contract import utc

ROOT = Path(__file__).resolve().parents[2]
MANIFEST=ROOT/"data/source_manifests/r16_official_intake_rights_documentary_redacted_20261031.json"
PIN="cadd5e743afc4e0d3b63f595c94ecdbed48380de0d11feec94d2dfccca0683fe"
SAFE_BY=datetime(2026,11,1,tzinfo=timezone.utc)
MATRIX_SHA="338917b0e667f118659092bb78975d2ca0c4e1565cb0b2a0738c98d8b1393e3c"
RECEIPT_SHA="f5c3a7597486cf77bfabf3200267e723c1b214b77054efac448f5029dd61846e"
FREEZE_SHA="3cbbdfffacc5b6babc6e2d508f34944aeed616c2aa90448af66fd24093a3ea98"

ROOT_KEYS={
    "schema","local_documentary_audit_day","source_private_matrix_sha256",
    "source_private_receipt_sha256","synthetic_code_freeze_sha256",
    "documentary_only","new_real_case_records_acquired",
    "outcomes_or_personal_cases_inspected","terms_or_cookies_accepted",
    "scientific_AB_cycles","independent_all_received_denominator",
    "case_terminal_pending_or_censored","historical_individual_first_public_at",
    "real_original_vintage_pairs","cross_institutional_verified_case_links",
    "three_documentary_routes_not_added_to_any_homogeneous_risk_set",
}
ROW_KEYS={
    "source_id","institution","documentary_unit","stage_selection_limit",
    "legal_rights_scope","official_documentation_url",
    "independent_procedural_comparison_url","official_editorial_conflict",
    "catalogue_license_claim","distribution_rights_certified",
    "general_register_includes_noncomplaint_traffic",
    "preclassification_padrón_complete","case_data_originals_acquired",
    "independent_entry_denominator","negative_pending_or_censored_states",
    "historical_first_public_at",
}
ALLOWED={
    "SINDIC_CV_COMPLAINT_REGISTRATION":(
        "Síndic de Greuges de la Comunitat Valenciana",
        "REGISTERED_COMPLAINT_BEFORE_ADMISSION_VERSUS_POST_ADMISSION_FILE_NUMBER",
        "NO_ALL_RECEIVED_PUBLIC_CASE_REGISTER_OR_OFFICIAL_REGISTRATION_TO_FILE_CROSSWALK",
        "www.elsindic.com",
        "RECEIPT_3_VS_5_DAYS_AND_CASE_NUMBER_STAGE_CONFLICT; LEGAL_VINTAGE_NOT_RESOLVED",
    ),
    "CTCYL_POST_REQUEST_ACCESS_COMPLAINTS":(
        "Comisión de Transparencia de Castilla y León",
        "TRANSPARENCY_COMPLAINT_AFTER_INITIAL_ACCESS_REQUEST",
        "COMPLAINT_IS_NOT_ALL_INITIAL_ACCESS_REQUESTS; EDITORIAL_TOTAL_NOT_EXTERNAL_DENOMINATOR",
        "ctcyl.es",
        "REVIEW_STAGE_DISTINCT_FROM_INITIAL_REQUEST; NONADDITIVE_ACROSS_MUNICIPALITIES",
    ),
    "CTPDA_ANDALUCIA_SELECTED_REVIEW_RESOLUTIONS":(
        "Consejo de Transparencia y Protección de Datos de Andalucía",
        "EDITORIAL_PUBLIC_RESOLUTIONS_OF_REVIEW_CLAIMS_NOT_INITIAL_ENTRIES",
        "SELECTED_RESOLUTIONS_NOT_COMPLETE_PRECLASSIFICATION_REGISTER_OR_ALL_INITIAL_ACCESS_REQUESTS",
        "www.juntadeandalucia.es",
        "TRANSPARENCY_REVIEW_RESOLUTIONS_AND_DATA_PROTECTION_CLAIMS_ARE_DISTINCT_FAMILIES",
    ),
}


def _pairs(pairs):
    out={}
    for k,v in pairs:
        if k in out:
            raise ValueError("R16_DUPLICATE_JSON_FIELD")
        out[k]=v
    return out


def _url(url:str,host:str) -> bool:
    if type(url) is not str or len(url)>1400:
        return False
    u=urlsplit(url)
    return (u.scheme=="https" and u.hostname==host and
            not u.username and not u.password and not u.port and
            not u.fragment and not u.query)


def _load(path: Path) -> list[dict]:
    if (path.is_symlink() or not path.is_file()
            or not 1300<path.stat().st_size<15000):
        raise ValueError("R16_MANIFEST_ABSENT_OR_OVERSIZED")
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=PIN:
        raise ValueError("R16_UNREVIEWED_MANIFEST_SHA")
    doc=json.loads(raw.decode("utf8"),object_pairs_hook=_pairs,
                   parse_constant=lambda _: (_ for _ in ()).throw(
                       ValueError("R16_NONFINITE_JSON")))
    if (type(doc) is not dict or set(doc)!=ROOT_KEYS
            or doc["schema"]!="pfl.r16.registration_comparison_documentary.v1"
            or doc["local_documentary_audit_day"]!="2026-10-31"
            or doc["source_private_matrix_sha256"]!=MATRIX_SHA
            or doc["source_private_receipt_sha256"]!=RECEIPT_SHA
            or doc["synthetic_code_freeze_sha256"]!=FREEZE_SHA
            or doc["documentary_only"] is not True
            or doc["terms_or_cookies_accepted"] is not False
            or any(type(doc[k]) is not int or doc[k]!=0 for k in (
                "new_real_case_records_acquired","outcomes_or_personal_cases_inspected",
                "scientific_AB_cycles","real_original_vintage_pairs",
                "cross_institutional_verified_case_links"))
            or any(doc[k] is not None for k in (
                "independent_all_received_denominator","case_terminal_pending_or_censored",
                "historical_individual_first_public_at"))):
        raise ValueError("R16_UNATTESTED_SCIENTIFIC_OR_RIGHTS_PROMOTION")
    rows=doc["three_documentary_routes_not_added_to_any_homogeneous_risk_set"]
    if (type(rows) is not list or len(rows)!=3
            or {r.get("source_id") for r in rows if type(r) is dict}!=set(ALLOWED)):
        raise ValueError("R16_NOT_THREE_DISTINCT_DOCUMENTARY_ROUTES")
    output=[]
    for r in rows:
        if type(r) is not dict or set(r)!=ROW_KEYS:
            raise ValueError("R16_UNEXPECTED_ROUTE_FIELDS")
        institution,unit,limitation,host,conflict=ALLOWED[r["source_id"]]
        if ((r["institution"],r["documentary_unit"],
             r["stage_selection_limit"],r["official_editorial_conflict"])
            !=(institution,unit,limitation,conflict)):
            raise ValueError("R16_SOURCE_JURISDICTION_OR_SELECTION_DRIFT")
        if (not _url(r["official_documentation_url"],host)
                or (r["independent_procedural_comparison_url"] is not None
                    and not _url(r["independent_procedural_comparison_url"],host))
                or (r["source_id"]=="SINDIC_CV_COMPLAINT_REGISTRATION"
                    and r["independent_procedural_comparison_url"] is None)):
            raise ValueError("R16_UNTRUSTED_SOURCE_URL")
        if (type(r["catalogue_license_claim"]) is not str
                or type(r["legal_rights_scope"]) is not str
                or len(r["legal_rights_scope"])>400
                or len(r["catalogue_license_claim"])>400
                or r["distribution_rights_certified"] is not False
                or r["preclassification_padrón_complete"] is not False
                or type(r["case_data_originals_acquired"]) is not int
                or r["case_data_originals_acquired"]!=0
                or any(r[x] is not None for x in (
                    "independent_entry_denominator",
                    "negative_pending_or_censored_states",
                    "historical_first_public_at"))
                or r["general_register_includes_noncomplaint_traffic"] not in (True,None)):
            raise ValueError("R16_RIGHTS_COVERAGE_OR_OUTCOME_PROMOTION")
        output.append({
            "source_id":r["source_id"],"institution":institution,
            "documentary_unit":unit,"limitation":limitation,
            "rights_scope":r["legal_rights_scope"],
            "catalogue_license_claim":r["catalogue_license_claim"],
            "editorial_conflict":r["official_editorial_conflict"],
            "source_originals_acquired":0,
            "distribution_rights_certified":False,
            "independent_entry_denominator":None,
            "real_terminal_decisions":None,"real_pending_or_censored":None,
            "first_public_at":None,
            "source_role_is_not_a_homogeneous_risk_set":True,
        })
    return output


def status(*, as_of:str|None=None, path:Path|None=None) -> dict:
    cut=utc(as_of) if as_of is not None else datetime.now(timezone.utc)
    base={
        "schema":"pfl.r16.registration_comparison_documentary_status.v1",
        "as_of":as_of,"real_denominator":None,
        "real_pending_or_censoring":None,"terminal_outcomes":None,
        "historical_first_public_at":None,
        "historical_original_pairs":None,
        "scientific_cycles":0,"rights_to_download_originals":False,
        "source_groups_additive":False,
    }
    hidden={"source_rows":[],"documentary_source_count":None,
            "manifest_sha256":None,"documentary_safe_by":None}
    if cut<SAFE_BY:
        return {**base,**hidden,"status":"R16_NOT_KNOWN_AT_CUT"}
    try:
        rows=_load(path or MANIFEST)
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return {**base,**hidden,"status":"R16_MANIFEST_QUARANTINED"}
    return {**base,"status":"R16_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED",
            "source_rows":rows,"documentary_source_count":len(rows),
            "manifest_sha256":PIN,"documentary_safe_by":SAFE_BY.isoformat()}
