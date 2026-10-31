"""Eight SHA-pinned documentary leads (NOT cohorts); fail closed historically.

R13 metadata is derived from independent agents' private, hash-pinned
matrices. No new case original, consent, portal session, outcomes, official
case join, registered risk set, or first-public date is included. The local
audit day has DATE precision: earlier as-of requests get no titles, counts,
rights statuses, SHA or quarantine diagnostics from this source.
"""
from __future__ import annotations

from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit

from .procedural_index_contract import utc

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/"data/source_manifests/r13_petition_transparency_documentary_redacted_20261031.json"
PIN="0bf0cfc12424ee9aa3ca1dc4a6f2d0eaf5de18cc52b0cab4f7ad2cf6ed707fa0"
SENATE_SHA="0467dcf9c339cbf4906ea31ba1086c08813d3727e9e1ac2e0d732d6d8cd0da7c"
REVIEW_SHA="6153fc6aa4bb6fcd7b23206710f8b61cf639c585301fbc6a41fe8317d5bdd588"
SAFE_BY=datetime(2026,11,1,tzinfo=timezone.utc)
HOSTS={"www.senado.es","mptmd.gob.es","datos.gob.es",
       "analisi.transparenciacatalunya.cat","parlamentodenavarra.es"}
ALLOWED={
    "SENATE_INITIAL_PETITION_REGISTRY":("CITIZEN_SIGNED_PETITION_BEFORE_COMMISSION",
        "REGISTER_DESCRIBED_NOT_EXPORTED_AND_PII_CONFIDENTIAL",
        "NO_SPECIFIC_PETITION_REGISTER_LICENSE","SENATE_AND_AGE_PETITIONS"),
    "SENATE_PETITIONS_PERIODIC_REPORTS":("COMMISSION_PERIOD_REPORT_871",
        "ADMITTED_DICTAMENS_AND_REPORTS_NOT_PRECLASSIFICATION_SEATS",
        "GENERAL_NOTICE_CANNOT_LICENSE_PETITION_REGISTER","SENATE_AND_AGE_PETITIONS"),
    "SENATE_OPEN_DATA_CATALOGUE":("SOURCE_CATALOGUE_NOT_PETITION_REGISTER",
        "CATALOGUE_LISTS_NO_COMPLETE_PETITIONS_DISTRIBUTION",
        "CC_BY4_CATALOGUE_WITH_GENERAL_BINDING_MERE_USE_TERMS","SENATE_AND_AGE_PETITIONS"),
    "AGE_GENERAL_PETITION_GUIDE":("AGE_GENERAL_PETITION_PROCEDURE",
        "GENERAL_ADMINISTRATION_NOT_SENATE_COMMISSION_OR_SAME_REGISTER",
        "PROCEDURE_DESCRIPTION_NOT_CASE_DISTRIBUTION_LICENSE","SENATE_AND_AGE_PETITIONS"),
    "GAIP_RESOLUTIONS_PUBLISHED":("GAIP_DECISION_TERMINATING_APPEAL",
        "APPROVED_DECISIONS_ONLY_NO_ALL_FILED_APPEALS",
        "GENERAL_CATALUNYA_TERMS_BY_ACCESS_ASSET_NOT_CERTIFIED",
        "GAIP_GENCAT_NAVARRA_DOCUMENTATION"),
    "GAIP_PLENARY_MINUTES":("GAIP_PLENARY_MINUTE_DOCUMENT",
        "MINUTES_AFTER_ADMISSION_NOT_INITIAL_CLAIM_ENTRIES",
        "GENERAL_DATASET_TERMS_NO_RIGHTS_FOR_PDF_LINKS",
        "GAIP_GENCAT_NAVARRA_DOCUMENTATION"),
    "GENCAT_SAIP_INITIAL_FILINGS":("INITIAL_REQUEST_FOR_ACCESS_TO_INFORMATION",
        "GENCAT_ADMINISTRATION_ONLY_NOT_ALL_GAIP_APPEALS",
        "GENERAL_LICENSE_BY_ACCESS_DISTRIBUTION_RIGHTS_UNCONFIRMED",
        "GAIP_GENCAT_NAVARRA_DOCUMENTATION"),
    "NAVARRA_TRANSPARENCY_COUNCIL":("ANNUAL_REPORT_OF_RECEIVED_APPEALS",
        "AGGREGATE_AND_DECISION_CATALOG_NOT_COMPLETE_CASE_REGISTER",
        "PARLIAMENTARY_NOTICE_AND_DATASET_LICENSE_NOT_EQUIVALENT",
        "GAIP_GENCAT_NAVARRA_DOCUMENTATION"),
}
ROW_KEYS={"source_id","documentary_unit","entry_frame_limitation",
          "rights_scope","official_catalogue_url","documentary_origin",
          "individual_originals_downloaded","individual_outcomes_inspected",
          "complete_all_received_denominator","admission_or_censoring_certified",
          "first_public_at","two_comparable_original_vintages"}


def _no_dupes(pairs):
    result={}
    for k,v in pairs:
        if k in result:
            raise ValueError("R13_DUPLICATED_JSON_FIELD")
        result[k]=v
    return result


