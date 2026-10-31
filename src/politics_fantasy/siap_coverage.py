"""Catalan Parliament SIAP: one witnessed index page, not a research cohort.

The original HTML is protected in a separate local scratch folder. This
read-only aggregate is pinned to a reviewed capture/metadata receipt. It never
reads case names, IDs, outcomes, HTML or the private scratch directory.
Current-capture visibility is deliberately distinct from historical public
availability, which is UNKNOWN, and from a complete entry denominator.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/source_manifests/catalunya_siap_page1_20261031.json"
MANIFEST_SHA256 = "d1e127cb0bdb4c74e01b6e2f4615ecadcbad5cc1ae3852448f0da59e472666fe"
SAFE_LOCAL_OBSERVATION_BY = datetime.fromisoformat("2026-10-31T06:02:49+00:00")
SOURCE_URL = ("https://www.parlament.cat/web/activitat-parlamentaria/"
              "iniciatives-legislatives/proposicions-llei/index.html")
ORIGINAL_SHA256 = "3846b9fec8f20b426bfa1c231b717e0c20664d08aaf8586e49171339d927fc8d"


def _unique_pairs(pairs):
    obj = {}
    for name, value in pairs:
        if name in obj:
            raise ValueError("DUPLICATE_JSON_KEY")
        obj[name] = value
    return obj


def _utc(value: str) -> datetime:
    if not isinstance(value, str) or len(value) > 42 or "T" not in value:
        raise ValueError("INVALID_AS_OF")
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("INVALID_AS_OF") from exc
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("AS_OF_REQUIRES_TIMEZONE")
    return instant.astimezone(timezone.utc)


def _admit_manifest(path: Path) -> dict:
    if not path.is_file() or not 0 < path.stat().st_size < 10_000:
        raise ValueError("MISSING_OR_OVERSIZED_MANIFEST")
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != MANIFEST_SHA256:
        raise ValueError("UNREVIEWED_MANIFEST")
    row = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs,
                     parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))
    required = {
        "schema": "pfl.siap.catalunya.capture_page_metadata.v1",
        "publisher": "Parlament de Catalunya",
        "system": "SIAP",
        "source_url": SOURCE_URL,
        "original_local_only": True,
        "original_bytes": 21934,
        "original_sha256": ORIGINAL_SHA256,
        "original_http_status": 200,
        "original_http_content_type": "text/html; charset=UTF-8",
        "original_http_date": "Sat, 31 Oct 2026 06:02:44 GMT",
        "capture_completed_utc": "2026-10-31T06:02:48+00:00",
        "sent_cookie": False, "cookie_jar_used": False,
        "terms_accepted": False, "redirects_followed": False,
        "original_capture_receipt_sha256": "57cd91bb7bf838aaf899305e67ac912223440d9268093282796706e941d1870b",
        "precapture_parser_freeze_sha256": "19d35816554f10c753c76657ccd8b4db97c757f402c7170390a90a2f2c29e7ea",
        "parser_code_sha256": "ff14bbebc9fee8d56b3afa432eff9794ff4805e815cf99c955d3c8726b37ae3b",
        "metadata_only_receipt_sha256": "ee2824bd526fec8e563ff7f8e08a0b4fb8c080645852fa334ce05320bd2d12c4",
        "index_pages_advertised": 44,
        "index_pages_captured": 1,
        "index_pages_not_captured": 43,
        "page_one_index_position": 1,
        "source_local_process_links_page_one": 20,
        "source_local_process_links_unique_page_one": 20,
        "source_local_process_links_emitted": False,
        "pagination_complete": False,
        "institutional_entry_registry_complete": False,
        "pre_admission_processes_included_verified": False,
        "pending_and_failed_outcomes_analyzed": False,
        "historical_first_public_at": None,
        "document_published_at": None,
        "source_current_capture_only": True,
        "first_public_at_backfilled_from_capture": False,
        "right_censored_process_outcomes_known": False,
        "eligible_longitudinal_risk_denominator": None,
        "reuse_specific_personal_purpose_adjudicated": False,
        "robots_receipt_sha256": "d2793c4248c2505ba0941ba75059243af26c89898dffe627f77ba137b2dfc99b",
        "robot_attempt_http_status": 404,
        "robot_attempt_retried": False,
        "real_people_scored": False,
        "original_rows_published": False,
        "scientific_ABH_cycles": 0,
    }
    if not isinstance(row, dict) or any(
            type(row.get(key)) is not type(value) or row[key] != value
            for key, value in required.items()):
        raise ValueError("SOURCE_METADATA_OR_EVIDENCE_ESCALATED")
    if (row.get("source_errors") != [
            "UNVERIFIED_PAGE_2_THROUGH_44",
            "UNVERIFIED_PRE_ADMISSION_COVERAGE",
            "NO_HISTORICAL_VINTAGE_SEQUENCE",
            "ROBOTS_TXT_HTTP_404", "NO_VERIFIED_MASS_CRAWL_POLICY"]):
        raise ValueError("SOURCE_UNCERTAINTY_MISSING")
    if (_utc(row["capture_completed_utc"]) >= SAFE_LOCAL_OBSERVATION_BY
            or row.get("legal_notice") !=
            "https://www.parlament.cat/wp/pcat/serveis-parlament/avis-legal/"):
        raise ValueError("LOCAL_CAPTURE_OR_RIGHTS_CHANGED")
    return row


def status(*, as_of: str | None = None, path: Path | None = None) -> dict:
    """Display only index metadata at its conservative local observation cut."""
    cut = _utc(as_of) if as_of is not None else None
    base = {
        "schema": "pfl.siap_coverage.v1", "institution": "Parlament de Catalunya",
        "release_grade": False, "individual_records_exposed": False,
        "historical_first_public_at": None, "historical_asof_admitted": False,
        "outcomes_analyzed": False, "right_censoring_estimable": False,
        "full_parliament_risk_population_verified": False,
        "eligible_risk_denominator": None, "links_to_other_institutions": False,
        "real_person_scoring": False,
    }
    if cut is not None and cut < SAFE_LOCAL_OBSERVATION_BY:
        return {**base, "status": "NOT_YET_IN_LOCAL_OBSERVATORY",
                "source_index_pages": None, "source_pages_captured": None,
                "observed_links": None, "safe_local_observation_by": None,
                "original_sha256": None}
    try:
        doc = _admit_manifest(path or MANIFEST)
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return {**base, "status": "INDEX_METADATA_QUARANTINED",
                "source_index_pages": None, "source_pages_captured": None,
                "observed_links": None, "safe_local_observation_by": None,
                "original_sha256": None}
    return {**base, "status": "ONE_INDEX_PAGE_OF_UNCERTIFIED_POPULATION",
            "source_url": SOURCE_URL,
            "source_index_pages": doc["index_pages_advertised"],
            "source_pages_captured": doc["index_pages_captured"],
            "source_pages_missing": doc["index_pages_not_captured"],
            "observed_links": doc["source_local_process_links_unique_page_one"],
            "safe_local_observation_by": SAFE_LOCAL_OBSERVATION_BY.isoformat(),
            "safe_local_observation_is_first_public_at": False,
            "original_sha256": ORIGINAL_SHA256,
            "original_bytes": 21934,
            "source_original_outside_git": True,
            "rights_scope": "GENERAL_INFORMATION_REUSE; PERSON_PURPOSE_NOT_ADJUDICATED",
            "census_gate_status": "PAGINATION_AND_PRE_ADMISSION_UNVERIFIED",
            "interpretation": "One current HTML index page of 44, without completed source pagination, historical states or first_public_at. Distinct institution and family from Canarias PE."}
