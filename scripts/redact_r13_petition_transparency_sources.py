"""Reproducibly declassify only approved official catalogue *metadata*.

This reads pinned private scratch matrices; never fetches site data, accepts
terms, handles petitioners, court documents, or publishes case identifiers.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
SENATE=ROOT.parent/"PFL-scratch-congreso2-20261031/ronda13/EVIDENCE_MATRIX.json"
REVIEW=ROOT.parent/"PFL-scratch-links2-20261031/ronda13/OFFICIAL_SOURCE_MATRIX.json"
OUTPUT=ROOT/"data/source_manifests/r13_petition_transparency_documentary_redacted_20261031.json"
SENATE_SHA="0467dcf9c339cbf4906ea31ba1086c08813d3727e9e1ac2e0d732d6d8cd0da7c"
REVIEW_SHA="6153fc6aa4bb6fcd7b23206710f8b61cf639c585301fbc6a41fe8317d5bdd588"
HOSTS={"www.senado.es","mptmd.gob.es","datos.gob.es",
       "analisi.transparenciacatalunya.cat","parlamentodenavarra.es"}
SEN_MAP={
 "R13-A-SENADO-FILING-REGISTER":(
  "SENATE_INITIAL_PETITION_REGISTRY","CITIZEN_SIGNED_PETITION_BEFORE_COMMISSION",
  "REGISTER_DESCRIBED_NOT_EXPORTED_AND_PII_CONFIDENTIAL",
  "NO_SPECIFIC_PETITION_REGISTER_LICENSE"),
 "R13-B-COMMISSION-REPORTS":(
  "SENATE_PETITIONS_PERIODIC_REPORTS","COMMISSION_PERIOD_REPORT_871",
  "ADMITTED_DICTAMENS_AND_REPORTS_NOT_PRECLASSIFICATION_SEATS",
  "GENERAL_NOTICE_CANNOT_LICENSE_PETITION_REGISTER"),
 "R13-C-SENATE-OPEN-DATA-CATALOGUE":(
  "SENATE_OPEN_DATA_CATALOGUE","SOURCE_CATALOGUE_NOT_PETITION_REGISTER",
  "CATALOGUE_LISTS_NO_COMPLETE_PETITIONS_DISTRIBUTION",
  "CC_BY4_CATALOGUE_WITH_GENERAL_BINDING_MERE_USE_TERMS"),
 "R13-D-SEPARATE-AGE-ALTERNATIVE":(
  "AGE_GENERAL_PETITION_GUIDE","AGE_GENERAL_PETITION_PROCEDURE",
  "GENERAL_ADMINISTRATION_NOT_SENATE_COMMISSION_OR_SAME_REGISTER",
  "PROCEDURE_DESCRIPTION_NOT_CASE_DISTRIBUTION_LICENSE"),
}
REVIEW_MAP={
 "GAIP_RESOLUTION":(
  "GAIP_RESOLUTIONS_PUBLISHED","GAIP_DECISION_TERMINATING_APPEAL",
  "APPROVED_DECISIONS_ONLY_NO_ALL_FILED_APPEALS",
  "GENERAL_CATALUNYA_TERMS_BY_ACCESS_ASSET_NOT_CERTIFIED","G2"),
 "GAIP_PLENARY_AND_UPSTREAM":(
  "GAIP_PLENARY_MINUTES","GAIP_PLENARY_MINUTE_DOCUMENT",
  "MINUTES_AFTER_ADMISSION_NOT_INITIAL_CLAIM_ENTRIES",
  "GENERAL_DATASET_TERMS_NO_RIGHTS_FOR_PDF_LINKS","G8"),
 "CATALUNYA_SAIP_FILINGS":(
  "GENCAT_SAIP_INITIAL_FILINGS","INITIAL_REQUEST_FOR_ACCESS_TO_INFORMATION",
  "GENCAT_ADMINISTRATION_ONLY_NOT_ALL_GAIP_APPEALS",
  "GENERAL_LICENSE_BY_ACCESS_DISTRIBUTION_RIGHTS_UNCONFIRMED","G10"),
 "NAVARRA_TRANSPARENCIA":(
  "NAVARRA_TRANSPARENCY_COUNCIL","ANNUAL_REPORT_OF_RECEIVED_APPEALS",
  "AGGREGATE_AND_DECISION_CATALOG_NOT_COMPLETE_CASE_REGISTER",
  "PARLIAMENTARY_NOTICE_AND_DATASET_LICENSE_NOT_EQUIVALENT","N1"),
}


def _load(path:Path,pin:str):
    if path.is_symlink() or not path.is_file() or not 1500<path.stat().st_size<30000:
        raise ValueError("R13_PRIVATE_SOURCE_MISSING")
    content=path.read_bytes()
    if sha256(content).hexdigest()!=pin:
        raise ValueError("R13_PRIVATE_SOURCE_SHA_CHANGED")
    return json.loads(content.decode("utf8"))


def _official(url):
    if not isinstance(url,str) or len(url)>2000:
        raise ValueError("R13_UNSAFE_CATALOGUE_URL")
    u=urlsplit(url)
    if (u.scheme!="https" or u.hostname not in HOSTS
            or u.username or u.password or u.port or u.fragment):
        raise ValueError("R13_UNSAFE_CATALOGUE_URL")
    return url


def _row(key,unit,block,rights,url,origin):
    return {
        "source_id":key,"documentary_unit":unit,
        "entry_frame_limitation":block,"rights_scope":rights,
        "official_catalogue_url":_official(url),"documentary_origin":origin,
        "individual_originals_downloaded":0,"individual_outcomes_inspected":False,
        "complete_all_received_denominator":None,
        "admission_or_censoring_certified":False,
        "first_public_at":None,"two_comparable_original_vintages":False,
    }


def sanitized():
    senate=_load(SENATE,SENATE_SHA)
    review=_load(REVIEW,REVIEW_SHA)
    if (senate.get("schema")!="PFL_R13_SENATE_PETITIONS_DOCUMENTARY_MATRIX_V1"
            or senate.get("site_original_PDF_or_microdata_gets")!=0
            or senate.get("individual_petitions_or_replies_queried")!=0
            or senate.get("raw_petition_records_saved")!=0
            or senate.get("R5_STOP_active") is not True
            or senate.get("first_public_at") is not None
            or senate.get("matrix_contains_personal_petitioner_names_or_addresses") is not False):
        raise ValueError("R13_SENATE_RECORD_OR_ORIGINAL_LEAK")
    if (review.get("round")!="R13"
            or review.get("STOP_R5") is not True
            or any(review.get(k)!=0 for k in (
                "source_original_gets","case_outcome_gets","pii_gets",
                "data_distribution_gets","terms_or_cookie_acceptance","AB_cycles"))
            or review.get("source_original_hashes") is not None
            or review.get("individual_outcomes_examined")!=0):
        raise ValueError("R13_REVIEW_RECORD_OR_ORIGINAL_LEAK")
    sr=senate.get("routes")
    rr=review.get("routes")
    assets=review.get("sources")
    if (type(sr)!=list or len(sr)!=4 or {x["id"] for x in sr}!=set(SEN_MAP)
            or type(rr)!=list or len(rr)!=4 or {x["id"] for x in rr}!=set(REVIEW_MAP)
            or type(assets)!=list or len(assets)!=17
            or len(review.get("negative_findings",[]))!=24):
        raise ValueError("R13_UNEXPECTED_DOCUMENTARY_FAMILY_OR_ASSETS")
    rows=[]
    for x in sr:
        identifier,unit,block,rights=SEN_MAP[x["id"]]
        if x["id"].startswith("R13-A"):
            url=x["source_url"]
        elif x["id"].startswith("R13-B"):
            url=x["source_urls"][0]
        elif x["id"].startswith("R13-C"):
            url=x["catalogue_url"]
        else:
            url=x["procedure_url"]
        if (x.get("first_public_at") is not None or
                x.get("source_original_sha256") is not None):
            raise ValueError("R13_ORIGINAL_OR_FIRST_PUBLIC_PROMOTED")
        rows.append(_row(identifier,unit,block,rights,url,"SENATE_AND_AGE_PETITIONS"))
    listed={x["id"]:x for x in assets}
    for x in rr:
        identifier,unit,block,rights,asset=REVIEW_MAP[x["id"]]
        if (x.get("independent_filing_register_verified") is not False
                or x.get("first_public_at_by_claim_verified") is not False
                or x.get("rights_per_distribution_verified") is not False):
            raise ValueError("R13_GAIP_SAIP_FALSE_ADMISSION")
        rows.append(_row(identifier,unit,block,rights,listed[asset]["url"],
                         "GAIP_GENCAT_NAVARRA_DOCUMENTATION"))
    return {
        "schema":"pfl.r13.petitions_transparency_documentary.v1",
        "local_documentary_audit_day":"2026-10-31",
        "private_matrix_sha256":{"senate":SENATE_SHA,"gaip_navarra":REVIEW_SHA},
        "documentation_only":True,"source_originals_downloaded":0,
        "case_outcomes_examined":0,"terms_accepted":False,
        "AB_scientific_cycles":0,"complete_scientific_denominator":False,
        "same_distribution_original_vintages_verified":0,
        "individual_identifiers_or_personal_data_exported":False,
        "historical_first_public_at":None,
        "documentary_sources":rows,
    }


if __name__=="__main__":
    if OUTPUT.exists():
        raise ValueError("R13_REDACTION_REFUSES_OVERWRITE")
    out=(json.dumps(sanitized(),ensure_ascii=False,indent=2)+"\n").encode()
    OUTPUT.write_bytes(out)
    print("R13_SANITIZED_SHA256",sha256(out).hexdigest())
