"""Public aggregate publication metadata for the Spanish research observatory.

Reading this manifest does NOT read originals from the private local raw lake
or admit individual identities, historical completeness, legal rights or scoring.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[2] / "data/source_manifests/interior_congreso_20261031.json"
AGGREGATE = (Path(__file__).resolve().parents[2]
             / "research/PFL_SYSTEM20_20261031/INTERIOR_METADATA/receipts/phase2.json")
IDS = {"INTERIOR_CONGRESO_ELECTED", "INTERIOR_CONGRESO_RESULTS"}
HASH = re.compile(r"[0-9a-f]{64}\Z")
URL_PREFIX = "https://descargas.interior.gob.es/datasets/resultados_electorales/"
AGGREGATE_SHA256 = "e2128f79c6bb06ca51953d99746a5c0267fcb5fc89f4a119356fa2c344d04207"
POLICY_SHA256 = "bfb0548942cf0f6f03336d0a4eb86c0d7408118bb9594abbe4975217b2e7e929"


def _strict_pairs(pairs: list[tuple[str, object]]) -> dict:
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("DUPLICATE_JSON_KEY")
        out[key] = value
    return out


def _metadata_only(path: Path) -> dict:
    """Only an exact, reviewed, non-person aggregate gets rendered publicly.

    The receipt proves a local exploration, NOT census completeness, data
    rights for subjects, first historical publication, or scientific validity.
    """
    from hashlib import sha256
    if not path.is_file() or path.stat().st_size > 25_000:
        raise ValueError("MISSING_AGGREGATE")
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != AGGREGATE_SHA256:
        raise ValueError("UNREVIEWED_AGGREGATE_REVISION")
    obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_strict_pairs,
                     parse_constant=lambda x: (_ for _ in ()).throw(ValueError("NONFINITE")))
    if (obj.get("phase") != "PHASE2_AGGREGATE_NON_OUTCOME"
            or obj.get("policy_sha256") != POLICY_SHA256
            or obj.get("causal_or_abh_conclusions") is not False
            or obj.get("raw_originals_recaptured") is not False
            or obj.get("download_requests") != 0
            or obj.get("source_first_public_at") is not None):
        raise ValueError("AGGREGATE_NOT_METADATA_ONLY")
    rows = obj.get("outputs")
    if not isinstance(rows, list) or len(rows) != 2:
        raise ValueError("AGGREGATE_DISTRIBUTION_MISMATCH")
    expected = {
        "Elecciones-Congreso-cargos-electos.xlsx": {"A", "B", "C", "D", "E"},
        "Elecciones-Congreso.xlsx": {"A", "B", "C"},
    }
    result = {}
    for item in rows:
        if not isinstance(item, dict):
            raise ValueError("INVALID_AGGREGATE_ROW")
        name = item.get("filename")
        if name not in expected or name in result or item.get("status") != "AGGREGATE_EXPLORATORY_ONLY":
            raise ValueError("UNRECOGNIZED_AGGREGATE_SOURCE")
        if item.get("person_rows_or_outcome_values_exported") is not False:
            raise ValueError("SUBJECT_VALUES_EXPORTED")
        if set(item.get("metadata_columns_by_letter", {})) != expected[name]:
            raise ValueError("SENSITIVE_METADATA_COLUMN")
        total = item.get("rows_scanned")
        valid = item.get("valid_year_rows")
        years = item.get("year_counts")
        if (type(total) is not int or type(valid) is not int or total < 1
                or valid != total or not isinstance(years, dict) or len(years) > 40):
            raise ValueError("INVALID_AGGREGATE_COUNTS")
        if any(not isinstance(y, str) or not y.isdigit() or not 1970 <= int(y) <= 2026
               or type(n) is not int or n < 0 for y, n in years.items()):
            raise ValueError("INVALID_YEAR_COUNTS")
        if sum(years.values()) != total:
            raise ValueError("YEAR_TOTAL_DISAGREEMENT")
        result[name] = {
            "rows_in_document": total, "observed_years": len(years),
            "first_year": min(years), "last_year": max(years),
            "rows_by_year": dict(sorted(years.items())),
            "missing_in_selected_administrative_columns": 0,
            "coverage_status": "METADATA_ROWS_NOT_CERTIFIED_UNIVERSE",
            "individual_values_released": False,
        }
    if set(result) != set(expected):
        raise ValueError("AGGREGATE_DISTRIBUTION_MISMATCH")
    return result


def published_sources(path: Path | None = None, aggregate_path: Path | None = None) -> dict:
    """Return only a bounded, scrutinized aggregate of public source references."""
    blocked = {"ok": False, "source_data": [], "real_person_scoring": False,
               "source_corpus_admitted": False, "error": "MANIFEST_UNAVAILABLE_OR_INVALID"}
    try:
        path = path if path is not None else MANIFEST
        if not path.is_file() or path.stat().st_size > 25_000:
            return blocked
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("schema") != "pfl.source_capture_manifest.v1":
            return blocked
        items = doc.get("distribution")
        if not isinstance(items, list) or len(items) != 2 or {item["id"] for item in items} != IDS:
            return blocked
        out = []
        for item in items:
            if not isinstance(item, dict):
                return blocked
            filename = item.get("filename")
            url = item.get("official_url")
            digest = item.get("sha256")
            size = item.get("byte_length")
            if (not isinstance(filename, str) or filename not in
                    {"Elecciones-Congreso.xlsx", "Elecciones-Congreso-cargos-electos.xlsx"}
                    or url != URL_PREFIX + filename or not isinstance(digest, str)
                    or not HASH.fullmatch(digest) or not isinstance(size, int)
                    or not 0 < size <= 25_000_000 or item.get("http_status") != 200):
                return blocked
            out.append({
                "id": item["id"], "official_url": url, "sha256": digest,
                "bytes": size, "observed_utc": item["observed_utc"],
                "source_record_count_verified": None,
                "first_public_at_verified": False,
                "official_bytes_preserved_in_git": False,
            })
        try:
            aggregate = _metadata_only(aggregate_path if aggregate_path is not None else AGGREGATE)
        except (OSError, ValueError, TypeError, KeyError, AttributeError):
            aggregate = {}
        for record in out:
            filename = record["official_url"].rsplit("/", 1)[-1]
            record["metadata_audit"] = aggregate.get(filename, {
                "coverage_status": "AGGREGATE_UNAVAILABLE_OR_UNREVIEWED",
            })
        return {
            "ok": True, "status": "TWO_SPANISH_OFFICIAL_SOURCES_CAPTURED",
            "manifest_class": "CAPTURE_METADATA_NOT_SOURCE_CERTIFICATION",
            "publisher": "Ministerio del Interior", "distribution_count": 2,
            "official_catalogue": doc["official_catalogue"],
            "licence_reference": doc["catalogue_licence_ref"],
            "source_data": out, "source_corpus_admitted": False,
            "source_aggregate_metadata_reproduced": len(aggregate) == 2,
            "metadata_rows_scanned": sum(r["rows_in_document"] for r in aggregate.values()),
            "congress_initiative_population_verified": False,
            "first_public_at_verified": False,
            "real_person_scoring": False,
            "interpretation": "Source bytes captured outside Git; identities, field schemas, historical dates and Congress initiatives remain unvalidated.",
        }
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return blocked
