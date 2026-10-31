"""Documentary Canary-Islands initiative cohort inventory, for LOCAL observatory.

Only a versioned, SHA-pinned *aggregate* is admissible. The actual personal
and outcome-containing CSV originals remain in the user's separate local raw
workspace; they are never read here. This is not a historical source-vintage
archive or a complete denominator for the Parliament of the Canary Islands.

as_of is the time at which the local audited snapshot existed, never the first
historical publication of each process. Earlier queries fail closed.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "research/PFL_SYSTEM20_20261031/PARCAN_COHORTS/receipts/metadata_only_coverage.json"
EXPECTED_SHA256 = "72f4c0a66c80a032c108b70a6051fe79f9916e12bf202a6720a5968785328b64"
PE2025_RECEIPT = ROOT / "research/PFL_SYSTEM20_20261031/PARCAN_COHORTS/PE2025_METADATA_ONLY_RECEIPT.json"
PE2025_EXPECTED_SHA256 = "0ce42317bd0802f7e7546483d26abcb63f1a9c128350fbe4f30ea007a2ce7ce3"
PE2025_SOURCE_SHA256 = "13350568f6ef8f311b7bd8cb41791da1028550c98f3ef73bcc8bb4a78a7809ba"
PE2025_CAPTURE_RECEIPT_SHA256 = "e96bc4a300fa1c886d0a33403ab9e9c67dec93525edc9f68ec7eb39270238c53"
PE2025_PRECAPTURE_FREEZE_SHA256 = "8ffab701bf241fbb591e9a37673497b57cb2ce544a7fe766c6c19c12d11a247a"
PE2025_AUDIT_AT = datetime.fromisoformat("2026-10-31T05:34:51+00:00")
MONTHLY_RECEIPT = ROOT / "data/source_manifests/parcan_source_local_months_20261031.json"
MONTHLY_EXPECTED_SHA256 = "c86e3d8f6d889bede76f2c215e61e9bea880c3fabc3db40c97317ccd6fc5927f"
MONTHLY_AUDIT_AT = datetime.fromisoformat("2026-10-31T05:49:50+00:00")
MONTHLY_SAFE_BY = datetime.fromisoformat("2026-10-31T05:49:51+00:00")
MONTHLY_SOURCE_SCOPE = {
    "PARCAN:LEG10:PPL:YEAR2023": 1,
    "PARCAN:LEG11:PE:YEAR2024": 686,
    "PARCAN:LEG11:PE:YEAR2025": 543,
    "PARCAN:LEG11:PE:YEAR2026": 524,
}
SOURCES = {
    ("PPL", 2023, 10): ("c426afb56f8b5c51f84afeeadb281a340cf46ccc268f218b2d5841961bd9b095", 1,
                       "https://datos.parcan.es/dataset/iniciativas_tipoppl_anio2023_xlegislatura/resource/dd23200f-d3df-4360-92d9-45807ba5da87"),
    ("PE", 2024, 11): ("9ee6895522725f29cdf977ac0dd6da0490ad27c4128dea5fc2d0d7f48bf0e19c", 686,
                      "https://datos.parcan.es/dataset/iniciativas_tipope_anio2024_xilegislatura"),
    ("PE", 2026, 11): ("fe51a78cc89a9549b9e0232c27b638b6fd4fa0c1aefec2ce89ddb7455312dad2", 524,
                      "https://datos.parcan.es/dataset/iniciativas_tipope_anio2026_xilegislatura"),
}


def _pairs(pairs: list[tuple[str, object]]) -> dict:
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("DUPLICATED_JSON_KEY")
        out[key] = value
    return out


def _utc(value: str) -> datetime:
    if not isinstance(value, str) or len(value) > 42 or "T" not in value:
        raise ValueError("INVALID_AS_OF")
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("INVALID_AS_OF") from exc
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError("AS_OF_REQUIRES_TIMEZONE")
    return moment.astimezone(timezone.utc)


def _safe_after_second_precision_audit(moment: datetime) -> datetime:
    """An audit timestamp truncated to whole seconds is known by *next* second.

    Neither a recorded '05:34:51' nor an HTTP Date proves that the artifact
    already existed at '05:34:51.000000'. Fail closed throughout that second.
    """
    if moment.microsecond != 0:
        raise ValueError("AUDIT_TIME_PRECISION_CHANGED")
    return moment + timedelta(seconds=1)


def _read_receipt(path: Path) -> tuple[datetime, list[dict]]:
    if not path.is_file() or path.stat().st_size > 20_000:
        raise ValueError("MISSING_OR_OVERSIZED_METADATA_RECEIPT")
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != EXPECTED_SHA256:
        raise ValueError("UNREVIEWED_METADATA_RECEIPT")
    doc = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                     parse_constant=lambda x: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))
    if (doc.get("kind") != "PHASE1_METADATA_ONLY_AFTER_CAPTURE"
            or doc.get("institution") != "Parlamento de Canarias"
            or doc.get("outcomes_analyzed") is not False
            or doc.get("outcome_typed_cells_decoded_by_csv_parser") is not True
            or doc.get("raw_person_fields_exported") is not False
            or doc.get("raw_source_downloads_here") != 0
            or doc.get("first_public_at_historically_verified") != 0
            or doc.get("not_a_full_parliament_universe") is not True):
        raise ValueError("METADATA_RECEIPT_SEMANTICS_CHANGED")
    seen = set()
    out = []
    raw_sources = doc.get("source_cohorts")
    if not isinstance(raw_sources, list) or len(raw_sources) != 3:
        raise ValueError("COHORTS_OUTSIDE_FROZEN_SCOPE")
    for item in raw_sources:
        if not isinstance(item, dict) or not isinstance(item.get("stratum"), dict):
            raise ValueError("INVALID_COHORT")
        s = item["stratum"]
        kind = s.get("initiative_type", s.get("initiative_type_code"))
        key = (kind, s.get("year"), s.get("legislature"))
        if key not in SOURCES or key in seen:
            raise ValueError("UNEXPECTED_OR_DUPLICATE_COHORT")
        seen.add(key)
        digest, rows, url = SOURCES[key]
        if (item.get("original_sha256") != digest
                or type(item.get("records_read")) is not int
                or item["records_read"] != rows
                or item.get("distinct_nonmissing_id_legislature_keys") != rows
                or item.get("missing_id") != 0
                or item.get("missing_legislature") != 0
                or item.get("missing_creation_date") != 0
                or item.get("same_key_same_metadata_rows") != 0
                or item.get("same_key_conflicting_creation_date_rows") != 0
                or item.get("outcome_values_not_inspected_or_aggregated") is not True
                or item.get("full_csv_rows_parsed_for_structure") is not True
                or item.get("pagination_completeness_verified") is not False
                or item.get("complete_congress_population") is not False
                or item.get("complete_parliamentary_population") is not False
                or item.get("first_public_at") is not None
                or item.get("response_status") != 200):
            raise ValueError("COHORT_METADATA_SEMANTICS_CHANGED")
        out.append({
            "institution": "Parlamento de Canarias",
            "initiative_type": kind, "legislature": key[2], "year": key[1],
            "source_distribution_url": url,
            "capture_sha256": digest, "rows_in_captured_distribution": rows,
            "distinct_id_legislature_keys": rows, "missing_creation_date": 0,
            "first_public_at": None, "outcomes_accessed_for_analysis": False,
            "source_population_complete": False, "individual_records_exposed": False,
        })
    if seen != set(SOURCES):
        raise ValueError("MISSING_COHORT")
    out.sort(key=lambda x: (x["year"], x["initiative_type"]))
    return _utc(doc["audited_utc"]), out


def _read_pe2025(path: Path) -> tuple[datetime, dict]:
    """Pin the later independent audit without rewriting the old 3-cohort snapshot."""
    if not path.is_file() or path.stat().st_size > 15_000:
        raise ValueError("MISSING_OR_OVERSIZED_PE2025_RECEIPT")
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != PE2025_EXPECTED_SHA256:
        raise ValueError("UNREVIEWED_PE2025_RECEIPT")
    doc = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                     parse_constant=lambda x: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))
    if (doc.get("schema") != "pfl.parcan.pe2025.metadata_only.v1"
            or doc.get("publisher") != "Parlamento de Canarias"
            or doc.get("catalogue") != "https://datos.parcan.es/dataset/iniciativas_tipope_anio2025_xilegislatura"
            or doc.get("license") != "odc-pddl"
            or doc.get("stratum") != {"initiative_type": "PE", "legislature": 11, "year": 2025}
            or doc.get("source_sha256") != PE2025_SOURCE_SHA256
            or doc.get("capture_receipt_sha256") != PE2025_CAPTURE_RECEIPT_SHA256
            or doc.get("precapture_freeze_sha256") != PE2025_PRECAPTURE_FREEZE_SHA256
            or type(doc.get("source_bytes")) is not int or doc["source_bytes"] != 165663
            or type(doc.get("records_read")) is not int or doc["records_read"] != 543
            or doc.get("distinct_nonmissing_id_legislature_keys") != 543
            or doc.get("date_string_shape_counts") != {"yyyy-mm-dd": 543}
            or doc.get("distinct_legislature_labels") != 1
            or any(doc.get(key) != 0 for key in (
                "missing_id", "missing_legislature", "missing_creation_date",
                "same_key_same_metadata_rows", "same_key_conflicting_creation_date_rows"))
            or any(doc.get(key) is not False for key in (
                "current_outcomes_interpreted", "historical_asof_admitted",
                "historical_outcome_vintages_admitted", "pagination_completeness_verified",
                "population_completeness_certified", "complete_parliamentary_population",
                "complete_congress_population", "scientific_preregistered"))
            or any(doc.get(key) is not True for key in (
                "full_csv_rows_parsed_for_structure",
                "outcome_values_not_inspected_or_aggregated",
                "records_not_redistributed", "source_rows_only_on_local_disk"))
            or doc.get("first_public_at") is not None
            or doc.get("source_first_public_at") is not None
            or doc.get("publisher_expected_row_total") is not None
            or doc.get("ABH_cycles") != 0):
        raise ValueError("PE2025_METADATA_SEMANTICS_CHANGED")
    audited = _utc(doc["audited_utc"])
    if audited != PE2025_AUDIT_AT:
        raise ValueError("PE2025_AUDIT_TIME_CHANGED")
    return audited, {
        "institution": "Parlamento de Canarias", "initiative_type": "PE",
        "legislature": 11, "year": 2025,
        "source_distribution_url": doc["catalogue"],
        "capture_sha256": PE2025_SOURCE_SHA256,
        "rows_in_captured_distribution": 543,
        "distinct_id_legislature_keys": 543, "missing_creation_date": 0,
        "first_public_at": None, "outcomes_accessed_for_analysis": False,
        "source_population_complete": False, "individual_records_exposed": False,
    }


def _read_monthly_summary(path: Path) -> list[dict]:
    """A derived, non-person count of source-reported creation months only."""
    if not path.is_file() or path.stat().st_size > 12_000:
        raise ValueError("MONTHLY_RECEIPT_MISSING_OR_LARGE")
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != MONTHLY_EXPECTED_SHA256:
        raise ValueError("MONTHLY_RECEIPT_UNREVIEWED")
    doc = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                     parse_constant=lambda x: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))
    if (doc.get("schema") != "pfl.parcan.creation_month_aggregate.v1"
            or doc.get("provenance") != "TWO_PINNED_LOCAL_JSONL_FILES"
            or doc.get("publisher") != "Parlamento de Canarias"
            or doc.get("input_local_jsonl_sha256") != [
                "7ed31c97be3928e306749972f5b3d746ca0c20a961818674ff0626e9c6679463",
                "88041ac88a6dcb6e8b5c20ca89ae07fcdb6f95548a209042b4d6dd06aaec2bcc"]
            or doc.get("input_rows_per_file") != [1211, 543]
            or doc.get("local_aggregate_audited_at") != MONTHLY_AUDIT_AT.isoformat()
            or doc.get("local_aggregate_safe_by") != MONTHLY_SAFE_BY.isoformat()
            or doc.get("source_local_total") != 1754
            or doc.get("source_local_unique_keys") != 1754
            or doc.get("missing_months_are_unknown_not_zero") is not True
            or doc.get("source_creation_date_is_first_public_at") is not False
            or doc.get("historical_asof_verified") is not False
            or doc.get("terminal_states_or_transitions_analyzed") is not False
            or doc.get("publisher_census_completeness_certified") is not False
            or doc.get("individual_rows_exported") is not False
            or doc.get("ABH_cycles") != 0):
        raise ValueError("MONTHLY_SEMANTICS_CHANGED")
    cohorts = doc.get("distribution_counts")
    if not isinstance(cohorts, list) or len(cohorts) != 4 or {
        c["scope"]: c["records_in_captured_distribution"] for c in cohorts
    } != MONTHLY_SOURCE_SCOPE:
        raise ValueError("MONTHLY_COHORTS_CHANGED")
    rows = doc.get("creation_months_with_observed_records_only")
    if not isinstance(rows, list) or len(rows) != 34:
        raise ValueError("MONTHLY_SHAPE_CHANGED")
    seen, counts, out = set(), {}, []
    for item in rows:
        if not isinstance(item, dict) or set(item) != {
                "scope", "source_reported_created_month", "observed_entries"}:
            raise ValueError("MONTHLY_UNEXPECTED_FIELD")
        scope, month, count = item["scope"], item["source_reported_created_month"], item["observed_entries"]
        if (scope not in MONTHLY_SOURCE_SCOPE or not isinstance(month, str)
                or not re.fullmatch(r"20\d{2}-(?:0[1-9]|1[0-2])", month)
                or int(month[:4]) != int(scope.rsplit("YEAR", 1)[1])
                or type(count) is not int or count < 1
                or (scope, month) in seen):
            raise ValueError("MONTHLY_TIME_OR_COUNT_INVALID")
        seen.add((scope, month))
        counts[scope] = counts.get(scope, 0) + count
        out.append({"scope": scope, "source_reported_created_month": month,
                    "observed_entries": count})
    if counts != MONTHLY_SOURCE_SCOPE:
        raise ValueError("MONTHLY_SUMS_NOT_RECONCILED")
    return sorted(out, key=lambda r: (r["source_reported_created_month"], r["scope"]))


def status(*, as_of: str | None = None, path: Path | None = None) -> dict:
    """Expose real, aggregate, provenance-bound rows as a local-audit snapshot.

    Before the audited snapshot date, no census values or hashes are returned.
    Missing knowledge is NULL, not zero. This is not first_public_at.
    """
    base = {
        "ok": False, "origin": "PDDL_CANARIAS_AGGREGATE_ONLY",
        "release_grade": False, "real_person_scoring": False,
        "process_lifecycle_or_outcomes_admitted": False,
        "historical_publication_times_verified": 0,
        "congress_initiative_universe_verified": False,
        "complete_canarian_parliament_universe": False,
        "available_historial_vintages": False,
    }
    try:
        requested = _utc(as_of) if as_of is not None else None
        audited, rows = _read_receipt(path if path is not None else RECEIPT)
        if PE2025_AUDIT_AT <= audited:
            raise ValueError("NONMONOTONE_SOURCE_AUDIT_TIMES")
        if requested is not None and requested < _safe_after_second_precision_audit(audited):
            return {
                **base, "ok": True, "status": "NOT_KNOWN_TO_LOCAL_OBSERVATORY_AT_CUT",
                "as_of": requested.isoformat(), "local_snapshot_audited_at": None,
                "source_cohorts": [], "observed_rows": None, "exposure_denominator": None,
                "semantics": "Unknown to local system at cut, NOT zero parliamentary initiatives.",
            }
        # Critical: a compromised future receipt cannot retroactively erase a
        # valid earlier snapshot or disclose its later source. We need not read it.
        show_later = requested is None or requested >= _safe_after_second_precision_audit(PE2025_AUDIT_AT)
        if show_later:
            next_audited, pe2025 = _read_pe2025(PE2025_RECEIPT)
            rows = sorted([*rows, pe2025], key=lambda x: (x["year"], x["initiative_type"]))
        visible_audit = PE2025_AUDIT_AT if show_later else audited
        monthly_rows, monthly_status, monthly_audit = None, "NOT_AUDITED_AT_CUT", None
        if show_later and (requested is None or requested >= MONTHLY_SAFE_BY):
            try:
                monthly_rows = _read_monthly_summary(MONTHLY_RECEIPT)
                monthly_status = "SOURCE_CREATION_MONTHS_AUDITED_ONLY"
                monthly_audit = MONTHLY_AUDIT_AT.isoformat()
            except (OSError, ValueError, TypeError, KeyError, AttributeError):
                # Quarantine this newer optional derivative, not the earlier
                # independently pinned annual cohorts.
                monthly_status = "MONTHLY_DERIVATIVE_QUARANTINED"
        return {
            **base, "ok": True, "status": "AUDITED_METADATA_CURRENT_CAPTURE",
            "as_of": (requested.isoformat() if requested is not None else None),
            "local_snapshot_audited_at": visible_audit.isoformat(),
            "source_licence": "Open Data Commons PDDL (distribution catalogue)",
            "source_cohorts": rows,
            "observed_rows": sum(x["rows_in_captured_distribution"] for x in rows),
            "exposure_denominator": None,
            "creation_monthly_status": monthly_status,
            "creation_monthly_observed_entries": monthly_rows,
            "creation_monthly_local_audited_at": monthly_audit,
            "creation_monthly_missing_months_unknown_not_zero": True,
            "creation_monthly_first_public_at_verified": False,
            "comparability": ("2024/2025/2026 PE in XI legislature (three source distributions, not certified exhaustive); "
                              "2023 PPL different type/legislature" if show_later else
                              "2024/2026 PE in XI legislature; 2025 not yet audited at this local as-of; "
                              "2023 PPL different type/legislature"),
            "semantics": "Current captured distribution metadata, not historical status transitions or a complete opportunity census.",
        }
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        if isinstance(exc, ValueError) and str(exc) in {"INVALID_AS_OF", "AS_OF_REQUIRES_TIMEZONE"}:
            raise
        return {**base, "status": "METADATA_QUARANTINED", "source_cohorts": [], "observed_rows": None,
                "exposure_denominator": None}
