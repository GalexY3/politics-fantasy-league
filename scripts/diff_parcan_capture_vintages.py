"""Prospective, OFFLINE and aggregate-only source-vintage differ for Canarias.

Not a scientific outcome reader. Expects TWO independently captured copies of
the SAME type/year/legislature, each in a separate outside-Git directory.
It never downloads. It verifies raw SHA against a receipt but explicitly does
not assert that a caller-supplied receipt authenticates the publisher.

ADDED_IN_NEW_CAPTURE != NEWLY_REGISTERED_ON_THAT_DAY.
MISSING_IN_NEW_CAPTURE != REJECTED/DELETED/FAILED.
F_CREACION != first_public_at. No status or finalization cells are examined.
Only repeated prospective captures could establish *local* observation windows.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

from build_parcan_local_processes import parse_metadata, IngestError

REPO = Path(__file__).resolve().parents[1]
SCHEMA = "pfl.parcan.prospective_capture_receipt.v1"
DATASET = re.compile(r"https://datos\.parcan\.es/dataset/iniciativas_tipo[a-z]{2,8}_anio20\d{2}_[a-z0-9]+\Z")
URL = re.compile(r"https://www\.parcan\.es/api/iniciativas/20\d{2}/\d{1,2}/[A-Z]{2,8}/\?format=csv\Z")
HEX = re.compile(r"[0-9a-f]{64}\Z")


def _utc(value: object) -> datetime:
    if not isinstance(value, str) or "T" not in value:
        raise IngestError("CAPTURE_CLOCK_REQUIRED")
    try:
        clock=datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError as exc:
        raise IngestError("BAD_CAPTURE_CLOCK") from exc
    if clock.tzinfo is None or clock.utcoffset() is None:
        raise IngestError("NAIVE_CAPTURE_CLOCK")
    return clock.astimezone(timezone.utc)


def _no_dupes(pairs):
    d={}
    for k,v in pairs:
        if k in d:
            raise IngestError("DUPLICATE_JSON_KEY")
        d[k]=v
    return d


def read_vintage(directory:Path, *, receipt_sha256:str) -> dict:
    """Read immutable raw CSV outside Git. Return IDs only in private memory."""
    if not isinstance(receipt_sha256,str) or not HEX.fullmatch(receipt_sha256):
        raise IngestError("PINNED_RECEIPT_SHA_REQUIRED")
    if directory.is_symlink():
        raise IngestError("SYMLINK_DIRECTORY_FORBIDDEN")
    folder=directory.resolve(strict=True)
    if (REPO == folder or REPO in folder.parents
            or REPO.parent not in folder.parents or not folder.is_dir()):
        raise IngestError("RAW_MUST_BE_OUTSIDE_GIT")
    receipt_path=folder/"capture_receipt.json"
    if receipt_path.is_symlink() or not receipt_path.is_file() or receipt_path.stat().st_size>20_000:
        raise IngestError("RECEIPT_MISSING_OR_SYMLINK")
    raw_receipt=receipt_path.read_bytes()
    if sha256(raw_receipt).hexdigest()!=receipt_sha256:
        raise IngestError("RECEIPT_PIN_MISMATCH")
    receipt=json.loads(raw_receipt.decode("utf-8"),object_pairs_hook=_no_dupes,
                       parse_constant=lambda _: (_ for _ in ()).throw(IngestError("NONFINITE")))
    if not isinstance(receipt,dict) or set(receipt)!={
            "schema", "source_publisher", "scope", "canonical_url",
            "catalogue_url", "catalogue_licence_label", "rights_review_state",
            "terms_accepted", "http_status", "original_filename",
            "original_sha256", "original_bytes", "capture_completed_at",
            "first_public_at", "outcomes_analyzed"}:
        raise IngestError("INVALID_RECEIPT_CONTRACT")
    scope=receipt["scope"]
    if (receipt["schema"]!=SCHEMA
        or receipt["source_publisher"]!="Parlamento de Canarias"
        or not isinstance(scope,dict) or set(scope)!={"year","legislature","type"}
        or type(scope["year"]) is not int or not 2020<=scope["year"]<=2100
        or type(scope["legislature"]) is not int or not 1<=scope["legislature"]<=40
        or not isinstance(scope["type"],str)
        or re.fullmatch(r"[A-Z]{2,8}",scope["type"]) is None
        or receipt["canonical_url"] !=
           f"https://www.parcan.es/api/iniciativas/{scope['year']}/{scope['legislature']}/{scope['type']}/?format=csv"
        or not isinstance(receipt["catalogue_url"],str)
        or not DATASET.fullmatch(receipt["catalogue_url"])
        or receipt["catalogue_licence_label"]!="odc-pddl"
        or receipt["rights_review_state"]!="CATALOGUE_LABEL_ONLY_NO_PERSONAL_USE_ADJUDICATION"
        or receipt["terms_accepted"] is not False
        or receipt["http_status"]!=200 or type(receipt["http_status"]) is not int
        or receipt["first_public_at"] is not None
        or receipt["outcomes_analyzed"] is not False):
        raise IngestError("UNTRUSTED_OR_CHANGED_SOURCE_SCOPE")
    # Only a plain filename: never a caller-specified traversal path.
    name=receipt["original_filename"]
    if not isinstance(name,str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,90}\.csv",name):
        raise IngestError("UNSAFE_RAW_FILENAME")
    original=folder/name
    if original.is_symlink() or not original.is_file():
        raise IngestError("RAW_MISSING_OR_SYMLINK")
    raw=original.read_bytes()
    digest=receipt["original_sha256"]
    if (not isinstance(digest,str) or not HEX.fullmatch(digest)
            or type(receipt["original_bytes"]) is not int
            or receipt["original_bytes"]!=len(raw)
            or sha256(raw).hexdigest()!=digest):
        raise IngestError("ORIGINAL_SHA_AND_BYTES_MISMATCH")
    clock=_utc(receipt["capture_completed_at"])
    records,stats=parse_metadata(raw,legislature=scope["legislature"],
             kind=scope["type"],year=scope["year"],
             source_sha=digest,captured_utc=clock.isoformat())
    if stats["year_mismatch_rows"]!=0:
        raise IngestError("SOURCE_YEAR_MISMATCH")
    # Private process IDs used solely for in-memory comparison, never output.
    return {"scope":scope,"captured_at":clock,"sha256":digest,
            "receipt_sha256":receipt_sha256,
            "records":{r["source_process_id"]:r["created_on"] for r in records}}


def compare(earlier:dict, later:dict) -> dict:
    if earlier["scope"]!=later["scope"]:
        raise IngestError("CROSS_INSTITUTION_OR_COHORT_JOIN_FORBIDDEN")
    if earlier["captured_at"]>=later["captured_at"]:
        raise IngestError("OUT_OF_ORDER_SOURCE_VINTAGES")
    old,new=earlier["records"],later["records"]
    if not isinstance(old,dict) or not isinstance(new,dict):
        raise IngestError("RECORDS_REQUIRE_MAPPING")
    old_ids,new_ids=set(old),set(new)
    changed=sum(old[k]!=new[k] for k in old_ids & new_ids)
    return {
        "schema":"pfl.parcan.prospective_vintage_diff.v1",
        "publisher":"Parlamento de Canarias",
        "scope":earlier["scope"],
        "earlier_original_sha256":earlier["sha256"],
        "later_original_sha256":later["sha256"],
        "earlier_receipt_sha256":earlier["receipt_sha256"],
        "later_receipt_sha256":later["receipt_sha256"],
        "earlier_local_capture":earlier["captured_at"].isoformat(),
        "later_local_capture":later["captured_at"].isoformat(),
        "earlier_observed_rows":len(old),
        "later_observed_rows":len(new),
        "same_source_id_and_creation_date":sum(old[k]==new[k] for k in old_ids&new_ids),
        "source_ids_present_only_in_later_capture":len(new_ids-old_ids),
        "source_ids_absent_in_later_capture":len(old_ids-new_ids),
        "source_reported_creation_date_changed":changed,
        "absence_is_not_terminal_outcome":True,
        "new_presence_is_not_newly_registered_at_capture":True,
        "publisher_census_independent_of_snapshots":None,
        "first_public_at_confirmed":None,
        "outcome_transitions_examined":False,
        "legal_and_privacy_release_adjudicated":False,
        "cross_institution_joins":0,
        "source_ids_or_person_rows_exported":False,
        "historical_asof_eligible":False,
        "scientific_abh_cycles":0,
    }


def run(*, earlier:Path,later:Path,earlier_receipt_sha:str,later_receipt_sha:str,
        output:Path) -> dict:
    dest=output.resolve(strict=False)
    if (REPO==dest or REPO in dest.parents or dest.exists()
            or REPO.parent not in dest.parents or not dest.parent.is_dir()):
        raise IngestError("OUTPUT_MUST_BE_NEW_OUTSIDE_GIT")
    a=read_vintage(earlier,receipt_sha256=earlier_receipt_sha)
    b=read_vintage(later,receipt_sha256=later_receipt_sha)
    report=compare(a,b)
    with dest.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(report,f,sort_keys=True,indent=2,ensure_ascii=False)
        f.write("\n")
    return {"status":"SOURCE_LOCAL_DIFF_METADATA_ONLY", "sha256":sha256(dest.read_bytes()).hexdigest(),
            "previous":report["earlier_observed_rows"],"later":report["later_observed_rows"]}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Offline source-local metadata diff: NEVER claims historic first_public_at")
    parser.add_argument("--earlier",type=Path,required=True)
    parser.add_argument("--later",type=Path,required=True)
    parser.add_argument("--earlier-receipt-sha",required=True)
    parser.add_argument("--later-receipt-sha",required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(earlier=args.earlier,later=args.later,
        earlier_receipt_sha=args.earlier_receipt_sha,later_receipt_sha=args.later_receipt_sha,
        output=args.output),sort_keys=True))
