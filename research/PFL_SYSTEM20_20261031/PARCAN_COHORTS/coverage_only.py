"""Conservative offline structural coverage of PDDL Canary initiative CSVs.

The CSV parser decodes all cells for structure, including outcome-typed
columns; code inspects/aggregates only index positions 0, 1 and 3 (initiative
ID, legislature and creation date), never outcome contents. This limitation
is declared explicitly to avoid false claims of blind raw-data processing.
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
EXPECTED_HEADERS = (
    "ID_INICIATIVA", "LEGISLATURA", "EXTRACTO", "F_CREACION",
    "SITUACION", "PROCEDIMIENTO", "TIPO_FINALIZACION", "TIPO_DESCRIPCION"
)
MAX_BYTES = 4_000_000
MAX_ROWS = 50_000
MAX_FIELD_LENGTH = 40_000
FILES = (
    ("canonical_receipt.json", "RAW_CAPTURED_WITHOUT_POPULATION_CERTIFICATION",
     "parcan_2023_X_PPL_original.csv", "scope"),
    ("pe_2024_receipt.json", "RAW_CAPTURED_POPULATION_NOT_CERTIFIED",
     "parcan_2024_XI_PE_original.csv", "source_scope"),
    ("pe_2026_receipt.json", "RAW_CAPTURED_POPULATION_NOT_CERTIFIED",
     "parcan_2026_XI_PE_original.csv", "source_scope"),
)


def sha256(raw: bytes):
    return hashlib.sha256(raw).hexdigest()


def now_utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save_new(path: Path, value: object):
    with path.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(value, file, ensure_ascii=False, sort_keys=True, indent=2)
        file.write("\n")


def date_format(text: str):
    text = text.strip()
    if not text:
        return "missing"
    formats = (
        (r"\d{2}/\d{2}/\d{4}", "dd/mm/yyyy"),
        (r"\d{4}-\d{2}-\d{2}", "yyyy-mm-dd"),
        (r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", "dd/mm/yyyy_hh_mm"),
        (r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})?", "iso8601"),
    )
    for regex, label in formats:
        if re.fullmatch(regex, text):
            return label
    return "unrecognized"


def audit_bytes(raw: bytes, *, scope: dict) -> dict:
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_BYTES:
        raise ValueError("BAD_SIZE_OR_TYPE")
    if not isinstance(scope, dict):
        raise ValueError("BAD_SCOPE")
    try:
        text = raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as error:
        raise ValueError("NON_UTF8_CSV") from error
    if "\x00" in text:
        raise ValueError("EMBEDDED_NUL")
    reader = csv.reader(StringIO(text, newline=""), strict=True)
    header = next(reader, None)
    if header != list(EXPECTED_HEADERS):
        raise ValueError("UNVERIFIED_CSV_HEADERS")
    seen: dict[tuple[str, str], tuple[str, str, str]] = {}
    repeated_key = 0
    conflicting_key = 0
    no_key = 0
    null_id = 0
    null_legs = 0
    null_date = 0
    by_date_shape = Counter()
    leg_distinct = set()
    count = 0
    for row in reader:
        count += 1
        if count > MAX_ROWS:
            raise ValueError("TOO_MANY_ROWS")
        if len(row) != len(EXPECTED_HEADERS) or any(len(x) > MAX_FIELD_LENGTH for x in row):
            raise ValueError("BAD_ROW_SHAPE_OR_OVERSIZE_FIELD")
        # CSV parsing instantiated all cells, but program logic never
        # inspects, aggregates or exports row[2] or row[4:].
        ident, leg, created = row[0].strip(), row[1].strip(), row[3].strip()
        if not ident:
            null_id += 1
        if not leg:
            null_legs += 1
        else:
            leg_distinct.add(leg)
        if not created:
            null_date += 1
        by_date_shape[date_format(created)] += 1
        if not ident or not leg:
            no_key += 1
            continue
        key = (ident, leg)
        selected = (ident, leg, created)
        if key in seen:
            if seen[key] == selected:
                repeated_key += 1
            else:
                conflicting_key += 1
        else:
            seen[key] = selected
    return {
        "stratum": scope,
        "records_read": count,
        "distinct_nonmissing_id_legislature_keys": len(seen),
        "same_key_same_metadata_rows": repeated_key,
        "same_key_conflicting_creation_date_rows": conflicting_key,
        "missing_primary_key_rows": no_key,
        "missing_id": null_id,
        "missing_legislature": null_legs,
        "missing_creation_date": null_date,
        "date_string_shape_counts": dict(sorted(by_date_shape.items())),
        "distinct_legislature_labels": len(leg_distinct),
        "full_csv_rows_parsed_for_structure": True,
        "outcome_values_not_inspected_or_aggregated": True,
        "outcome_columns_declared_not_interpreted": ["SITUACION", "TIPO_FINALIZACION"],
        "first_public_at": None,
        "event_creation_does_not_attest_publication": True,
        "observed_current_status_is_not_historical_as_of": True,
        "publisher_expected_row_total": None,
        "pagination_completeness_verified": False,
        "complete_parliamentary_population": False,
        "complete_congress_population": False,
        "data_rows_redistributed_or_printed": False,
        "ABH_cycles": 0,
    }


def main():
    target = RUN / "metadata_only_coverage.json"
    if target.exists():
        raise ValueError("COVERAGE_ALREADY_WRITTEN")
    frozen_path = RUN / "frozen_code.json"
    if not frozen_path.exists():
        raise ValueError("CODE_TEST_FREEZE_REQUIRED")
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    if frozen.get("tests_passed") is not True:
        raise ValueError("TESTS_NOT_PASSED")
    for filename, expected_sha in frozen["code_sha256"].items():
        if sha256((ROOT / filename).read_bytes()) != expected_sha:
            raise ValueError("CODE_CHANGED_SINCE_TEST_FREEZE")
    all_reports = []
    for receipt_name, accepted_state, filename, scope_field in FILES:
        receipt_raw = (RUN / receipt_name).read_bytes()
        receipt = json.loads(receipt_raw)
        if receipt.get("state", receipt.get("status")) != accepted_state:
            raise ValueError("SOURCE_NOT_VALIDLY_CAPTURED")
        if receipt.get("raw_file") != filename:
            raise ValueError("SOURCE_FILE_MISMATCH")
        raw = (RUN / filename).read_bytes()
        if sha256(raw) != receipt["raw_sha256"] or len(raw) != receipt["raw_bytes"]:
            raise ValueError("SOURCE_RAW_BYTES_CHANGED")
        scope = receipt[scope_field]
        summary = audit_bytes(raw, scope=scope)
        summary.update({
            "publisher": "Parlamento de Canarias",
            "rights": "specific dataset Open Data Commons PDDL",
            "original_sha256": receipt["raw_sha256"],
            "original_bytes": len(raw),
            "capture_receipt_sha256": sha256(receipt_raw),
            "http_date": receipt.get("http_date"),
            "response_status": receipt["http_status"],
            "http_last_modified_not_first_publication": True,
            "raw_url": receipt.get("request_url", receipt.get("url")),
        })
        all_reports.append(summary)
    result = {
        "kind": "PHASE1_METADATA_ONLY_AFTER_CAPTURE",
        "audited_utc": now_utc(),
        "raw_source_downloads_here": 0,
        "code_freeze_sha256": sha256(frozen_path.read_bytes()),
        "source_cohorts": all_reports,
        "institution": "Parlamento de Canarias",
        "not_a_full_parliament_universe": True,
        "not_span_same_initiative_type_for_longitudinal_comparison": True,
        "first_public_at_historically_verified": 0,
        "outcomes_analyzed": False,
        "outcome_typed_cells_decoded_by_csv_parser": True,
        "raw_person_fields_exported": False,
    }
    save_new(target, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if sys.argv[1:] != ["audit"]:
        print("Usage: python coverage_only.py audit (offline, one-time)", file=sys.stderr)
        sys.exit(2)
    main()
