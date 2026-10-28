"""Conservative read-only historical Congreso member projection.

Source rows are institutional observations, not legal RPP identity, proof of
uninterrupted mandate, currently active service, personal traits, or scores.
Never serve biographies or arbitrary fields from upstream official JSON.
"""
from __future__ import annotations

from datetime import date, datetime
import json
import re
from urllib.parse import urlsplit

SOURCE_URL = ("https://www.congreso.es/webpublica/opendata/diputados/"
              "DiputadosActivos__20260725050010.json")
SOURCE_FILENAME_DATE = "2026-07-25"  # URL filename only; not a certified publication timestamp.
ROW_KEYS = frozenset(("NOMBRE", "CIRCUNSCRIPCION", "FORMACIONELECTORAL",
                      "GRUPOPARLAMENTARIO", "FECHAALTA", "FECHACONDICIONPLENA",
                      "FECHAALTAENGRUPOPARLAMENTARIO"))
URL_PATTERN = re.compile(r"^/webpublica/opendata/diputados/"
                         r"DiputadosActivos__\d{14}\.json$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class SourceContractError(ValueError):
    pass


def _official_url(url: str) -> bool:
    try:
        p = urlsplit(url)
        return (p.scheme == "https" and p.hostname == "www.congreso.es" and
                p.port in (None, 443) and not p.username and not p.password and
                not p.query and not p.fragment and bool(URL_PATTERN.fullmatch(p.path)))
    except ValueError:
        return False


def _date(value: object) -> str | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise SourceContractError("DATE_NOT_STRING")
    try:
        return datetime.strptime(value, "%d/%m/%Y").date().isoformat()
    except ValueError as exc:
        raise SourceContractError("INVALID_DATE") from exc


def _unique_json_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise SourceContractError("DUPLICATE_JSON_MEMBER")
        result[key] = value
    return result


def project(raw: bytes, *, url: str = SOURCE_URL, max_rows: int = 5) -> dict:
    if not _official_url(url):
        raise SourceContractError("NOT_EXACT_OFFICIAL_HOST_OR_PATH")
    if not isinstance(raw, bytes) or not 2 <= len(raw) <= 10_000_000:
        raise SourceContractError("SOURCE_BYTES_UNSAFE")
    if not isinstance(max_rows, int) or isinstance(max_rows, bool) or not 1 <= max_rows <= 1000:
        raise SourceContractError("INVALID_BOUNDED_SAMPLE")
    try:
        rows = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_json_pairs)
    except SourceContractError:
        raise
    except (UnicodeError, ValueError) as exc:
        raise SourceContractError("BAD_JSON") from exc
    if not isinstance(rows, list) or not rows or len(rows) > 10000:
        raise SourceContractError("NOT_NONEMPTY_ARRAY")
    output = []
    for i, row in enumerate(rows[:max_rows]):
        if not isinstance(row, dict) or not ROW_KEYS.issubset(row):
            raise SourceContractError("MISSING_REQUIRED_PUBLIC_FIELDS")
        for k in ("NOMBRE", "CIRCUNSCRIPCION", "FORMACIONELECTORAL", "GRUPOPARLAMENTARIO"):
            if not isinstance(row[k], str) or not row[k].strip() or len(row[k]) > 300:
                raise SourceContractError("INVALID_OFFICIAL_FIELD")
        dates = {k: _date(row[k]) for k in
                 ("FECHAALTA", "FECHACONDICIONPLENA", "FECHAALTAENGRUPOPARLAMENTARIO")}
        output.append({
            "snapshot_row_id": f"CONGRESO_XV_SNAPSHOT_20260725_ROW_{i+1:04d}",
            "display_name_from_official": row["NOMBRE"],
            "constituency_from_official": row["CIRCUNSCRIPCION"],
            "electoral_label_not_legal_party_id": row["FORMACIONELECTORAL"],
            "parliamentary_group_not_party_membership": row["GRUPOPARLAMENTARIO"],
            "admission_date_from_official": dates["FECHAALTA"],
            "full_condition_date_from_official": dates["FECHACONDICIONPLENA"],
            "group_joined_date_from_official": dates["FECHAALTAENGRUPOPARLAMENTARIO"],
            "first_public_at": None,
            "end_of_mandate": None,
            "continuous_membership_confirmed": False,
            "eligible_for_real_scoring": False,
        })
    return {
        "dataset_class": "OFFICIAL_HISTORICAL_EXTRACT_BOUNDED",
        "source_url": url,
        "source_filename_date": SOURCE_FILENAME_DATE,
        "source_date_is_publisher_certified": False,
        "rows_in_original_response": len(rows),
        "rows_in_bounded_projection": len(output),
        "projection_sampling_rule": f"first_{max_rows}_rows_in_original_source_order",
        "rpp_id_verified": False,
        "status_as_of_october_2026": "UNKNOWN_NOT_INFERRED",
        "score_real_people": False,
        "people": output,
        "limitations": ("Historical July 2026 filename; no present-day mandate/party identity "
                        "inferred, no biography, no predictive/fantasy score."),
    }
