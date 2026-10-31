"""Normalize source-scoped Canary parliamentary-process *metadata* from local raws.

The script never downloads data and never reads EXTRACTO, SITUACION,
PROCEDIMIENTO, TIPO_FINALIZACION or TIPO_DESCRIPCION as substantive fields.
CSV parsing necessarily decodes cells structurally. Originals and the
resulting non-person ID/date JSONL stay OUTSIDE Git.

The resulting rows are not source-certified process-state trajectories:
F_CREACION is not first_public_at, and no full initiative universe or complete
multi-year population is attested. This is an engineering/observability stage.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, datetime, timezone
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RECEIPTS = REPO / "research/PFL_SYSTEM20_20261031/PARCAN_COHORTS/receipts"
EXPECTED_HEADERS = (
    "ID_INICIATIVA", "LEGISLATURA", "EXTRACTO", "F_CREACION",
    "SITUACION", "PROCEDIMIENTO", "TIPO_FINALIZACION", "TIPO_DESCRIPCION")
SOURCES = (
    ("parcan_2023_X_PPL_original.csv", "canonical_receipt.json", "PPL", 10, 2023, 1),
    ("parcan_2024_XI_PE_original.csv", "pe_2024_receipt.json", "PE", 11, 2024, 686),
    ("parcan_2026_XI_PE_original.csv", "pe_2026_receipt.json", "PE", 11, 2026, 524),
)
MAX_SOURCE_BYTES = 3_000_000
MAX_ROWS = 100_000


class IngestError(ValueError):
    pass


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _unique_pairs(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise IngestError("DUPLICATE_JSON_KEY")
        d[k] = v
    return d


def strict_json(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size > 25_000:
        raise IngestError("MISSING_OR_OVERSIZE_RECEIPT")
    obj = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs,
                     parse_constant=lambda x: (_ for _ in ()).throw(IngestError("NONFINITE")))
    if not isinstance(obj, dict):
        raise IngestError("BAD_RECEIPT")
    return obj


def parse_metadata(raw: bytes, *, legislature: int, kind: str, year: int,
                   source_sha: str, captured_utc: str) -> tuple[list[dict], dict]:
    """Decode all cells structurally but select only ID, legislature, creation date."""
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_SOURCE_BYTES:
        raise IngestError("SOURCE_SIZE_INVALID")
    if digest(raw) != source_sha:
        raise IngestError("SOURCE_SHA256_MISMATCH")
    try:
        reader = csv.reader(StringIO(raw.decode("utf-8-sig", errors="strict"), newline=""),
                            strict=True)
        if next(reader, None) != list(EXPECTED_HEADERS):
            raise IngestError("UNKNOWN_SCHEMA")
        records = []
        keyset = set()
        mismatch_year = 0
        for row in reader:
            if len(records) >= MAX_ROWS or len(row) != len(EXPECTED_HEADERS) or any(len(c) > 50000 for c in row):
                raise IngestError("BOUNDED_ROW_SHAPE_VIOLATION")
            # Neither personal/extract nor status/finalization values enter the result.
            ident, leg, created = row[0].strip(), row[1].strip(), row[3].strip()
            if not ident or len(ident) > 160 or any(ord(c) < 32 for c in ident):
                raise IngestError("BAD_INITIATIVE_ID")
            if leg != str(legislature):
                raise IngestError("WRONG_LEGISLATURE")
            try:
                datevalue = date.fromisoformat(created)
            except ValueError as exc:
                raise IngestError("BAD_CREATION_DATE") from exc
            if datevalue.isoformat() != created:
                raise IngestError("NONCANONICAL_CREATION_DATE")
            if datevalue > datetime.fromisoformat(captured_utc.replace("Z","+00:00")).date():
                raise IngestError("CREATED_AFTER_SOURCE_CAPTURE")
            if datevalue.year != year:
                mismatch_year += 1
            key = (legislature, kind, ident)
            if key in keyset:
                raise IngestError("DUPLICATED_SOURCE_PROCESS_ID")
            keyset.add(key)
            records.append({
                "schema": "pfl.parcan_source_local_process_metadata.v1",
                "authority": "PARLAMENTO_CANARIAS",
                "source_scope": f"PARCAN:LEG{legislature}:{kind}:YEAR{year}",
                "legislature": legislature, "process_family": kind,
                "source_process_id": ident, "created_on": created,
                "source_sha256": source_sha,
                "first_public_at": None, "terminal_state": None,
                "transition_events": None, "outcome_fields_analyzed": False,
                "historical_asof_admitted": False,
                "scope_population_certified": False,
            })
        return records, {"rows":len(records), "year_mismatch_rows":mismatch_year,
                         "duplicate_keys_within_distribution":0}
    except (UnicodeError, csv.Error) as exc:
        raise IngestError("MALFORMED_SOURCE_CSV") from exc


def build(*, originals: Path, output: Path) -> dict:
    """Single offline run; immutable original receipts, no overwrite and no network."""
    original_dir = originals.resolve(strict=True)
    destination = output.resolve(strict=False)
    if destination == REPO or REPO in destination.parents:
        raise IngestError("DO_NOT_STORE_SOURCE_ROWS_IN_GIT")
    if destination.exists():
        raise IngestError("REFUSE_OVERWRITE")
    all_rows = []
    coverage = []
    keys_across_files = {}
    for filename, receipt_name, kind, legislature, year, n_expected in SOURCES:
        r = strict_json(RECEIPTS / receipt_name)
        if (r.get("raw_file") != filename or r.get("http_status") != 200 or
                type(r.get("raw_bytes")) is not int or not 0 < r["raw_bytes"] <= MAX_SOURCE_BYTES or
                not isinstance(r.get("raw_sha256"), str) or len(r["raw_sha256"]) != 64 or
                r.get("first_public_at") is not None or
                r.get("source_first_public_at") is not None or
                r.get("status", r.get("state")) not in {
                    "RAW_CAPTURED_WITHOUT_POPULATION_CERTIFICATION",
                    "RAW_CAPTURED_POPULATION_NOT_CERTIFIED",
                }):
            raise IngestError("SOURCE_HAS_DIFFERENT_PROVENANCE")
        path = original_dir / filename
        if path.is_symlink() or not path.is_file():
            raise IngestError("SOURCE_MISSING_OR_SYMLINK")
        raw = path.read_bytes()
        if len(raw) != r["raw_bytes"] or digest(raw) != r["raw_sha256"]:
            raise IngestError("ORIGINAL_NOT_EQUAL_TO_CAPTURE_RECEIPT")
        captured = r.get("capture_finished_utc", r.get("finished_utc"))
        if not isinstance(captured, str) or "T" not in captured:
            raise IngestError("MISSING_LOCAL_CAPTURE_DATE")
        rows, info = parse_metadata(raw, legislature=legislature, kind=kind, year=year,
                                    source_sha=r["raw_sha256"], captured_utc=captured)
        if len(rows) != n_expected:
            raise IngestError("SOURCE_ROW_COUNT_DIFFERS_FROM_PRIOR_AUDIT")
        coverage.append({
            "distribution": f"PARCAN:LEG{legislature}:{kind}:YEAR{year}",
            "filename": filename, "source_sha256":r["raw_sha256"],
            "source_capture_utc":captured, "rows":info["rows"],
            "year_mismatch_rows":info["year_mismatch_rows"],
            "population_certified":False,
            "first_public_at_verified":False,
        })
        for record in rows:
            idkey = (legislature, kind, record["source_process_id"])
            if idkey in keys_across_files:
                raise IngestError("CROSS_YEAR_DUPLICATE_PROCESS_NEEDS_ADJUDICATION")
            keys_across_files[idkey] = True
        all_rows.extend(rows)
    all_rows.sort(key=lambda r:(r["legislature"],r["process_family"],r["created_on"],r["source_process_id"]))
    recorded = datetime.now(timezone.utc).isoformat(timespec="seconds")
    # *recorded_at* is new local normalization time, not a backdated source timestamp.
    for record in all_rows:
        record["recorded_at"] = recorded
    lines = (json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
             for x in all_rows)
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    report = {
        "schema": "pfl.parcan_local_ingest_receipt.v1",
        "stage": "METADATA_ONLY_NOT_SOURCE_VINTAGE_ADMITTED",
        "recorded_at": recorded,
        "local_records_normalized": len(all_rows),
        "eligible_population_certified": False,
        "full_canary_or_congress_coverage": False,
        "first_public_at_verified": 0,
        "states_or_outcomes_read_for_analysis": False,
        "source_publisher": "Parlamento de Canarias",
        "license_documented": "Open Data Commons PDDL; legal use-specific review still required",
        "source_receipts": coverage,
        "local_jsonl_sha256": digest(payload),
        "normalized_file": "process_source_metadata.jsonl",
        "private_originals_copied_to_git": False,
        "ABH_cycles": 0,
        "limitations": "No historical state transitions, publisher denominators, or exact first publication; year 2025 not covered.",
    }
    destination.mkdir(parents=True, exist_ok=False)
    (destination / report["normalized_file"]).write_bytes(payload)
    (destination / "ingest_receipt.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    if digest((destination / report["normalized_file"]).read_bytes()) != report["local_jsonl_sha256"]:
        raise IngestError("POST_WRITE_HASH_MISMATCH")
    # Do not display IDs, titles, question statuses or person information.
    return {k:report[k] for k in (
        "stage","recorded_at","local_records_normalized","first_public_at_verified",
        "eligible_population_certified","local_jsonl_sha256","ABH_cycles")}


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--originals-dir",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(build(originals=args.originals_dir, output=args.output_dir),
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
