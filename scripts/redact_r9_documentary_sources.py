"""Publish sanitized R9 documentary inventory, never worker source-local IDs.

Scratch originals are separately retained OUTSIDE Git. This script checks
their complete SHA before deriving a deliberately lossy, privacy-minimized
inventory. All source numbers and individual ids are excluded, as are any
outcomes. Published records are source descriptions, NOT institution cases.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
REGIONAL=ROOT.parent/"PFL-scratch-congreso2-20261031/ronda9/EVIDENCE_MATRIX.json"
NATIONAL=ROOT.parent/"PFL-scratch-links2-20261031/ronda9/OFFICIAL_SOURCE_MATRIX.json"
REGIONAL_OUTPUT=ROOT/"data/source_manifests/r9_regional_documentary_redacted_20261031.json"
NATIONAL_OUTPUT=ROOT/"data/source_manifests/r9_national_documentary_redacted_20261031.json"

# Both worker source-matrix SHA digests were rechecked byte-for-byte locally.
REGIONAL_SOURCE_SHA="6a64b4b356f5798f859f8c4ebdb288f4f5ad048a1d3e8a4fdff9aeba2ad438a1"
NATIONAL_SOURCE_SHA="c2546633789b56723e5dc815cc227da7e3b2cbe536c8dc75819edb950320e32c"

REGIONAL_CODES={
    "galicia_ix_ppli_retrospective":"RETROSPECTIVE_ENTRY_AND_MESA_INDEX_NOT_REGISTRY_CENSUS",
    "galicia_x_ppli_retrospective":"CONTRADICTORY_EDITORIAL_HEADING_AND_ENNUMERATION",
    "galicia_xi_partial_semester_reports":"DISTINCT_PERIOD_REPORTS_NOT_CASE_PUBLICATION_VINTAGES",
    "galicia_legal_process_and_nonparliamentary_false_positive":"ADMINISTRATIVE_DATA_NOT_PARLIAMENTARY_ENTRIES",
    "valencia_ilp_html_list":"PAGINATED_EDITORIAL_ILP_NOT_INDEPENDENT_ALL_RECEIVED",
    "valencia_register_vs_initiatives_functions":"REGISTRY_AND_CASE_MANAGEMENT_DIFFERENT_OPERATIONS",
    "castilla_la_mancha_seres":"PROTECTED_ELECTRONIC_SUBMISSION_NOT_PUBLIC_BULK_DATA",
    "basque_parliament_ilp_open_xml_unverified":"UNLOCATED_SPECIFIC_ILP_DATASET_AND_LICENSE",
}

def _load(path:Path, pin:str)->dict:
    if not isinstance(pin,str) or len(pin)!=64:
        raise ValueError("SOURCE_SHA_NOT_PINNED")
    if path.is_symlink() or not path.is_file() or not 5000 < path.stat().st_size < 30000:
        raise ValueError("UNTRUSTED_WORKER_SOURCE")
    data=path.read_bytes()
    if sha256(data).hexdigest()!=pin:
        raise ValueError("WORKER_SOURCE_SHA_DRIFT")
    return json.loads(data.decode("utf8"))

def sanitized():
    regional=_load(REGIONAL,REGIONAL_SOURCE_SHA)
    national=_load(NATIONAL,NATIONAL_SOURCE_SHA)
    if (regional.get("schema")!="PFL_R9_ILP_SOURCE_RIGHTS_AND_COHORT_MATRIX_V1"
            or regional.get("real_direct_gets")!=0 or regional.get("raw_originals_saved")!=0
            or regional.get("outcome_columns_or_cases_aggregated") is not False
            or regional.get("first_public_at") is not None
            or regional.get("AB_cycles")!=0
            or regional.get("new_eligible_machine_readable_distributions")!=0):
        raise ValueError("UNSUPPORTED_REGIONAL_WORKER_PROMOTION")
    if (national.get("schema")!="pfl.links2.r9.national_intake_metadata.v1"
            or national.get("source_originals_get")!=0
            or national.get("source_original_bytes")!=0
            or national.get("outcome_analysis")!=0
            or national.get("AB_valid")!=0
            or national.get("reused_as_congress_population") is not False):
        raise ValueError("UNSUPPORTED_NATIONAL_WORKER_PROMOTION")
    entries=regional.get("entries")
    nrecords=national.get("source_records")
    if (not isinstance(entries,list) or len(entries)!=len(REGIONAL_CODES)
            or {x["id"] for x in entries}!=set(REGIONAL_CODES)
            or not isinstance(nrecords,list) or len(nrecords)!=11
            or len({x["id"] for x in nrecords})!=11):
        raise ValueError("R9_WORKER_SOURCE_SCOPE_INVALID")

    # Whitelist only categorical descriptors, stable official document URLs
    # and methodological negatives. NO free text or source case/reg IDs.
    clean_reg=[]
    for e in entries:
        urls=e.get("source_urls", [e.get("source_url")])
        if (not isinstance(urls,list) or not urls
                or any(not isinstance(u,str) or not u.startswith("https://") for u in urls)
                or e.get("downloaded_this_round") is not False
                or e.get("real_original_sha256") is not None
                or e.get("first_public_at") is not None):
            raise ValueError("REGIONAL_ASSET_NOT_DOCUMENTARY_ONLY")
        clean_reg.append({
            "id":e["id"],"institution":e["institution"],
            "family":e["family"],"official_urls":urls,
            "documentary_risk":REGIONAL_CODES[e["id"]],
            "rights_for_bulk_reuse_proven":False,
            "all_received_denominator":None,
            "source_original_sha256":None,
            "individual_source_local_ids_republished":False,
            "historical_source_vintages_certified":False,
            "outcomes_for_inference_admitted":False,
        })
    clean_national=[]
    for e in nrecords:
        if (e.get("original_sha256") is not None
                or e.get("first_public_at") is not None
                or e.get("eligible_for_census") is not False
                or e.get("per_case_history_verified") is not False
                or e.get("original_bytes_examined") is not False):
            raise ValueError("NATIONAL_SOURCE_ORIGINAL_OR_CENSUS_PROMOTION")
        clean_national.append({
            "id":e["id"],"institution":e["institution"],
            "unit":e["population"],"official_metadata_url":e["url"],
            "source_grain":e["documentation_type"],
            "rights_for_bulk_reuse_proven":False,
            "all_received_denominator":None,
            "source_original_sha256":None,
            "historical_source_vintages_certified":False,
            "case_outcomes_for_inference_admitted":False,
            "intake_count_from_unreplayed_original":None,
        })
    region={
        "schema":"pfl.r9.regional_documentary_redacted.v1",
        "audit_day_utc":"2026-10-31",
        "source_worker_matrix_sha256":REGIONAL_SOURCE_SHA,
        "preserved_full_matrix_outside_git":True,
        "source_local_ids_or_outcomes_published":False,
        "real_source_originals_downloaded":0,
        "scientific_cycles":0,
        "entries":clean_reg,
    }
    nation={
        "schema":"pfl.r9.national_documentary_redacted.v1",
        "audit_day_utc":"2026-10-31",
        "source_worker_matrix_sha256":NATIONAL_SOURCE_SHA,
        "preserved_full_matrix_outside_git":True,
        "source_local_ids_or_outcomes_published":False,
        "real_source_originals_downloaded":0,
        "scientific_cycles":0,
        "entries":clean_national,
    }
    return region,nation

if __name__=="__main__":
    region,nation=sanitized()
    for path,doc in [(REGIONAL_OUTPUT,region),(NATIONAL_OUTPUT,nation)]:
        if path.exists():
            raise ValueError(f"DESTINATION_EXISTS_{path.name}")
        data=(json.dumps(doc,ensure_ascii=False,indent=2)+"\n").encode("utf8")
        path.write_bytes(data)
        print(path.name,sha256(data).hexdigest(),len(doc["entries"]))
