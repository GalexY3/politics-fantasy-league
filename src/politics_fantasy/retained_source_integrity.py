"""Offline integrity attestations of seven already captured PFL artifacts.

This module opens local files ONLY as binary chunks for SHA-256; it does not
decode CSV/HTML/JSONL, expose original identifiers, access outcomes or HTTP,
or certify licensing, a registration census or first public availability.
The path allowlist is fixed in code and every source remains outside Git.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
import json
import os

from .procedural_index_contract import GateError, SHA, utc

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class FilePin:
    source_id: str
    external_path: str
    sha256: str
    nbytes: int
    role: str

    def __post_init__(self):
        if (not isinstance(self.source_id, str) or not self.source_id.isascii()
                or not self.source_id.replace("_","").isalnum()
                or not isinstance(self.external_path, str)
                or not self.external_path.startswith("../PFL-")
                or "\\" in self.external_path
                or ".." in self.external_path[3:].split("/")
                or not SHA.fullmatch(self.sha256)
                or type(self.nbytes) is not int or not 0 < self.nbytes <= 5_000_000
                or self.role not in {"OFFICIAL_CAPTURE_ORIGINAL", "PRIVATE_DERIVED_METADATA"}):
            raise GateError("INVALID_RETAINED_FILE_PIN")


PINS = (
    FilePin("PARCAN_X_PPL_2023", "../PFL-scratch-congreso2-20261031/runs/2026-10-31/parcan_2023_X_PPL_original.csv",
            "c426afb56f8b5c51f84afeeadb281a340cf46ccc268f218b2d5841961bd9b095", 285, "OFFICIAL_CAPTURE_ORIGINAL"),
    FilePin("PARCAN_XI_PE_2024", "../PFL-scratch-congreso2-20261031/runs/2026-10-31/parcan_2024_XI_PE_original.csv",
            "9ee6895522725f29cdf977ac0dd6da0490ad27c4128dea5fc2d0d7f48bf0e19c", 203545, "OFFICIAL_CAPTURE_ORIGINAL"),
    FilePin("PARCAN_XI_PE_2025", "../PFL-raw-primary/parcan_PE2025_20261031/parcan_2025_XI_PE_original.csv",
            "13350568f6ef8f311b7bd8cb41791da1028550c98f3ef73bcc8bb4a78a7809ba", 165663, "OFFICIAL_CAPTURE_ORIGINAL"),
    FilePin("PARCAN_XI_PE_2026", "../PFL-scratch-congreso2-20261031/runs/2026-10-31/parcan_2026_XI_PE_original.csv",
            "fe51a78cc89a9549b9e0232c27b638b6fd4fa0c1aefec2ce89ddb7455312dad2", 169570, "OFFICIAL_CAPTURE_ORIGINAL"),
    FilePin("SIAP_PROPOSICIONS_PAGE1", "../PFL-scratch-congreso2-20261031/ronda5/runs/siap_proposicions_page1_original.html",
            "3846b9fec8f20b426bfa1c231b717e0c20664d08aaf8586e49171339d927fc8d", 21934, "OFFICIAL_CAPTURE_ORIGINAL"),
    FilePin("PARCAN_SOURCE_METADATA_1211", "../PFL-local-processes-20261031-r1/process_source_metadata.jsonl",
            "7ed31c97be3928e306749972f5b3d746ca0c20a961818674ff0626e9c6679463", 638200, "PRIVATE_DERIVED_METADATA"),
    FilePin("PARCAN_PE2025_METADATA_543", "../PFL-local-processes-pe2025-20261031-r1/pe2025_source_local_metadata.jsonl",
            "88041ac88a6dcb6e8b5c20ca89ae07fcdb6f95548a209042b4d6dd06aaec2bcc", 312768, "PRIVATE_DERIVED_METADATA"),
)


def _check_pin_bytes(root: Path, pin: FilePin) -> None:
    """Do not decode source bytes; refuse a link or reparse of personal data."""
    if not isinstance(pin, FilePin):
        raise GateError("SOURCE_NOT_IN_PIN_ALLOWLIST")
    target = root / pin.external_path
    if not target.is_file() or target.is_symlink():
        raise GateError("RETAINED_SOURCE_MISSING_OR_LINK")
    # Refuse symlinked ancestors as well as the leaf. A known path must not be
    # redirected to a new private document or file outside its approved slot.
    parent = target.parent
    while parent != root.parent and parent != parent.parent:
        if parent.is_symlink():
            raise GateError("RETAINED_SOURCE_PARENT_IS_LINK")
        parent = parent.parent
    before = target.stat()
    if before.st_size != pin.nbytes:
        raise GateError("RETAINED_SOURCE_SIZE_DRIFT")
    dig = sha256()
    with target.open("rb") as f:
        while part := f.read(64 * 1024):
            dig.update(part)
    after = target.stat()
    if (after.st_size != before.st_size or after.st_mtime_ns != before.st_mtime_ns
            or after.st_ctime_ns != before.st_ctime_ns):
        raise GateError("RETAINED_SOURCE_CHANGED_DURING_AUDIT")
    if dig.hexdigest() != pin.sha256:
        raise GateError("RETAINED_SOURCE_SHA256_MISMATCH")


def audited_receipt(*, root: Path = ROOT, pins: tuple[FilePin, ...] = PINS,
                    at: datetime | None = None) -> dict:
    """Only a fully passing all-or-nothing audit returns a receipt."""
    if not isinstance(root, Path) or not isinstance(pins, tuple) or len(pins) > 7:
        raise GateError("INVALID_SOURCE_AUDIT_SCOPE")
    if (len({x.source_id for x in pins}) != len(pins)
            or len({x.external_path for x in pins}) != len(pins)):
        raise GateError("REPLAYED_RETAINED_SOURCE_PIN")
    for pin in pins:
        _check_pin_bytes(root, pin)
    # The audit clock is read ONLY AFTER the final file was verified. Never
    # publish a safe-by that precedes the end of the integrity check.
    completed = at if at is not None else datetime.now(timezone.utc)
    if completed.tzinfo is None or completed.utcoffset() is None:
        raise GateError("AUDIT_TIME_NEEDS_TZ")
    completed = completed.astimezone(timezone.utc)
    # The instant is a *local SHA audit*, NOT an historical publisher stamp.
    audit_second = completed.replace(microsecond=0)
    safe_by = audit_second + timedelta(seconds=1)
    return {
        "schema": "pfl.retained_source_integrity_receipt.v1",
        "verified_by": "BINARY_SHA256_AND_BYTE_LENGTH_ONLY",
        "audit_completed_second_utc": audit_second.isoformat(),
        "local_audit_safe_by": safe_by.isoformat(),
        "all_pinned_files_byte_verified": True,
        "source_total_files": len(pins),
        "official_original_files": sum(p.role == "OFFICIAL_CAPTURE_ORIGINAL" for p in pins),
        "private_derivatives_files": sum(p.role == "PRIVATE_DERIVED_METADATA" for p in pins),
        "official_original_bytes": sum(p.nbytes for p in pins if p.role == "OFFICIAL_CAPTURE_ORIGINAL"),
        "private_derived_bytes": sum(p.nbytes for p in pins if p.role == "PRIVATE_DERIVED_METADATA"),
        "records_decoded_or_case_ids_exposed": 0,
        "source_content_examined_for_outcomes": False,
        "first_public_at": None,
        "institutional_all_received_denominator": None,
        "permission_for_additional_processing_adjudicated_here": False,
        "historical_public_vintage_verified": False,
        "source_originals_published_in_git": False,
        "scientific_cycles": 0,
        "sources": [{
            "source_id": p.source_id, "role": p.role, "sha256": p.sha256,
            "bytes": p.nbytes,
            "matching_original_on_this_local_PC": True,
        } for p in pins],
    }


def write_receipt(*, path: Path, root: Path = ROOT,
                  pins: tuple[FilePin, ...] = PINS) -> dict:
    """Write only nonsensitive SHA metadata, atomically, to a tracked manifest slot."""
    expected = ROOT / "data/source_manifests/r9_retained_sources_integrity_20261031.json"
    if path != expected or root != ROOT or pins != PINS:
        raise GateError("RECEIPT_OUTPUT_OR_PINS_NOT_ALLOWLISTED")
    data = audited_receipt(root=root, pins=pins)
    blob = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf8")
    temp = path.with_suffix(".json.partial")
    if path.exists() or temp.exists() or path.is_symlink() or temp.is_symlink():
        raise GateError("RECEIPT_OUTPUT_EXISTS")
    # The destination contains no raw bytes, private paths, or source rows.
    with temp.open("xb") as f:
        f.write(blob)
    os.replace(temp, path)
    return data
