"""Offline, standard-library prototype for Congress *initiative population* indexes.

There is deliberately no HTTP client. The Congress CSV/API schema and ability to
enumerate all initiatives have not been validated. Fixture JSON and CSV are a
proposed intermediate contract, not a representation of a downloaded export.
"""

from __future__ import annotations

import csv
from datetime import date, datetime, timezone
import hashlib
from io import StringIO
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
RUN_DIR = ROOT / "runs" / "2026-10-31"
SOURCE_INDEX = "https://www.congreso.es/es/busqueda-de-iniciativas"
SOURCE_OPEN_DATA = "https://www.congreso.es/es/datos-abiertos"
SOURCE_TERMS = "https://www.congreso.es/es/cem/aviso-legal"
DOC_HOST = "www.congreso.es"
EXPEDIENTE = re.compile(r"(?P<type>\d{3})/(?P<num>\d{6})(?:/\d{4})?\Z")
ROMAN = re.compile(r"(?:XV|XIV|XIII|XII|XI|X|IX|VIII|VII|VI|V|IV|III|II|I|CONSTITUYENTE)\Z")
ROW_FIELDS = frozenset({"legislature", "expediente", "presented_on", "qualified_on", "first_bocg_day", "first_bocg_url"})
PAGE_FIELDS = frozenset({"schema", "legislature", "type_code", "page", "next_page", "reported_total", "records"})
FORBIDDEN_FIELD_FRAGMENTS = ("resultado", "result", "outcome", "success", "aprob", "approved", "passed", "rejected", "rejection", "vot", "adjudic", "status", "stage", "closure", "conclu", "decision", "future", "final")
SCHEMA = "PFL_CONGRESO_INDEX_SYNTHETIC_V1"
AS_OF_DATE = date(2026, 10, 31)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_new_json(path: Path, data: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, sort_keys=True, indent=2, ensure_ascii=False)
        handle.write("\n")


def parse_date(value: object, field: str, *, nullable: bool = False) -> date | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"INVALID_{field.upper()}")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"INVALID_{field.upper()}") from error


def good_official_document_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        link = urlsplit(value)
        return (
            link.scheme == "https"
            and link.hostname == DOC_HOST
            and link.port in (None, 443)
            and link.username is None
            and link.password is None
            and bool(link.path.startswith("/public_oficiales/"))
            and not link.fragment
        )
    except ValueError:
        return False


def assert_no_outcomes(fields: object) -> None:
    if not isinstance(fields, dict):
        raise ValueError("ROW_NOT_OBJECT")
    for field in fields:
        if any(fragment in field.lower() for fragment in FORBIDDEN_FIELD_FRAGMENTS):
            raise ValueError(f"FORBIDDEN_OUTCOME_OR_FUTURE_FIELD:{field}")


def normalize_record(raw: object, *, legislature: str, type_code: str, cutoff: date) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("ROW_NOT_OBJECT")
    assert_no_outcomes(raw)
    if set(raw) != ROW_FIELDS:
        raise ValueError("ROW_SCHEMA_MISMATCH")
    if raw["legislature"] != legislature:
        raise ValueError("ROW_WRONG_LEGISLATURE")
    expediente = raw["expediente"]
    found = EXPEDIENTE.fullmatch(expediente) if isinstance(expediente, str) else None
    if found is None or found.group("type") != type_code:
        raise ValueError("ROW_INVALID_EXPEDIENTE_OR_TYPE")
    presented = parse_date(raw["presented_on"], "presented_on")
    qualified = parse_date(raw["qualified_on"], "qualified_on", nullable=True)
    publication = parse_date(raw["first_bocg_day"], "first_bocg_day", nullable=True)
    evidence = raw["first_bocg_url"]
    if publication is None and evidence is not None:
        raise ValueError("BOCG_URL_WITHOUT_DAY")
    if publication is not None and not good_official_document_url(evidence):
        raise ValueError("BOCG_DAY_WITHOUT_OFFICIAL_LINK")
    if qualified is not None and qualified < presented:
        raise ValueError("QUALIFICATION_BEFORE_PRESENTATION")
    if publication is not None and publication < presented:
        raise ValueError("BOCG_BEFORE_PRESENTATION_REQUIRES_INVESTIGATION")
    if presented > cutoff:
        raise ValueError("FUTURE_INITIATIVE_IN_SNAPSHOT")
    if publication is None:
        public_at_cutoff = "UNKNOWN_FIRST_PUBLIC_DAY"
    elif publication < cutoff:
        public_at_cutoff = "DATED_BOCG_REFERENCE_BEFORE_CUTOFF_UNATTESTED"
    elif publication == cutoff:
        public_at_cutoff = "SAME_DAY_TIME_UNKNOWN"
    else:
        public_at_cutoff = "NOT_PUBLIC_BY_CUTOFF"
    return {
        "key": f"{legislature}:{expediente}",
        "legislature": legislature,
        "type_code": type_code,
        "expediente": expediente,
        "presented_on": str(presented),
        "qualified_on": str(qualified) if qualified is not None else None,
        "first_bocg_day_candidate": str(publication) if publication is not None else None,
        "first_bocg_reference_url_candidate": evidence,
        "first_public_at": None,
        "first_public_at_attested": False,
        "publication_gate": public_at_cutoff,
        "censor_at": str(cutoff),
        "censoring_kind": "RIGHT_CENSORED_AT_OBSERVATION_DATE_NO_TERMINAL_STATE_INGESTED",
        "source_authenticity_attested": False,
    }


