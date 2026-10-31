"""Project R10 worker discovery into a no-case-id, no-outcome public index.

The scratch matrices include only official metadata but have richer indexed
prose than the observatory should redistribute. Verify SHA on their bytes,
restrict to a fixed set of source and route IDs, preserve only official URLs
and explicitly negative selection/rights claims. Zero downloads or AB cycles.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
REGIONAL=ROOT.parent/"PFL-scratch-congreso2-20261031/ronda10/EVIDENCE_MATRIX.json"
NATIONAL=ROOT.parent/"PFL-scratch-links2-20261031/ronda10/ROUTE_MATRIX.json"
OUTPUT=ROOT/"data/source_manifests/r10_documentary_constraints_redacted_20261031.json"
REGIONAL_SHA="16a34a6e596b00212ca84f89bbc0e17f9b3b77b32d363387790ce60ab11583d2"
NATIONAL_SHA="d7ec41fd797ba91cb9f416bde1ea238e9f8b29a68847f984b5649783c0967f2d"
REGION_CLASS={
    "andalucia_ilpa_xii_jea":"POST_MESA_REFERRED_ONLY_NOT_ALL_RECEIVED",
    "andalucia_jea_rights":"NO_EXPLICIT_OPEN_ILPA_DISTRIBUTION_RIGHTS",
    "andalucia_agrupa_march2026":"REGISTRATION_CHANNEL_REGIME_BREAK_NOT_SOURCE_VINTAGE",
    "castilla_y_leon_xi_dissolution_feb2026":"PENDING_AT_DISSOLUTION_IS_SURVIVOR_SELECTED_STOCK",
    "castilla_y_leon_xii_continuity_april2026":"TRANSFER_NOTICE_NOT_COMPLETE_ORIGINAL_ENTRY_FRAME",
    "castilla_y_leon_rights_and_ILP_protocol":"GENERAL_PAGE_RIGHTS_NOT_DATASET_REUSE",
}
NATIONAL_CLASS={
    "R10_A_CTBG_APPEALS":"APPEALS_RECEIVED_DISTINCT_FROM_RESOLUTIONS_AND_INITIAL_REQUESTS",
    "R10_B_CNMC_PUBLIC_CONSULTATIONS":"PUBLISHED_CONTRIBUTIONS_CONDITIONED_ON_CONFIDENTIALITY",
    "R10_C_BASQUE_PARLIAMENT_REGISTER":"UPSTREAM_REGISTRY_LEGAL_BUT_NOT_PUBLIC_COMPLETE_DATASET",
}

def _get(path:Path,expected:str):
    if not path.is_file() or path.is_symlink() or not 3000<path.stat().st_size<30000:
        raise ValueError("R10_SOURCE_MATRIX_MISSING_OR_BAD_SIZE")
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=expected:
        raise ValueError("R10_WORKER_MATRIX_SHA_DRIFT")
    return json.loads(raw.decode("utf8"))

def _url(value):
    if not isinstance(value,str) or not value.startswith("https://"):
        raise ValueError("R10_UNVERIFIED_SOURCE_URL")
    p=urlsplit(value)
    if (not p.hostname or p.username or p.password or p.port is not None or p.fragment
            or p.hostname not in {
                "juntaelectoral.parlamentodeandalucia.es","www.parlamentodeandalucia.es",
                "www.ccyl.es","consejodetransparencia.es","www.cnmc.es",
                "cnmc.es","data.cnmc.es","administracion.gob.es",
                "laadministracionaldia.inap.es","www.legebiltzarra.eus",
                "www.coprepa.es","www.adi.legebiltzarra.eus"}):
        raise ValueError("R10_SOURCE_ORIGIN_OUTSIDE_SCOPE")
    return value

def sanitize():
    reg=_get(REGIONAL,REGIONAL_SHA)
    nat=_get(NATIONAL,NATIONAL_SHA)
    if (reg.get("schema")!="PFL_R10_PARLIAMENTARY_ILP_STAGE_RIGHTS_MATRIX_V1"
            or reg.get("real_source_direct_GETs")!=0 or reg.get("source_records_downloaded")!=0
            or reg.get("real_source_SHA256") is not None
            or reg.get("first_public_at") is not None
            or reg.get("R5_AJ_not_executed") is not True
            or reg.get("outcomes_compared_or_modelled") is not False
            or reg.get("documentary_status_headings_seen_pre_AJ") is not True):
        raise ValueError("R10_REGIONAL_WORKER_PROMOTION")
    policy=nat.get("capture_policy",{})
    if (nat.get("schema")!="pfl.links2.r10.three_distinct_routes.v1"
            or any(policy.get(k)!=0 for k in (
                "GET_originals","HEAD_originals","original_bytes",
                "asset_specific_licenses_adjudicated_for_get",
                "licenses_accepted_in_users_name","cookies_or_access_bypass",
                "person_rows","outcomes_read_or_analyzed","AB_cycles",
                "PFL_trabajo_writes","Git_operations"))
            or policy.get("original_sha256") is not None
            or policy.get("parser_sha_prefrozen_for_source_ingestion") is not False):
        raise ValueError("R10_NATIONAL_WORKER_PROMOTION")
    regional=reg.get("rows")
    national=nat.get("routes")
    if (not isinstance(regional,list) or len(regional)!=6
            or {x["id"] for x in regional}!=set(REGION_CLASS)
            or not isinstance(national,list) or len(national)!=3
            or {x["id"] for x in national}!=set(NATIONAL_CLASS)):
        raise ValueError("R10_WORKER_ROUTE_SCOPE_CHANGED")
    regions=[]
    for x in regional:
        if (x.get("direct_GET") is not False or x.get("original_sha256") is not None
                or x.get("first_public_at") is not None
                or x.get("specific_dataset_distribution_url") is not None
                or x.get("specific_dataset_license_url") is not None):
            raise ValueError("R10_REGION_UNVERIFIED_ORIGINAL_OR_RIGHTS")
        url=_url(x["source_url"] if "source_url" in x else x["source_urls"][0])
        regions.append({
            "source_id":x["id"],"institution":x["institution"],
            "official_document_url":url,"scope_failure_code":REGION_CLASS[x["id"]],
            "documentary_only":True,"no_original_get":True,
            "all_received_register_count":None,"data_distribution_licence":None,
            "known_case_decisions":None,"first_public_at":None,
        })
    nations=[]
    for x in national:
        if (x.get("asset_distribution_get_allowed") is not False
                or x.get("original_sha256") is not None
                or x.get("first_public_at") is not None):
            raise ValueError("R10_NATIONAL_ORIGINAL_OR_RIGHTS_PROMOTION")
        nations.append({
            "source_id":x["id"],"institution":x["institution"],
            "entry_unit":x["primary_entry_unit"],
            "selection_failure_code":NATIONAL_CLASS[x["id"]],
            "rights_to_acquire_case_source":False,
            "all_received_register_count":None,"real_original_sha256":None,
            "independent_entry_denominator":None,"first_public_at":None,
        })
    return {
        "schema":"pfl.r10.documentary_constraints_redacted.v1",
        "audit_day_utc":"2026-10-31",
        "upstream_private_worker_matrices_sha256":{
            "regional":REGIONAL_SHA,"national":NATIONAL_SHA,
        },
        "no_source_ids_or_outcome_values_exported":True,
        "real_source_originals_downloaded":0,
        "AB_cycles_executed":0,
        "pre_AJ_outcome_category_headings_seen":True,
        "all_received_denominator_certified":False,
        "historic_first_public_at_verified":False,
        "and_unverified_agrupa_effective_on":"2026-03-20",
        "and_measurement_channel_overlap_requires_controls":True,
        "regional_documentary_assets":regions,
        "distinct_institutional_entry_routes":nations,
    }

if __name__=="__main__":
    if OUTPUT.exists():
        raise ValueError("R10_REDACTED_OUTPUT_ALREADY_EXISTS")
    raw=(json.dumps(sanitize(),indent=2,ensure_ascii=False)+"\n").encode("utf8")
    OUTPUT.write_bytes(raw)
    print("R10_REDACTED",sha256(raw).hexdigest(),len(raw))
