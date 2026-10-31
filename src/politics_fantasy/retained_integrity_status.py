"""SHA-locked public summary of a *past local* binary integrity inspection.

No private file is opened by this read-only status adapter. The trusted check
is the offline receipt produced by scripts/attest_retained_sources.py with
fixed paths and source hashes. The receipt is valid evidence ONLY that those
bytes matched on the local PC at audit completion, never that the sources are
legally reusable in a new context, historically public or population complete.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from .procedural_index_contract import utc
from .retained_source_integrity import PINS

ROOT=Path(__file__).resolve().parents[2]
RECEIPT=ROOT/"data/source_manifests/r9_retained_sources_integrity_20261031.json"
PINNED_SHA="67ae2bc5955e98cafd083ca1e8ba0ea1fe8544cc153a4f9f5e9ce6fb62a9d99a"
AUDIT_SECOND=datetime(2026,10,31,7,8,41,tzinfo=timezone.utc)
SAFE_BY=datetime(2026,10,31,7,8,42,tzinfo=timezone.utc)


def _unique_pairs(pairs):
    ret={}
    for k,v in pairs:
        if k in ret:
            raise ValueError("DUPLICATE_SOURCE_RECEIPT_KEY")
        ret[k]=v
    return ret


def _load(path:Path):
    if path.is_symlink() or not path.is_file() or not 1000 < path.stat().st_size < 5000:
        raise ValueError("BAD_SOURCE_RECEIPT_PATH_OR_SIZE")
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=PINNED_SHA:
        raise ValueError("SOURCE_RECEIPT_PINNED_SHA_MISMATCH")
    obj=json.loads(raw.decode("utf8"),object_pairs_hook=_unique_pairs,
                   parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE_SOURCE_RECEIPT")))
    if (type(obj)!=dict or set(obj)!={
            "schema","verified_by","audit_completed_second_utc","local_audit_safe_by",
            "all_pinned_files_byte_verified","source_total_files",
            "official_original_files","private_derivatives_files",
            "official_original_bytes","private_derived_bytes",
            "records_decoded_or_case_ids_exposed",
            "source_content_examined_for_outcomes","first_public_at",
            "institutional_all_received_denominator",
            "permission_for_additional_processing_adjudicated_here",
            "historical_public_vintage_verified","source_originals_published_in_git",
            "scientific_cycles","sources"
            } or obj["schema"]!="pfl.retained_source_integrity_receipt.v1"
            or obj["verified_by"]!="BINARY_SHA256_AND_BYTE_LENGTH_ONLY"
            or utc(obj["audit_completed_second_utc"])!=AUDIT_SECOND
            or utc(obj["local_audit_safe_by"])!=SAFE_BY
            or obj["all_pinned_files_byte_verified"] is not True
            or type(obj["source_total_files"]) is not int or obj["source_total_files"]!=7
            or type(obj["official_original_files"]) is not int or obj["official_original_files"]!=5
            or type(obj["private_derivatives_files"]) is not int or obj["private_derivatives_files"]!=2
            or type(obj["records_decoded_or_case_ids_exposed"]) is not int
            or obj["records_decoded_or_case_ids_exposed"]!=0
            or type(obj["scientific_cycles"]) is not int or obj["scientific_cycles"]!=0
            or obj["source_content_examined_for_outcomes"] is not False
            or obj["first_public_at"] is not None
            or obj["institutional_all_received_denominator"] is not None
            or obj["permission_for_additional_processing_adjudicated_here"] is not False
            or obj["historical_public_vintage_verified"] is not False
            or obj["source_originals_published_in_git"] is not False):
        raise ValueError("SOURCE_RECEIPT_SCIENTIFIC_PROMOTION")
    source_records=obj["sources"]
    if type(source_records)!=list or len(source_records)!=len(PINS):
        raise ValueError("SOURCE_RECEIPT_SCOPE_CHANGED")
    if any(type(s)!=dict or set(s)!={
            "source_id","role","sha256","bytes","matching_original_on_this_local_PC"}
            or s["source_id"]!=p.source_id or s["role"]!=p.role
            or s["sha256"]!=p.sha256 or type(s["bytes"]) is not int or s["bytes"]!=p.nbytes
            or s["matching_original_on_this_local_PC"] is not True
            for s,p in zip(source_records,PINS)):
        raise ValueError("SOURCE_RECEIPT_BYTES_NOT_THE_PINS")
    if (obj["official_original_bytes"] != sum(p.nbytes for p in PINS if p.role=="OFFICIAL_CAPTURE_ORIGINAL")
            or obj["private_derived_bytes"] != sum(p.nbytes for p in PINS if p.role=="PRIVATE_DERIVED_METADATA")):
        raise ValueError("SOURCE_RECEIPT_BYTE_TOTALS_WRONG")
    return obj


def status(*,as_of:str|None=None,path:Path|None=None):
    t=utc(as_of) if as_of is not None else None
    base={
        "schema":"pfl.retained_integrity_status.v1",
        "as_of":as_of,
        "historical_first_public_at":None,
        "complete_institutional_denominator":None,
        "source_use_rights_for_inference_established":False,
        "verified_historical_vintages":False,
        "actual_original_bytes_in_api_response":False,
        "case_identifiers_in_response":False,
        "individual_outcomes_in_response":False,
        "scientific_cycles":0,
    }
    if t is not None and t<SAFE_BY:
        return {**base, "status":"INTEGRITY_AUDIT_NOT_KNOWN_AT_CUT",
                "originals_verified":None, "private_derivatives_verified":None,
                "total_files_verified":None, "local_audit_safe_by":None,
                "receipt_sha256":None, "source_rows":[]}
    try:
        doc=_load(path if path is not None else RECEIPT)
    except (ValueError,OSError,TypeError,KeyError,AttributeError):
        return {**base,"status":"INTEGRITY_RECEIPT_QUARANTINED",
                "originals_verified":None,"private_derivatives_verified":None,
                "total_files_verified":None,"local_audit_safe_by":None,
                "receipt_sha256":None,"source_rows":[]}
    return {**base,"status":"PAST_LOCAL_BINARY_INTEGRITY_CONFIRMED",
            "originals_verified":doc["official_original_files"],
            "private_derivatives_verified":doc["private_derivatives_files"],
            "total_files_verified":doc["source_total_files"],
            "local_audit_safe_by":SAFE_BY.isoformat(),
            "receipt_sha256":PINNED_SHA,
            "source_rows":[{"source_id":p.source_id,"role":p.role,
                            "sha256":p.sha256,"bytes":p.nbytes}
                           for p in PINS],
            "scope":"LOCAL_BINARY_INTEGRITY_AT_AUDIT_NOT_CONTINUOUS_SOURCE_VERIFICATION",
            "rights_status":"NO_NEW_USE_RIGHTS_OR_BULK_ACCESS_GRANTED",
            "science_status":"NO_REGISTRATION_CENSUS_NO_TRANSITIONS_NO_OUTCOMES",
            }