def read_page(raw: bytes) -> dict:
    if len(raw) > 1_000_000:
        raise ValueError("PAGE_EXCEEDS_1MB")
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("BAD_JSON_OR_ENCODING") from error
    if not isinstance(doc, dict) or set(doc) != PAGE_FIELDS:
        raise ValueError("PAGE_SCHEMA_MISMATCH")
    if doc["schema"] != SCHEMA:
        raise ValueError("UNVERIFIED_FORMAT_NO_AUTOMATIC_SCHEMA_MAPPING")
    if not isinstance(doc["legislature"], str) or ROMAN.fullmatch(doc["legislature"]) is None:
        raise ValueError("UNKNOWN_LEGISLATURE")
    if not isinstance(doc["type_code"], str) or re.fullmatch(r"\d{3}", doc["type_code"]) is None:
        raise ValueError("INVALID_TYPE_CODE")
    if type(doc["page"]) is not int or doc["page"] < 1:
        raise ValueError("INVALID_PAGE")
    if doc["next_page"] is not None and (type(doc["next_page"]) is not int or doc["next_page"] <= doc["page"]):
        raise ValueError("INVALID_OR_CYCLIC_NEXT_PAGE")
    if doc["reported_total"] is not None and (type(doc["reported_total"]) is not int or doc["reported_total"] < 0):
        raise ValueError("INVALID_REPORTED_TOTAL")
    if not isinstance(doc["records"], list) or len(doc["records"]) > 500:
        raise ValueError("INVALID_PAGE_RECORDS")
    return doc


def parse_offline_csv(raw: bytes, *, legislature: str, type_code: str, page: int, next_page: int | None, reported_total: int | None) -> bytes:
    """Adapt known synthetic CSV columns; real CSV schema requires adjudication."""
    if len(raw) > 1_000_000:
        raise ValueError("CSV_EXCEEDS_1MB")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError as error:
        raise ValueError("BAD_CSV_ENCODING") from error
    reader = csv.DictReader(StringIO(text), strict=True)
    if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise ValueError("DUPLICATE_OR_MISSING_CSV_HEADERS")
    if set(reader.fieldnames) != ROW_FIELDS:
        raise ValueError("CSV_UNKNOWN_SCHEMA_OR_OUTCOME_FIELDS")
    rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError("CSV_EXTRA_VALUES")
    for row in rows:
        for name in ("qualified_on", "first_bocg_day", "first_bocg_url"):
            if row[name] == "":
                row[name] = None
    return json.dumps({
        "schema": SCHEMA, "legislature": legislature, "type_code": type_code,
        "page": page, "next_page": next_page, "reported_total": reported_total, "records": rows,
    }, ensure_ascii=False, sort_keys=True).encode("utf-8")


