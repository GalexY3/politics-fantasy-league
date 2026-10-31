"""R12: privacy-redacted, SHA-pinned cross-institution documentary status.

This can NOT authorize original download, official links, historic first
availability, R5 admission or empirical outcomes. A source is shown only at
a sufficiently late archive cut; tampering quarantines all six source rows.
"""
from __future__ import annotations

from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit

from .procedural_index_contract import utc

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/"data/source_manifests/r12_normative_appeals_documentary_redacted_20261031.json"
PIN="c865517ce8bc25cc2b1b835185e6710a518d7558b424147335ee0a66a3cc98a5"
NORM_SHA="261c69692dcd17f8987a6d222f92c90ca910b80fa6ed14e72dc95a8888f27ed6"
APPEALS_SHA="35d3b630a65ee94601f9180937e56d37c50915bdfe76f91633fa34b10a632da3"
SAFE_BY=datetime(2026,11,1,tzinfo=timezone.utc)
ALLOWED={
    "AGE_PAN_2026":("GOVERNMENTAL_NORMATIVE_METADATA","PLANNED_NORMATIVE_INSTRUMENT",
        "YEAR_AGENDA_NOT_ALL_SUBMITTED_CONSULTATIONS",
        "GENERAL_REUSE_CONDITIONS_NO_ASSET_RIGHTS_CERTIFICATION"),
    "AGE_EARLY_CONSULTATION":("GOVERNMENTAL_NORMATIVE_METADATA","PUBLIC_CONSULTATION_INVITATION",
        "MINISTRY_DISTRIBUTED_AND_LEGAL_WAIVERS_UNOBSERVED",
        "PORTAL_GENERAL_MERE_USE_TERMS_AND_MINISTRY_GAPS"),
    "AGE_NORMAS_EN_TRAMITACION":("GOVERNMENTAL_NORMATIVE_METADATA","SELECTED_DRAFT_IN_PROCESS",
        "STAGE_INDEX_EXCLUDES_SIMULTANEOUS_CONSULTATIONS",
        "GENERAL_REUSE_CONDITIONS_NO_COMPLETE_REGISTER_LICENCE"),
    "TACRC_INTAKE_APPEALS":("ADMINISTRATIVE_APPEALS_METADATA","ANNUAL_APPEAL_ENTRY_AGGREGATE",
        "RESOURCES_RECEIVED_NOT_RESOLUTIONS_OR_COHORT_TERMINALS",
        "MINISTRY_GENERAL_CONDITIONS_NO_CASE_REGISTER_LICENCE"),
    "TARCJA_PUBLIC_RESOLUTIONS":("ADMINISTRATIVE_APPEALS_METADATA","PUBLISHED_APPEALS_DECISION",
        "OUTCOME_SELECTED_CSV_NOT_REGISTERED_APPEAL_DENOMINATOR",
        "CC_BY_4_CSV_ONLY_NOT_EDITORIAL_REPORT_OR_FILINGS"),
    "TEA_TAX_APPEALS":("ADMINISTRATIVE_APPEALS_METADATA","AGGREGATE_TAX_APPEAL_ENTRY",
        "DYCTEA_DOCTRINAL_SELECTION_NOT_ALL_FILED_CLAIMS",
        "MINISTRY_GENERAL_TERMS_AND_TAX_CASE_CONFIDENTIALITY"),
}
HOSTS={"transparencia.gob.es","www.hacienda.gob.es","www.juntadeandalucia.es"}
ROW_KEYS={"source_id","origin","documentary_unit","primary_index_url",
          "risk_frame_limitation","specific_rights_scope",
          "source_originals_acquired","individual_decisions_inspected",
          "all_received_denominator","official_case_link_certified",
          "right_censoring_observed","historical_first_public_at"}


def _distinct_pairs(pairs):
    d={}
    for key,value in pairs:
        if key in d:
            raise ValueError("R12_DUPLICATE_JSON_KEY")
        d[key]=value
    return d


