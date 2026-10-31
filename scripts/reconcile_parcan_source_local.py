"""Offline four-distribution provenance and monthly-observation audit.

Inputs are two immutable local JSONL files outside Git, with SHA-256 pinned to
earlier capture receipts. This tool NEVER opens original CSV or outcome cells,
and writes only non-person aggregate diagnostics (positive monthly counts).
Creation dates are reported by the current source, not first_public_at.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCES = (
    ("process_source_metadata.jsonl",
     "7ed31c97be3928e306749972f5b3d746ca0c20a961818674ff0626e9c6679463", 1211),
    ("pe2025_source_local_metadata.jsonl",
     "88041ac88a6dcb6e8b5c20ca89ae07fcdb6f95548a209042b4d6dd06aaec2bcc", 543),
)
SCOPES = {
    "PARCAN:LEG10:PPL:YEAR2023": (10, "PPL", 2023, 1,
                                   "c426afb56f8b5c51f84afeeadb281a340cf46ccc268f218b2d5841961bd9b095"),
    "PARCAN:LEG11:PE:YEAR2024": (11, "PE", 2024, 686,
                                   "9ee6895522725f29cdf977ac0dd6da0490ad27c4128dea5fc2d0d7f48bf0e19c"),
    "PARCAN:LEG11:PE:YEAR2025": (11, "PE", 2025, 543,
                                   "13350568f6ef8f311b7bd8cb41791da1028550c98f3ef73bcc8bb4a78a7809ba"),
    "PARCAN:LEG11:PE:YEAR2026": (11, "PE", 2026, 524,
                                   "fe51a78cc89a9549b9e0232c27b638b6fd4fa0c1aefec2ce89ddb7455312dad2"),
}
MAX_BYTES = 1_000_000
ALLOWED_KEYS = frozenset({
    "schema", "authority", "source_scope", "legislature", "process_family",
    "source_process_id", "created_on", "source_sha256", "first_public_at",
    "terminal_state", "transition_events", "outcome_fields_analyzed",
    "historical_asof_admitted", "scope_population_certified", "recorded_at",
    "source_capture_utc",
})


class AuditError(ValueError):
    pass


def unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise AuditError("DUPLICATE_JSON_KEY")
        out[key] = value
    return out


def utc(value):
    if not isinstance(value, str):
        raise AuditError("BAD_CLOCK")
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuditError("BAD_CLOCK") from exc
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise AuditError("NAIVE_CLOCK")
    return moment.astimezone(timezone.utc)


def audit_payloads(payloads: list[bytes], *, expected_sources=SOURCES) -> dict:
    if len(payloads) != len(expected_sources):
        raise AuditError("MISSING_SOURCE_FILES")
    seen = set()
    counts = Counter()
    months = Counter()
    count_by_file = []
    for payload, (_, pinned_digest, expected_count) in zip(payloads, expected_sources):
        if not isinstance(payload, bytes) or not 0 < len(payload) <= MAX_BYTES:
            raise AuditError("INVALID_LOCAL_JSONL_BYTES")
        if sha256(payload).hexdigest() != pinned_digest:
            raise AuditError("LOCAL_JSONL_SHA_MISMATCH")
        lines = payload.splitlines()
        if len(lines) != expected_count:
            raise AuditError("LOCAL_JSONL_COUNT_MISMATCH")
        for line in lines:
            if len(line) > 8192:
                raise AuditError("OVERSIZED_METADATA_ROW")
            try:
                record = json.loads(line, object_pairs_hook=unique_pairs,
                                    parse_constant=lambda _: (_ for _ in ()).throw(
                                        AuditError("NONFINITE_JSON")))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise AuditError("MALFORMED_METADATA_ROW") from exc
            if not isinstance(record, dict) or set(record) - ALLOWED_KEYS:
                raise AuditError("UNKNOWN_SOURCE_LOCAL_FIELD")
            scope = record.get("source_scope")
            if scope not in SCOPES:
                raise AuditError("UNKNOWN_PROCESS_SCOPE")
            leg, kind, year, _, expected_raw = SCOPES[scope]
            if (record.get("schema") != "pfl.parcan_source_local_process_metadata.v1"
                    or record.get("authority") != "PARLAMENTO_CANARIAS"
                    or type(record.get("legislature")) is not int
                    or record["legislature"] != leg
                    or record.get("process_family") != kind
                    or record.get("source_sha256") != expected_raw
                    or record.get("first_public_at") is not None
                    or record.get("terminal_state") is not None
                    or record.get("transition_events") is not None
                    or record.get("outcome_fields_analyzed") is not False
                    or record.get("historical_asof_admitted") is not False
                    or record.get("scope_population_certified") is not False):
                raise AuditError("SOURCE_LOCAL_SEMANTICS_CHANGED")
            ident = record.get("source_process_id")
            if not isinstance(ident, str) or not ident or len(ident) > 160:
                raise AuditError("BAD_SOURCE_LOCAL_ID")
            key = (leg, kind, ident)
            if key in seen:
                raise AuditError("DUPLICATE_CROSS_DISTRIBUTION_PROCESS_ID")
            seen.add(key)
            try:
                created = date.fromisoformat(record["created_on"])
            except (ValueError, TypeError, KeyError) as exc:
                raise AuditError("INVALID_DATE_ONLY") from exc
            if created.isoformat() != record["created_on"] or created.year != year:
                raise AuditError("WRONG_SOURCE_YEAR")
            recorded = utc(record.get("recorded_at"))
            if created > recorded.date():
                raise AuditError("BACKDATED_OR_FUTURE_CREATION")
            if record.get("source_capture_utc") is not None and (
                    utc(record["source_capture_utc"]) > recorded):
                raise AuditError("RECORD_BEFORE_SOURCE_CAPTURE")
            counts[scope] += 1
            months[(scope, created.isoformat()[:7])] += 1
        count_by_file.append(len(lines))
    for scope, (_, _, _, expected_count, _) in SCOPES.items():
        if counts[scope] != expected_count:
            raise AuditError("COHORT_MISSING_OR_OVERCOUNTED")
    result = {
        "schema": "pfl.parcan.creation_month_aggregate.v1",
        "provenance": "TWO_PINNED_LOCAL_JSONL_FILES",
        "publisher": "Parlamento de Canarias",
        "input_local_jsonl_sha256": [x[1] for x in expected_sources],
        "source_local_total": sum(counts.values()),
        "source_local_unique_keys": len(seen),
        "input_rows_per_file": count_by_file,
        "distribution_counts": [
            {"scope": scope, "records_in_captured_distribution": counts[scope]}
            for scope in sorted(SCOPES)],
        "creation_months_with_observed_records_only": [
            {"scope": scope, "source_reported_created_month": month, "observed_entries": count}
            for (scope, month), count in sorted(months.items())],
        "missing_months_are_unknown_not_zero": True,
        "source_creation_date_is_first_public_at": False,
        "historical_asof_verified": False,
        "terminal_states_or_transitions_analyzed": False,
        "political_outcome_model_executed": False,
        "publisher_census_completeness_certified": False,
        "individual_rows_exported": False,
        "ABH_cycles": 0,
    }
    return result


def build(*, earlier: Path, later: Path, output: Path) -> dict:
    candidates = (earlier, later)
    if any(p.is_symlink() for p in candidates):
        raise AuditError("SYMLINK_SOURCE_NOT_PERMITTED")
    paths = tuple(p.resolve(strict=True) for p in candidates)
    for path, (filename, _, _) in zip(paths, SOURCES):
        if (not path.is_file() or path.name != filename
                or path == REPO or REPO in path.parents):
            raise AuditError("SOURCE_MUST_BE_LOCAL_OUTSIDE_GIT")
    dest = output.resolve(strict=False)
    if (dest.exists() or dest.parent != REPO / "data" / "source_manifests"
            or dest.name != "parcan_source_local_months_20261031.json"):
        raise AuditError("OUTPUT_MUST_BE_NEW_AGGREGATE_IN_GIT")
    result = audit_payloads([p.read_bytes() for p in paths])
    # Posthoc metadata audit clock. Never use this to backfill original first publication.
    audited = datetime.now(timezone.utc).replace(microsecond=0)
    result["local_aggregate_audited_at"] = audited.isoformat()
    result["local_aggregate_safe_by"] = (audited + timedelta(seconds=1)).isoformat()
    result["source_csv_originals_remain_outside_git"] = True
    with dest.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    return {"observed":result["source_local_total"], "unique":result["source_local_unique_keys"],
            "monthly_observed_cells":len(result["creation_months_with_observed_records_only"]),
            "aggregate_sha256":sha256(dest.read_bytes()).hexdigest(),
            "safe_by":result["local_aggregate_safe_by"],
            "ABH_cycles":0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--earlier", type=Path, required=True)
    parser.add_argument("--later", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(earlier=args.earlier, later=args.later, output=args.output),
                     sort_keys=True))
