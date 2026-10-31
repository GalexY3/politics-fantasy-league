"""Offline diagnostic ingestion of one official Canary Islands CSV distribution.

All outputs are aggregate and strictly bounded. Neither a creation date nor
current status is treated as historically knowable at an earlier forecast cut.
"""

from __future__ import annotations

from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
from io import StringIO
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "runs" / "2026-10-31"
EXPECTED = (
    "ID_INICIATIVA", "LEGISLATURA", "EXTRACTO", "F_CREACION",
    "SITUACION", "PROCEDIMIENTO", "TIPO_FINALIZACION", "TIPO_DESCRIPCION"
)
MAX_BYTES = 2_000_000
MAX_RECORDS = 30_000
CELL_CHARS = 30_000
SAFE_COUNT_THRESHOLD = 5


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def hash_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def dump_once(path, payload):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=False)
        stream.write("\n")


def decode_csv(raw: bytes) -> list[dict[str, str]]:
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES or not raw:
        raise ValueError("CSV_MISSING_OR_OVERSIZE")
    try:
        text = raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("UTF8_REQUIRED_NO_SILENT_REPAIR") from exc
    if "\x00" in text:
        raise ValueError("NULL_BYTE")
    reader = csv.DictReader(StringIO(text, newline=""), strict=True)
    header = reader.fieldnames
    if header is None or len(header) != len(set(header)) or tuple(header) != EXPECTED:
        raise ValueError("UNRECOGNIZED_OR_DUPLICATE_HEADERS")
    rows = []
    for row in reader:
        if len(rows) >= MAX_RECORDS:
            raise ValueError("UNBOUNDED_ROW_COUNT")
        if None in row or any(value is None or len(value) > CELL_CHARS for value in row.values()):
            raise ValueError("MALFORMED_ROW_OR_CELL")
        # Prevent surprising, invisible control chars in identifiers.
        if not row["ID_INICIATIVA"].strip() or any(ord(c) < 32 for c in row["ID_INICIATIVA"]):
            raise ValueError("BAD_IDENTIFIER")
        rows.append(row)
    return rows


def redact_counts(counts: Counter) -> dict:
    """Do not expose a unique rare label via aggregates with tiny cell size."""
    return {
        "distinct_labels": len(counts),
        "observed_nonmissing": sum(counts.values()),
        "categories_at_least_5_rows": {key: count for key, count in sorted(counts.items()) if count >= SAFE_COUNT_THRESHOLD},
        "suppressed_categories": sum(1 for count in counts.values() if count < SAFE_COUNT_THRESHOLD),
        "suppressed_rows": sum(count for count in counts.values() if count < SAFE_COUNT_THRESHOLD),
    }


def date_structure(value: str) -> str:
    text = value.strip()
    if not text:
        return "missing"
    for pattern, kind in (
        (r"\d{2}/\d{2}/\d{4}", "dd/mm/yyyy"),
        (r"\d{4}-\d{2}-\d{2}", "yyyy-mm-dd"),
        (r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", "dd/mm/yyyy_hh:mm"),
        (r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*", "iso_datetime"),
    ):
        if re.fullmatch(pattern, text):
            return kind
    return "unknown_format"


def audit(raw: bytes, *, scope: dict) -> dict:
    rows = decode_csv(raw)
    legislature = scope.get("legislature")
    year = scope.get("year")
    kind = scope.get("initiative_type_code")
    if type(legislature) is not int or type(year) is not int or not isinstance(kind, str):
        raise ValueError("UNCLEAR_SOURCE_SCOPE")
    ids = {}
    identical_replays = 0
    conflicts = 0
    empty = Counter()
    time_formats = Counter()
    states = Counter()
    finals = Counter()
    status_present = 0
    final_present = 0
    for row in rows:
        key = (legislature, year, kind, row["ID_INICIATIVA"].strip())
        if key in ids:
            if ids[key] == row:
                identical_replays += 1
            else:
                conflicts += 1
        else:
            ids[key] = row
        for column in EXPECTED:
            if not row[column].strip():
                empty[column] += 1
        time_formats[date_structure(row["F_CREACION"])] += 1
        state = row["SITUACION"].strip()
        final = row["TIPO_FINALIZACION"].strip()
        if state:
            states[state] += 1
            status_present += 1
        if final:
            finals[final] += 1
            final_present += 1
    # No titles or individual identifiers leave this function.
    return {
        "scope": scope, "unit": "one CSV record in a licensed institutional year-legislature-type distribution",
        "raw_rows": len(rows), "distinct_keys": len(ids),
        "identical_replays": identical_replays,
        "conflicting_duplicate_keys": conflicts,
        "null_counts_by_column": dict(sorted(empty.items())),
        "creation_date_formats": dict(sorted(time_formats.items())),
        "state_field": redact_counts(states),
        "finalization_field": redact_counts(finals),
        "source_first_public_at": None,
        "event_created_at_is_publication_timestamp": False,
        "current_outcome_fields_usable_historically_as_of": False,
        "outcome_labels_are_final_scientific_targets": False,
        "longitudinal_completeness_verified": False,
        "parliament_wide_population_complete": False,
        "pagination": "single official per-type/year distribution; no certified publisher total or continuation metadata",
        "all_source_rows_private_to_local_scratch": True,
        "causal_or_ABH_conclusions": False,
    }


def report():
    receipt_file = RUN / "canonical_receipt.json"
    receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    if receipt.get("status") != "RAW_CAPTURED_WITHOUT_POPULATION_CERTIFICATION":
        raise ValueError("NO_VERIFIED_CAPTURE_RECEIPT")
    path = RUN / receipt["raw_file"]
    raw = path.read_bytes()
    if hash_bytes(raw) != receipt["raw_sha256"] or len(raw) != receipt["raw_bytes"]:
        raise ValueError("ORIGINAL_CAPTURE_HASH_MISMATCH")
    frozen = RUN / "freeze.json"
    if not frozen.exists():
        raise ValueError("TESTED_CODE_FREEZE_REQUIRED")
    hashes = json.loads(frozen.read_text(encoding="utf-8"))["code_sha256"]
    current = {name: hash_bytes((ROOT / name).read_bytes()) for name in ("ingest_offline.py", "test_ingest_offline.py")}
    if hashes != current:
        raise ValueError("CODE_CHANGED_SINCE_FREEZE")
    summary = audit(raw, scope=receipt["scope"])
    summary["source_uri"] = receipt["effective_url"]
    summary["capture_receipt_sha256"] = hash_bytes(receipt_file.read_bytes())
    summary["original_sha256"] = receipt["raw_sha256"]
    summary["original_bytes"] = receipt["raw_bytes"]
    summary["audit_utc"] = now()
    summary["legal_basis_dataset_license"] = receipt["licence"]
    summary["direct_http_status"] = receipt["http_status"]
    summary["http_date"] = receipt["http_date"]
    dump_once(RUN / "coverage.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if sys.argv[1:] != ["report"]:
        print("Usage: python ingest_offline.py report", file=sys.stderr)
        sys.exit(2)
    report()
