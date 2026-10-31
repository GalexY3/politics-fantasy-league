"""Conservative, SHA-pinned research-coverage view; never a legal admission API.

An independently displayed editorial counter is not an independent *source
database*. The recorded 31 Oct 2026 web observation lacks an archived HTML
original and precise observation time. As-of requests therefore see it only
after the END of that UTC calendar day. Default/latest is a local inventory.
Neither this view nor PDDL authorizes individual joins, outcomes or scoring.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/source_manifests/parcan_editorial_crossview_20261031.json"
EXPECTED_SHA256 = "a0133478a73f21916eec8575d2bea4803729deb8612d190cf0bf6641baf53bb1"
MIN_SAFE_OBSERVATION = datetime.fromisoformat("2026-11-01T00:00:00+00:00")
SOURCE_COUNTS = {
    2024: (686, "9ee6895522725f29cdf977ac0dd6da0490ad27c4128dea5fc2d0d7f48bf0e19c"),
    2025: (543, "13350568f6ef8f311b7bd8cb41791da1028550c98f3ef73bcc8bb4a78a7809ba"),
    2026: (524, "fe51a78cc89a9549b9e0232c27b638b6fd4fa0c1aefec2ce89ddb7455312dad2"),
}


def _unique_pairs(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError("DUPLICATE_JSON_KEY")
        seen[key] = value
    return seen


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


def _validate_manifest(path: Path) -> list[dict]:
    if not path.is_file() or path.stat().st_size > 10_000:
        raise ValueError("SOURCE_CROSSVIEW_MISSING_OR_LARGE")
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != EXPECTED_SHA256:
        raise ValueError("UNREVIEWED_CROSSVIEW_SHA")
    obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs,
                     parse_constant=lambda n: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))
    if (obj.get("schema") != "pfl.parcan.editorial_crossview.v1"
            or obj.get("observed_on") != "2026-10-31"
            or obj.get("publisher") != "Parlamento de Canarias"
            or obj.get("html_original_bytes_archived") is not False
            or obj.get("html_original_sha256") is not None
            or obj.get("html_http_date_or_signed_version") is not None
            or obj.get("html_reuse_permissions_reviewed") is not False
            or obj.get("html_source_database_independent_from_csv") is not None
            or obj.get("editorial_view_is_historical_vintage") is not False
            or obj.get("csv_first_public_at_certified") is not False
            or obj.get("eligible_longitudinal_risk_population_certified") is not False
            or obj.get("publisher_counter_crossview_only") is not True
            or obj.get("publisher_population_total_independent_backend_attested") is not False
            or obj.get("status_or_terminal_outcomes_analyzed") is not False
            or obj.get("data_rows_or_personal_data_exported") is not False
            or obj.get("cross_year_id_overlap_count") != 0
            or obj.get("ABH_cycles_consumed") != 0
            or obj.get("pe_counts_total_three_source_years") != 1753):
        raise ValueError("UNSUPPORTED_SOURCE_EVIDENCE_PROMOTION")
    cohorts = obj.get("cohorts")
    if not isinstance(cohorts, list) or len(cohorts) != 3:
        raise ValueError("UNEXPECTED_COHORTS")
    seen, out = set(), []
    for c in cohorts:
        if not isinstance(c, dict) or set(c) != {
                "year", "editorial_html_url", "editorial_reported_count", "csv_observed_rows",
                "csv_sha256", "count_equal"}:
            raise ValueError("UNEXPECTED_COHORT_SCHEMA")
        yr = c["year"]
        if type(yr) is not int or yr not in SOURCE_COUNTS or yr in seen:
            raise ValueError("UNEXPECTED_COHORT_YEAR")
        seen.add(yr)
        count, digest = SOURCE_COUNTS[yr]
        if (c["editorial_html_url"] !=
                f"https://www.parcan.es/iniciativas/arbol.py?ANIO={yr}&LEGIS=11&TIPO=PE"
                or type(c["editorial_reported_count"]) is not int
                or c["editorial_reported_count"] != count
                or type(c["csv_observed_rows"]) is not int
                or c["csv_observed_rows"] != count
                or c["csv_sha256"] != digest
                or c["count_equal"] is not True):
            raise ValueError("CROSSVIEW_NOT_MATCHED_TO_PINNED_SOURCE")
        out.append({
            "initiative_type": "PE", "legislature": 11, "year": yr,
            "publisher_editorial_count": count, "local_original_rows": count,
            "count_match": True,
            "independent_source_database_attested": False,
            "cohort_exhaustiveness_certified": False,
            "entry_event_complete": None,
            "dated_transitions_complete": None,
            "terminal_outcomes_complete": None,
            "historical_first_public_at": None,
            "historical_asof_usable": False,
            "eligible_risk_denominator": None,
        })
    if seen != set(SOURCE_COUNTS):
        raise ValueError("SOURCE_COHORT_MISSING")
    return sorted(out, key=lambda c: c["year"])


def coverage_status(*, as_of: str | None = None, path: Path | None = None) -> dict:
    """Report witnessed counts, and fail closed for unversioned historical queries.

    The comparison is only a *local source-catalogue metadata observation*.
    Its day-only time is safe-by (NOT first_public_at) next UTC midnight.
    """
    cutoff = _utc(as_of) if as_of is not None else None
    base = {
        "schema": "pfl.procedural_coverage.v1",
        "origin": "OFFICIAL_SOURCE_CROSSVIEW_METADATA_ONLY",
        "release_grade": False, "real_person_scoring": False,
        "full_canarian_parliament_risk_population": False,
        "full_national_congress_risk_population": False,
        "historical_asof_admitted": False,
        "cross_institutional_links_admitted": False,
        "outcomes_admitted": False,
        "right_censoring_estimable": False,
        "unknown_is_zero": False,
        "independent_database_verified": False,
        "first_public_at": None,
    }
    if cutoff is not None and cutoff < MIN_SAFE_OBSERVATION:
        return {**base, "status": "SOURCE_NOT_KNOWN_AT_REQUESTED_CUT",
                "source_strata": [], "editorial_count_total": None,
                "source_observed_rows": None,
                "safe_local_observation_by": None,
                "eligible_longitudinal_risk_denominator": None}
    try:
        rows = _validate_manifest(path if path is not None else MANIFEST)
    except (OSError, TypeError, ValueError, KeyError, AttributeError):
        return {**base, "status": "CROSSVIEW_QUARANTINED",
                "source_strata": [], "editorial_count_total": None,
                "source_observed_rows": None,
                "safe_local_observation_by": None,
                "eligible_longitudinal_risk_denominator": None}
    return {**base, "status": "CONCORDANT_SOURCE_COUNTERS_NOT_CENSUS",
            "source_strata": rows, "editorial_count_total": 1753,
            "source_observed_rows": 1753,
            "eligible_longitudinal_risk_denominator": None,
            "safe_local_observation_by": MIN_SAFE_OBSERVATION.isoformat(),
            "safe_by_is_not_first_public_at": True,
            "rights": "CSV CATALOGUE PDDL LABEL; HTML RIGHTS NOT ADJUDICATED",
            "missing_for_survival": [
                "EXHAUSTIVE_ENTRY_CENSUS", "ID_CROSSWALK_TO_EDITORIAL_INDEX",
                "DATED_PROCEDURAL_TRANSITIONS", "OBSERVED_TERMINAL_STATES_AND_CENSORING",
                "HISTORICAL_PUBLICATION_VINTAGES", "RIGHTS_AND_PURPOSE_REVIEW"],
            "interpretation": "Concordant editorial counts and captured CSV rows, potentially the same publisher database. Not a risk population, lifecycle or historical source vintage."}