def _row(row):
    if type(row)!=dict or set(row)!=ROW_KEYS:
        raise ValueError("R13_UNEXPECTED_SOURCE_FIELDS")
    k=row["source_id"]
    if k not in ALLOWED or tuple(row[field] for field in (
            "documentary_unit","entry_frame_limitation",
            "rights_scope","documentary_origin"))!=ALLOWED[k]:
        raise ValueError("R13_SOURCE_UNIT_RIGHTS_DRIFT")
    url=urlsplit(row["official_catalogue_url"])
    if (url.scheme!="https" or url.hostname not in HOSTS
            or url.username or url.password or url.port or url.fragment):
        raise ValueError("R13_UNTRUSTED_SOURCE_LINK")
    if (type(row["individual_originals_downloaded"]) is not int
            or row["individual_originals_downloaded"]!=0
            or row["individual_outcomes_inspected"] is not False
            or row["complete_all_received_denominator"] is not None
            or row["admission_or_censoring_certified"] is not False
            or row["first_public_at"] is not None
            or row["two_comparable_original_vintages"] is not False):
        raise ValueError("R13_UNAUTHORIZED_CASE_PROMOTION")
    return {
        "source_id":k,
        "unit":row["documentary_unit"],
        "identification_limit":row["entry_frame_limitation"],
        "rights_gate":row["rights_scope"],
        "source_originals_acquired":0,
        "complete_registered_risk_denominator":None,
        "pending_or_censored_cases":None,
        "terminal_outcomes":None,
        "historical_first_public_at":None,
    }


def _validated(path:Path):
    if path.is_symlink() or not path.is_file() or not 2000<path.stat().st_size<17000:
        raise ValueError("R13_NO_SANITIZED_MANIFEST")
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=PIN:
        raise ValueError("R13_SANITIZED_MANIFEST_SHA_MISMATCH")
    d=json.loads(raw.decode("utf8"),object_pairs_hook=_no_dupes)
    if (type(d)!=dict or set(d)!={
            "schema","local_documentary_audit_day","private_matrix_sha256",
            "documentation_only","source_originals_downloaded",
            "case_outcomes_examined","terms_accepted","AB_scientific_cycles",
            "complete_scientific_denominator","same_distribution_original_vintages_verified",
            "individual_identifiers_or_personal_data_exported",
            "historical_first_public_at","documentary_sources"}
            or d["schema"]!="pfl.r13.petitions_transparency_documentary.v1"
            or d["local_documentary_audit_day"]!="2026-10-31"
            or d["private_matrix_sha256"]!={"senate":SENATE_SHA,"gaip_navarra":REVIEW_SHA}
            or d["documentation_only"] is not True
            or any(type(d[field]) is not int or d[field]!=0 for field in (
                "source_originals_downloaded","case_outcomes_examined",
                "AB_scientific_cycles","same_distribution_original_vintages_verified"))
            or any(d[field] is not False for field in (
                "terms_accepted","complete_scientific_denominator",
                "individual_identifiers_or_personal_data_exported"))
            or d["historical_first_public_at"] is not None
            or type(d["documentary_sources"]) is not list
            or len(d["documentary_sources"])!=8
            or {r["source_id"] for r in d["documentary_sources"]}!=set(ALLOWED)):
        raise ValueError("R13_UNSAFE_MANIFEST_OR_POPULATION_CLAIM")
    return [_row(r) for r in d["documentary_sources"]]


def status(*,as_of:str|None=None,path:Path|None=None):
    cut=utc(as_of) if as_of is not None else None
    base={
        "schema":"pfl.r13.petition_transparency_discovery.v1",
        "as_of":as_of,
        "denominator_independently_verified":None,
        "real_original_vintage_pairs":None,
        "actual_censored_cases":None,
        "real_terminal_decisions":None,
        "first_public_at":None,
        "scientific_cycles":0,
        "all_eight_documentary_sources_nonadditive":True,
    }
    hidden={"documentary_source_count":None,
            "senate_age_source_count":None,"review_saip_source_count":None,
            "source_rows":[],"manifest_sha256":None,
            "documentary_safe_by":None,
            "senate_report_not_petition_count":None,
            "saip_not_all_gaip_claims":None,
            "restore_point_index_not_real_capture_pair":None,
            "rights_by_access_may_block_ingestion":None}
    if cut is not None and cut<SAFE_BY:
        return {**base,**hidden,"status":"R13_NOT_KNOWN_AT_CUT"}
    try:
        rows=_validated(path or MANIFEST)
    except (OSError,ValueError,TypeError,KeyError,AttributeError):
        return {**base,**hidden,"status":"R13_SOURCE_QUARANTINED"}
    return {**base,
        "status":"R13_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED",
        "documentary_source_count":8,
        "senate_age_source_count":4,
        "review_saip_source_count":4,
        "source_rows":rows,
        "manifest_sha256":PIN,
        "documentary_safe_by":SAFE_BY.isoformat(),
        "senate_report_not_petition_count":True,
        "saip_not_all_gaip_claims":True,
        "restore_point_index_not_real_capture_pair":True,
        "rights_by_access_may_block_ingestion":True,
        "recorded_decisions_not_all_received":True}
