"""Pin and REDACT independent R11 scratch findings into source metadata.

Do not copy original case IDs, allegations, participants, titles or outcomes.
License declarations are not permission to accept binding third-party terms.
Source matrices are private and their SHA must match before deriving output.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
MUNICIPAL=ROOT.parent/"PFL-scratch-congreso2-20261031/ronda11/EVIDENCE_MATRIX.json"
ECONOMIC=ROOT.parent/"PFL-scratch-links2-20261031/ronda11/OFFICIAL_SOURCE_MATRIX.json"
OUTPUT=ROOT/"data/source_manifests/r11_scoped_documentary_gates_20261031.json"
MUNICIPAL_SHA="ef8815c545e14634a0198ec0a61642344723812a8ae35aea836b39672de6e830"
ECONOMIC_SHA="18fa7bb8d486c87378160a0b999da7c63025a12042d8fd42f55b864d62c7b0b7"
MUNICIPAL_RULES={
    "R11-A":("FORMAL_ACCESS_REQUEST_CASE","CC_BY_4_CATALOGUE_WITH_BINDING_PORTAL_TERMS",
             "ALL_RECEIVED_CLAIM_NOT_INDEPENDENTLY_RECONCILED"),
    "R11-REGISTRY-COMPARATOR":("GENERAL_ADMINISTRATIVE_WRITING","CC_BY_4_WITH_BINDING_PORTAL_TERMS",
             "NO_OFFICIAL_CROSSWALK_TO_AIP_OR_CITIZEN_PROPOSALS"),
    "R11-B":("PLATFORM_PUBLISHED_PROPOSAL","CC_BY_4_WITH_BINDING_PORTAL_TERMS",
             "DRAFT_OR_UNPUBLISHED_ENTRY_UNIVERSE_UNVERIFIED"),
    "R11-C":("CANODROM_PARTICIPATION_SPACE_PROPOSAL","ODBL_DBCL_PLUS_ACCESS_TERMS",
             "NOT_CITYWIDE_FORMAL_INITIATIVE_REGISTER"),
}
ECONOMIC_RULES={
    "R11_A_PLACSP":("PUBLIC_TENDER_REVISION","MINISTRY_REUSE_TERMS_BY_USE",
                    "REPEATED_ATOM_VERSIONS_AND_2026_COVERAGE_OUTAGE"),
    "R11_B_BDNS":("PUBLIC_SUBSIDY_CALL","SNPSAP_REUSE_AND_PRIVACY_TERMS",
                    "CANONICAL_INSTRUMENTAL_AND_PUBLIC_GRANTS_DIFFER"),
    "R11_C_COOPERATION_REGISTERS":("SIGNED_REGISTERED_AGREEMENT","RIOJA_CC_BY_AND_DISTRIBUTION_REVIEW",
                    "ONE_ROW_PER_PARTICIPANT_AND_NO_FAILED_PROPOSAL_REGISTER"),
}
ECONOMIC_URL_IDS={
    "R11_A_PLACSP":"PLACSP_HACIENDA_PROFILE_FEED",
    "R11_B_BDNS":"BDNS_SNPSAP_API_DOC",
    "R11_C_COOPERATION_REGISTERS":"COOP_RIOJA_STATE_CATALOG",
}
HOSTS={
    "datos.madrid.es","decidim.canodrom.barcelona",
    "www.hacienda.gob.es","www.infosubvenciones.es","datos.gob.es",
}


def _load(path:Path,pin:str):
    if not path.is_file() or path.is_symlink() or not 3000<path.stat().st_size<40000:
        raise ValueError("R11_WORKER_FILE_NOT_AVAILABLE")
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=pin:
        raise ValueError("R11_WORKER_SOURCE_SHA_CHANGED")
    return json.loads(raw.decode("utf-8"))


def _url(value:str):
    if not isinstance(value,str) or len(value)>1500:
        raise ValueError("R11_INVALID_URL")
    u=urlsplit(value)
    if (u.scheme!="https" or u.hostname not in HOSTS
            or u.username or u.password or u.port is not None or u.fragment):
        raise ValueError("R11_UNTRUSTED_URL_HOST_OR_FEATURE")
    return value


def sanitized():
    m=_load(MUNICIPAL,MUNICIPAL_SHA)
    e=_load(ECONOMIC,ECONOMIC_SHA)
    if (m.get("schema")!="PFL_R11_MUNICIPAL_PARTICIPATION_ROUTES_DOCUMENTARY_V1"
            or m.get("original_dataset_gets")!=0 or m.get("original_downloads")!=0
            or m.get("real_records_seen_by_offline_instrument")!=0
            or m.get("outcome_analysis") is not False
            or m.get("scientific_R5_gate")!="STOP" or m.get("first_public_at") is not None):
        raise ValueError("R11_MUNICIPAL_SCIENTIFIC_PROMOTION")
    if (e.get("schema")!="pfl.links2.r11.economic_administrative_metadata.v1"
            or any(e.get(k)!=0 for k in (
                "original_data_get","original_data_head","original_bytes",
                "terms_accepted","person_records_inspected","outcome_records_inspected",
                "AB_cycles","Git_operations","PFL_trabajo_writes"))
            or e.get("rights_for_original_ingestion_adjudicated") is not False
            or e.get("original_sha256") is not None
            or e.get("population_source")!="NONE_ADMITTED"):
        raise ValueError("R11_ECONOMIC_SCIENTIFIC_PROMOTION")
    mr=m.get("routes")
    er=e.get("routes")
    if (type(mr)!=list or len(mr)!=4
            or {x["id"] for x in mr}!=set(MUNICIPAL_RULES)
            or type(er)!=list or len(er)!=3
            or {x["id"] for x in er}!=set(ECONOMIC_RULES)):
        raise ValueError("R11_ROUTE_IDS_CHANGED_OR_DUPLICATED")
    result=[]
    for x in mr:
        kind,rights,blocking=MUNICIPAL_RULES[x["id"]]
        permissions=x["rights"]
        if (permissions.get("download_allowed_in_this_round") is not False
                or x.get("source_data_sha256") is not None
                or x.get("first_public_at") is not None):
            raise ValueError("R11_MUNICIPAL_ORIGINAL_OR_RIGHTS_PROMOTION")
        url=_url(x.get("catalogue_url",x.get("source_metadata_url",x.get("source_catalogue_url"))))
        result.append({
            "route_id":x["id"],"origin":"MUNICIPAL_METADATA",
            "institution":x["institution"],"primary_catalogue_url":url,
            "institutional_entry_unit":kind,"rights_evaluation":rights,
            "independent_frame_block":blocking,
            "originals_acquired":0,"reuser_conditions_accepted":False,
            "case_level_denominator_verified":None,"outcomes_evaluated":None,
            "historical_first_public_at":None,
        })
    indexed={x["id"]:x for x in e.get("sources",[])}
    for x in er:
        kind,rights,blocking=ECONOMIC_RULES[x["id"]]
        if (x.get("safe_ingestion") is not False
                or x.get("original_sha256") is not None
                or x.get("first_public_at") is not None
                or x.get("independent_total_verified") is not False):
            raise ValueError("R11_ECONOMIC_ORIGINAL_OR_DENOMINATOR_PROMOTION")
        source=indexed[ECONOMIC_URL_IDS[x["id"]]]
        result.append({
            "route_id":x["id"],"origin":"ECONOMIC_ADMINISTRATIVE_METADATA",
            "institution":x["institution"],
            "primary_catalogue_url":_url(source["url"]),
            "institutional_entry_unit":kind,"rights_evaluation":rights,
            "independent_frame_block":blocking,
            "originals_acquired":0,"reuser_conditions_accepted":False,
            "case_level_denominator_verified":None,"outcomes_evaluated":None,
            "historical_first_public_at":None,
        })
    return {
        "schema":"pfl.r11.scoped_documentary_gates_redacted.v1",
        "discovery_day_utc":"2026-10-31",
        "upstream_private_worker_sha256":{
            "municipal":MUNICIPAL_SHA,"economic":ECONOMIC_SHA,
        },
        "reuser_terms_accepted":False,
        "real_original_datasets_acquired":0,"real_case_outcomes_read":0,
        "scientific_cycles_executed":0,
        "admissible_population_complete":False,
        "historical_public_witness_verified":False,
        "publisher_same_origin_counts_independent":False,
        "case_identifiers_or_person_data_exported":False,
        "source_routes":result,
    }


if __name__=="__main__":
    if OUTPUT.exists():
        raise ValueError("R11_PUBLISHED_DOCUMENT_EXISTS_NO_OVERWRITE")
    out=(json.dumps(sanitized(),ensure_ascii=False,indent=2)+"\n").encode()
    OUTPUT.write_bytes(out)
    print("R11_REDACTED_SHA256",hashlib.sha256(out).hexdigest())