def ingest_paginated_pages(pages: dict[int, bytes], *, cutoff: date = AS_OF_DATE) -> dict:
    """Fail-closed ingest: no gaps, cursor loops, duplicate conflicts or outcomes."""
    if not pages or len(pages) > 50:
        raise ValueError("EMPTY_OR_UNBOUNDED_PAGES")
    decoded = {number: read_page(raw) for number, raw in pages.items()}
    first = decoded.get(1)
    if first is None:
        raise ValueError("MISSING_FIRST_PAGE")
    legislature, type_code, reported_total = first["legislature"], first["type_code"], first["reported_total"]
    rows_by_key: dict[str, dict] = {}
    visited: list[int] = []
    duplicate_replays = 0
    next_number: int | None = 1
    while next_number is not None:
        if next_number in visited:
            raise ValueError("PAGINATION_CYCLE")
        page = decoded.get(next_number)
        if page is None:
            raise ValueError("MISSING_PAGINATION_PAGE")
        if page["page"] != next_number or page["legislature"] != legislature or page["type_code"] != type_code:
            raise ValueError("PAGE_STRATUM_OR_NUMBER_CONFLICT")
        if page["reported_total"] != reported_total:
            raise ValueError("INCONSISTENT_REPORTED_TOTAL")
        visited.append(next_number)
        for item in page["records"]:
            normalized = normalize_record(item, legislature=legislature, type_code=type_code, cutoff=cutoff)
            key = normalized["key"]
            if key in rows_by_key:
                if rows_by_key[key] != normalized:
                    raise ValueError("CONFLICTING_DUPLICATE_RECORD")
                duplicate_replays += 1
            else:
                rows_by_key[key] = normalized
        next_number = page["next_page"]
    if set(decoded) != set(visited):
        raise ValueError("UNREFERENCED_PAGES")
    if reported_total is not None and reported_total != len(rows_by_key):
        raise ValueError("PAGINATED_INDEX_TOTAL_MISMATCH")
    return {
        "schema": SCHEMA,
        "mode": "SYNTHETIC_ONLY",
        "stratum": {"legislature": legislature, "type_code": type_code},
        "as_of_date": str(cutoff),
        "page_numbers": visited,
        "traversal_complete_for_supplied_fixture": True,
        "distinct_initiatives": len(rows_by_key),
        "duplicate_identical_rows": duplicate_replays,
        "index_claimed_total": reported_total,
        "source_population_complete": False,
        "real_source_first_public_at_verified": 0,
        "real_source_records": 0,
        "records": [rows_by_key[key] for key in sorted(rows_by_key)],
    }


def smoke() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    marker = RUN_DIR / "smoke_attempt.json"
    if marker.exists():
        print("BLOCKED: only one synthetic smoke is permitted; prior marker exists")
        return 2
    started = now_utc()
    write_new_json(marker, {"started_utc": started, "kind": "SYNTHETIC_ONLY", "http_get_attempts": 0})
    receipt: dict = {
        "started_utc": started, "finished_utc": None,
        "target_index": SOURCE_INDEX, "open_data_portal": SOURCE_OPEN_DATA,
        "legal_reference": SOURCE_TERMS,
        "http_get_attempts": 0, "http_status": None, "http_date": None,
        "real_source_bytes": 0, "real_source_records": 0,
        "source_capture_state": "BLOCKED_UNVERIFIED_EXPORT_AND_ACCESS_403",
        "rights_note": "General Congress reuse conditions identified; no consent click or real export download attempted",
        "terms_accepted": False, "github_or_git_writes": 0,
        "synthetic_state": "PENDING", "synthetic_hashes": [],
    }
    try:
        pages: dict[int, bytes] = {}
        original_dir = RUN_DIR / "synthetic_originals"
        original_dir.mkdir(exist_ok=False)
        for number in (1, 2):
            name = f"page_{number}.json"
            raw = (ROOT / "fixtures" / name).read_bytes()
            sha = hashlib.sha256(raw).hexdigest()
            with (original_dir / name).open("xb") as f:
                f.write(raw)
            replay = hashlib.sha256((original_dir / name).read_bytes()).hexdigest()
            if sha != replay:
                raise ValueError("SYNTHETIC_HASH_REPLAY_FAILED")
            receipt["synthetic_hashes"].append({"path": f"synthetic_originals/{name}", "sha256": sha, "bytes": len(raw), "hash_replay_ok": True})
            pages[number] = raw
        result = ingest_paginated_pages(pages)
        summary = {key: value for key, value in result.items() if key != "records"}
        write_new_json(RUN_DIR / "synthetic_index.json", result)
        write_new_json(RUN_DIR / "coverage.json", {
            **summary,
            "real_source_downloads": 0,
            "real_export_count_known": False,
            "real_index_count_verified": 0,
            "index_available_through_search_not_certified_complete": True,
            "publication_date_vs_first_public_instant": "DAY_ONLY_REFERENCE_AND_UNATTESTED",
            "legal_rights_adjudicated": False,
            "no_outcomes_ingested": True,
            "no_causal_conclusions": True,
        })
        receipt.update({"synthetic_state": "PASS", "synthetic_distinct_initiatives": summary["distinct_initiatives"], "synthetic_duplicate_replays": summary["duplicate_identical_rows"]})
    except (OSError, ValueError, TypeError) as error:
        receipt.update({"synthetic_state": "FAIL", "synthetic_error": f"{type(error).__name__}: {error}"})
    finally:
        receipt["finished_utc"] = now_utc()
        write_new_json(RUN_DIR / "receipt.json", receipt)
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["synthetic_state"] == "PASS" else 1


if __name__ == "__main__":
    if sys.argv[1:] != ["smoke"]:
        print("Usage: python congreso_adapter.py smoke (synthetic only, no network)", file=sys.stderr)
        sys.exit(2)
    sys.exit(smoke())