def _check_asset(row):
    if type(row)!=dict or set(row)!=ROW_KEYS:
        raise ValueError("R12_UNRECOGNIZED_SOURCE_FIELDS")
    key=row["source_id"]
    if key not in ALLOWED or tuple(row[k] for k in (
            "origin","documentary_unit","risk_frame_limitation",
            "specific_rights_scope"))!=ALLOWED[key]:
        raise ValueError("R12_SOURCE_SCOPE_OR_RIGHTS_PROMOTED")
    u=urlsplit(row["primary_index_url"])
    if (u.scheme!="https" or u.hostname not in HOSTS
            or u.username or u.password or u.port is not None or u.fragment):
        raise ValueError("R12_UNTRUSTED_SOURCE_URL")
    if (type(row["source_originals_acquired"]) is not int
            or row["source_originals_acquired"]!=0
            or row["individual_decisions_inspected"] is not False
            or row["all_received_denominator"] is not None
            or row["official_case_link_certified"] is not False
            or row["right_censoring_observed"] is not None
            or row["historical_first_public_at"] is not None):
        raise ValueError("R12_REAL_SOURCE_OUTCOME_PROMOTION")
    return {
        "source_id":key,
        "documentary_unit":row["documentary_unit"],
        "risk_frame_limitation":row["risk_frame_limitation"],
        "specific_rights_scope":row["specific_rights_scope"],
        "original_available":False,
        "independent_entry_denominator":None,
        "terminal_case_count":None,
        "pending_case_count":None,
        "censored_case_count":None,
        "first_public_at":None,
    }


def _load(path:Path):
    if path.is_symlink() or not path.is_file() or not 2000<path.stat().st_size<15000:
        raise ValueError("R12_DOCUMENTARY_MANIFEST_UNAVAILABLE")
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=PIN:
        raise ValueError("R12_DOCUMENTARY_SHA_MISMATCH")
    d=json.loads(raw.decode("utf8"),object_pairs_hook=_distinct_pairs)
    if (type(d)!=dict or set(d)!={
            "schema","audit_day_utc","private_source_matrix_sha256",
            "documentation_not_case_rows","source_originals_downloaded",
            "case_outcomes_examined","AB_cycles_executed","terms_accepted",
            "complete_independent_registration_denominator",
            "historical_vintages_of_same_case_distribution",
            "confirmed_first_public_at","source_local_identifiers_exported",
            "documentary_routes"}
            or d["schema"]!="pfl.r12.normative_appeals_documentary_redacted.v1"
            or d["audit_day_utc"]!="2026-10-31"
            or d["private_source_matrix_sha256"]!={"normative":NORM_SHA,"appeals":APPEALS_SHA}
            or d["documentation_not_case_rows"] is not True
            or any(type(d[k]) is not int or d[k]!=0 for k in (
                "source_originals_downloaded","case_outcomes_examined","AB_cycles_executed"))
            or any(d[k] is not False for k in (
                "terms_accepted","complete_independent_registration_denominator",
                "historical_vintages_of_same_case_distribution",
                "source_local_identifiers_exported"))
            or d["confirmed_first_public_at"] is not None
            or type(d["documentary_routes"]) is not list or len(d["documentary_routes"])!=6
            or {r["source_id"] for r in d["documentary_routes"]}!=set(ALLOWED)):
        raise ValueError("R12_SOURCE_MANIFEST_SCHEMA_OR_EVIDENCE_PROMOTED")
    return [_check_asset(r) for r in d["documentary_routes"]]


def status(*,as_of:str|None=None,path:Path|None=None):
    t=utc(as_of) if as_of is not None else None
    base={
        "schema":"pfl.r12.normative_appeals_discovery.v1",
        "as_of":as_of,"independent_risk_denominator":None,
        "real_outcome_events":None,"real_censoring":None,
        "first_public_at":None,"scientific_cycles":0,
        "source_groups_additive":False,
    }
    hidden={
        "source_count":None,"normative_route_count":None,
        "appeals_route_count":None,"source_routes":[],
        "source_manifest_sha256":None,"source_documentary_safe_by":None,
        "pan_is_not_intake_denominator":None,
        "tacrc_multiple_resources_per_resolution":None,
        "licensed_tarcja_csv_does_not_license_intake":None,
    }
    if t is not None and t<SAFE_BY:
        return {**base,**hidden,"status":"R12_NOT_KNOWN_AT_CUT"}
    try:
        rows=_load(path or MANIFEST)
    except (OSError,ValueError,TypeError,KeyError,AttributeError):
        return {**base,**hidden,"status":"R12_SOURCE_QUARANTINED"}
    return {**base,"status":"R12_DOCUMENTARY_ONLY_NO_ADMISSIBLE_POPULATION",
            "source_count":6,"normative_route_count":3,
            "appeals_route_count":3,"source_routes":rows,
            "source_manifest_sha256":PIN,
            "source_documentary_safe_by":SAFE_BY.isoformat(),
            "pan_is_not_intake_denominator":True,
            "tacrc_multiple_resources_per_resolution":True,
            "licensed_tarcja_csv_does_not_license_intake":True,
            "legal_normative_exceptions_are_not_missing_outcomes":True,
            "decision_publication_is_not_resource_filing":True,
            "boe_is_not_denominator_of_unpublished_drafts":True,
            "historical_original_case_vintage_pairs_verified":0}
