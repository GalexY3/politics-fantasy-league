"""Append-only, offline PE/2025/XI SOURCE_LOCAL normalization outside Git.

Adds the previously missing 2025 stratum to local *metadata* without changing
the frozen 1,211-row 2023/2024/2026 v1 output or asserting historical as-of.
No outcomes, titles, persons, or real scoring leave the raw folder.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from build_parcan_local_processes import parse_metadata, strict_json, IngestError

REPO = Path(__file__).resolve().parents[1]
APPROVED_ROOT = REPO.parent
LAB = REPO / "research/PFL_SYSTEM20_20261031/PARCAN_COHORTS"
FILENAME = "parcan_2025_XI_PE_original.csv"
SOURCE_SHA256 = "13350568f6ef8f311b7bd8cb41791da1028550c98f3ef73bcc8bb4a78a7809ba"
METADATA_SHA256 = "0ce42317bd0802f7e7546483d26abcb63f1a9c128350fbe4f30ea007a2ce7ce3"
CAPTURE_SHA256 = "e96bc4a300fa1c886d0a33403ab9e9c67dec93525edc9f68ec7eb39270238c53"
FREEZE_SHA256 = "8ffab701bf241fbb591e9a37673497b57cb2ce544a7fe766c6c19c12d11a247a"


def checksum(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def safe_out(path: Path) -> Path:
    target = path.resolve(strict=False)
    if (target == APPROVED_ROOT or APPROVED_ROOT not in target.parents
            or target == REPO or REPO in target.parents):
        raise IngestError("INVALID_OUTSIDE_GIT_DESTINATION")
    if target.exists() or not target.parent.is_dir():
        raise IngestError("OUTPUT_MUST_BE_NEW")
    return target


def eligible_input(raw_dir: Path) -> tuple[bytes, str]:
    src = raw_dir.resolve(strict=True)
    if src == REPO or REPO in src.parents or APPROVED_ROOT not in src.parents:
        raise IngestError("INVALID_OUTSIDE_GIT_SOURCE")
    for name, expected in (
        ("PE2025_METADATA_ONLY_RECEIPT.json", METADATA_SHA256),
        ("PE2025_PRECAPTURE_FREEZE.json", FREEZE_SHA256),
    ):
        if checksum(LAB / name) != expected:
            raise IngestError("AUDIT_RECEIPT_CHANGED")
    freeze = strict_json(LAB / "PE2025_PRECAPTURE_FREEZE.json")
    for name, digest in freeze["instrument_sha256"].items():
        if checksum(LAB / name) != digest:
            raise IngestError("PRECAPTURE_INSTRUMENT_CHANGED")
    receipt_file = src / "capture_receipt.json"
    if checksum(receipt_file) != CAPTURE_SHA256:
        raise IngestError("RAW_RECEIPT_CHANGED")
    receipt = strict_json(receipt_file)
    if (receipt.get("state") != "RAW_CAPTURED_POPULATION_NOT_CERTIFIED"
            or receipt.get("http_status") != 200
            or receipt.get("raw_file") != FILENAME
            or receipt.get("raw_sha256") != SOURCE_SHA256
            or receipt.get("source_scope") != {"year": 2025, "legislature": 11,
                                                "initiative_type": "PE"}
            or receipt.get("catalogue_licence") != "odc-pddl"
            or receipt.get("interactive_terms_accepted") is not False
            or receipt.get("first_public_at") is not None):
        raise IngestError("SOURCE_PROVENANCE_NOT_ADMITTED")
    source = src / FILENAME
    if source.is_symlink() or not source.is_file():
        raise IngestError("ORIGINAL_MISSING_OR_SYMLINK")
    raw = source.read_bytes()
    if len(raw) != receipt["raw_bytes"] or sha256(raw).hexdigest() != SOURCE_SHA256:
        raise IngestError("ORIGINAL_SHA_OR_BYTES_CHANGED")
    return raw, receipt["finished_utc"]


def build(*, originals_dir: Path, output_dir: Path) -> dict:
    target = safe_out(output_dir)
    raw, captured = eligible_input(originals_dir)
    rows, stats = parse_metadata(
        raw, legislature=11, kind="PE", year=2025,
        source_sha=SOURCE_SHA256, captured_utc=captured)
    if len(rows) != 543 or stats["year_mismatch_rows"] != 0:
        raise IngestError("OUT_OF_SCOPE_OR_COUNT_MISMATCH")
    recorded = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for row in rows:
        row.update({"recorded_at": recorded, "source_capture_utc": captured})
        if (row["first_public_at"] is not None or row["terminal_state"] is not None
                or row["transition_events"] is not None or row["outcome_fields_analyzed"]):
            raise IngestError("OUTCOME_OR_BACKDATED_PUBLICATION_LEAK")
    rows.sort(key=lambda x: (x["created_on"], x["source_process_id"]))
    payload = ("\n".join(json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                        for x in rows) + "\n").encode("utf-8")
    report = {
        "schema": "pfl.parcan_pe2025_local_metadata.v1",
        "status": "INCREMENTAL_SOURCE_LOCAL_METADATA_ONLY",
        "source_sha256": SOURCE_SHA256,
        "source_metadata_receipt_sha256": METADATA_SHA256,
        "source_capture_receipt_sha256": CAPTURE_SHA256,
        "source_capture_utc": captured,
        "recorded_at": recorded,
        "rows": len(rows),
        "source_local_id_date_only": True,
        "outcome_values_analyzed": False,
        "historical_asof_admitted": False,
        "first_public_at_verified": 0,
        "population_complete": False,
        "denominator_verified": False,
        "distinct_keys_within_distribution": len(rows),
        "raw_csv_redistributed": False,
        "output_jsonl_sha256": sha256(payload).hexdigest(),
        "output_filename": "pe2025_source_local_metadata.jsonl",
        "ABH_cycles": 0,
        "note": "Additive to separate v1 1211 records; not a single certified census or complete time series.",
    }
    target.mkdir()
    (target / report["output_filename"]).write_bytes(payload)
    (target / "receipt.json").write_text(
        json.dumps(report, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    if checksum(target / report["output_filename"]) != report["output_jsonl_sha256"]:
        raise IngestError("POSTWRITE_METADATA_SHA_FAILURE")
    return {k: report[k] for k in (
        "status", "rows", "source_sha256", "output_jsonl_sha256", "population_complete",
        "first_public_at_verified", "ABH_cycles")}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--originals-dir", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    args = p.parse_args()
    print(json.dumps(build(originals_dir=args.originals_dir, output_dir=args.output_dir),
                     indent=2, ensure_ascii=False))
