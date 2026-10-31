"""Only approved R12 source-metadata fields pass from independent scratch.

The original agent matrices are private and pinned by SHA. This script cannot
fetch case data, accept website terms, include individual resource identifiers,
or treat published decisions as a register of incoming procedural appeals.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
NORMATIVE=ROOT.parent/"PFL-scratch-congreso2-20261031/ronda12/EVIDENCE_MATRIX.json"
APPEALS=ROOT.parent/"PFL-scratch-links2-20261031/ronda12/OFFICIAL_SOURCE_MATRIX.json"
DEST=ROOT/"data/source_manifests/r12_normative_appeals_documentary_redacted_20261031.json"
NORMATIVE_SHA="261c69692dcd17f8987a6d222f92c90ca910b80fa6ed14e72dc95a8888f27ed6"
APPEALS_SHA="35d3b630a65ee94601f9180937e56d37c50915bdfe76f91633fa34b10a632da3"
NORM_KINDS={
    "R12-A":("AGE_PAN_2026","PLANNED_NORMATIVE_INSTRUMENT",
             "YEAR_AGENDA_NOT_ALL_SUBMITTED_CONSULTATIONS",
             "GENERAL_REUSE_CONDITIONS_NO_ASSET_RIGHTS_CERTIFICATION"),
    "R12-B":("AGE_EARLY_CONSULTATION","PUBLIC_CONSULTATION_INVITATION",
             "MINISTRY_DISTRIBUTED_AND_LEGAL_WAIVERS_UNOBSERVED",
             "PORTAL_GENERAL_MERE_USE_TERMS_AND_MINISTRY_GAPS"),
    "R12-C":("AGE_NORMAS_EN_TRAMITACION","SELECTED_DRAFT_IN_PROCESS",
             "STAGE_INDEX_EXCLUDES_SIMULTANEOUS_CONSULTATIONS",
             "GENERAL_REUSE_CONDITIONS_NO_COMPLETE_REGISTER_LICENCE"),
}
APPEAL_KINDS={
    "TACRC":("TACRC_INTAKE_APPEALS","ANNUAL_APPEAL_ENTRY_AGGREGATE",
             "RESOURCES_RECEIVED_NOT_RESOLUTIONS_OR_COHORT_TERMINALS",
             "MINISTRY_GENERAL_CONDITIONS_NO_CASE_REGISTER_LICENCE","T1"),
    "TARCJA_ANDALUCIA":("TARCJA_PUBLIC_RESOLUTIONS","PUBLISHED_APPEALS_DECISION",
             "OUTCOME_SELECTED_CSV_NOT_REGISTERED_APPEAL_DENOMINATOR",
             "CC_BY_4_CSV_ONLY_NOT_EDITORIAL_REPORT_OR_FILINGS","A2"),
    "TEAC_TEARL":("TEA_TAX_APPEALS","AGGREGATE_TAX_APPEAL_ENTRY",
             "DYCTEA_DOCTRINAL_SELECTION_NOT_ALL_FILED_CLAIMS",
             "MINISTRY_GENERAL_TERMS_AND_TAX_CASE_CONFIDENTIALITY","E1"),
}
OFFICIAL_HOSTS={"transparencia.gob.es","www.hacienda.gob.es",
                "www.juntadeandalucia.es"}


def _load(path:Path,pin:str):
    if (not path.is_file() or path.is_symlink()
            or not 1000<path.stat().st_size<35000):
        raise ValueError("R12_PRIVATE_MATRIX_UNAVAILABLE")
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=pin:
        raise ValueError("R12_PRIVATE_SOURCE_SHA_MISMATCH")
    return json.loads(raw.decode("utf8"))


def _allow_url(value:str):
    if not isinstance(value,str) or len(value)>2000:
        raise ValueError("R12_BAD_OFFICIAL_URL")
    u=urlsplit(value)
    if (u.scheme!="https" or u.hostname not in OFFICIAL_HOSTS
            or u.username or u.password or u.port or u.fragment):
        raise ValueError("R12_UNTRUSTED_OFFICIAL_URL")
    return value


def _row(*,identifier,unit,limitation,rights,url,origin):
    return {
        "source_id":identifier,
        "origin":origin,
        "documentary_unit":unit,
        "primary_index_url":_allow_url(url),
        "risk_frame_limitation":limitation,
        "specific_rights_scope":rights,
        "source_originals_acquired":0,
        "individual_decisions_inspected":False,
        "all_received_denominator":None,
        "official_case_link_certified":False,
        "right_censoring_observed":None,
        "historical_first_public_at":None,
    }


def sanitized():
    n=_load(NORMATIVE,NORMATIVE_SHA)
    a=_load(APPEALS,APPEALS_SHA)
    if (n.get("schema")!="PFL_R12_AGE_PRE_NORMATIVE_DOCUMENTARY_MATRIX_V1"
            or n.get("source_downloads_or_original_gets")!=0
            or n.get("retrieved_individual_cases_or_outcomes")!=0
            or n.get("R5_STOP_and_remote_AJ_closed") is not True
            or n.get("first_public_at") is not None):
        raise ValueError("R12_NORMATIVE_PRE_CENSUS_PROMOTION")
    if (a.get("round")!="R12" or a.get("r5_stop") is not True
            or a.get("ab_cycles")!=0 or a.get("case_or_microdata_gets")!=0
            or a.get("outcome_analysis")!="NONE"
            or a.get("source_original_hashes") is not None):
        raise ValueError("R12_APPEALS_OUTCOME_OR_ORIGINAL_PROMOTION")
    nrows=n.get("main_routes")
    arows=a.get("routes")
    assets=a.get("sources_checked_as_official_documentation")
    if (type(nrows)!=list or len(nrows)!=3
            or {r["route_id"] for r in nrows}!=set(NORM_KINDS)
            or type(arows)!=list or len(arows)!=3
            or {r["id"] for r in arows}!=set(APPEAL_KINDS)
            or type(assets)!=list or len(assets)!=21
            or len(a.get("negative_findings",[]))!=18):
        raise ValueError("R12_DOCUMENTARY_SOURCE_ROUTE_DRIFT")
    rows=[]
    for x in nrows:
        identifier,unit,limitation,rights=NORM_KINDS[x["route_id"]]
        if (x.get("first_public_at") is not None
                or x.get("source_original_SHA256") is not None):
            raise ValueError("R12_NORMATIVE_REPURPOSED_OUTCOME")
        rows.append(_row(
            identifier=identifier,unit=unit,limitation=limitation,rights=rights,
            url=x["source_url"],origin="GOVERNMENTAL_NORMATIVE_METADATA"))
    idx={s["id"]:s for s in assets}
    for x in arows:
        identifier,unit,limitation,rights,asset=APPEAL_KINDS[x["id"]]
        if (x.get("case_first_public_at_confirmed") is not False
                or x.get("available_verified_public_individual_intake_census") is not False
                or x.get("gate")!="STOP_R5"):
            raise ValueError("R12_APPEAL_INTRODUCED_CASE_CENSUS")
        rows.append(_row(
            identifier=identifier,unit=unit,limitation=limitation,rights=rights,
            url=idx[asset]["url"],origin="ADMINISTRATIVE_APPEALS_METADATA"))
    return {
        "schema":"pfl.r12.normative_appeals_documentary_redacted.v1",
        "audit_day_utc":"2026-10-31",
        "private_source_matrix_sha256":{"normative":NORMATIVE_SHA,"appeals":APPEALS_SHA},
        "documentation_not_case_rows":True,
        "source_originals_downloaded":0,
        "case_outcomes_examined":0,
        "AB_cycles_executed":0,
        "terms_accepted":False,
        "complete_independent_registration_denominator":False,
        "historical_vintages_of_same_case_distribution":False,
        "confirmed_first_public_at":None,
        "source_local_identifiers_exported":False,
        "documentary_routes":rows,
    }


if __name__=="__main__":
    if DEST.exists():
        raise ValueError("R12_MANIFEST_ALREADY_GENERATED_NO_SILENT_OVERWRITE")
    data=(json.dumps(sanitized(),ensure_ascii=False,indent=2)+"\n").encode()
    DEST.write_bytes(data)
    print("R12_SHA256",hashlib.sha256(data).hexdigest())
