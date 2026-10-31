"""Read-only R8 institutional discovery with two SHA-pinned documentary matrices.

Six regional parliamentary leads and ten NATIONAL documentary assets are
heterogeneous descriptions: they are not 16 registrations, datasets, or
independent censuses. No direct source original has been captured in R8.
Snapshots dated only to a calendar day become visible no earlier than the
following UTC midnight. Never expose this manifest as historical public data.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit

from .procedural_index_contract import utc

ROOT = Path(__file__).resolve().parents[2]
REGIONAL = ROOT / "data/source_manifests/r8_regional_documentary_matrix_20261031.json"
NATIONAL = ROOT / "data/source_manifests/r8_national_documentary_matrix_20261031.json"
REGIONAL_SHA = "fbc6f74cb522295dc551b86d64caeec470bd9d65b11a36c4719f0919ee8daa8a"
NATIONAL_SHA = "c400427e0fb753496016500ff5411618f27e186f5ab5f14278d862691d841ec3"
SAFE_BY = datetime(2026, 11, 1, tzinfo=timezone.utc)
REGIONS = {
    "Illes Balears", "Principado de Asturias", "Cantabria",
    "Extremadura", "Región de Murcia", "La Rioja",
}
SELECT_NATIONAL = {
    "CE_ANNUAL_MEMORIES_INDEX", "CE_MEMORY_2024_PDF_INDEXED",
    "BOE_CE_DICTAMENS_SEARCH_FORM",
}
ALLOWED_HOSTS = {
    "web.parlamentib.es", "seu.parlamentib.es", "www.parlamentib.es",
    "www.jgpa.es", "parlamento-cantabria.es", "www.boe.es",
    "www.senado.es", "www.asambleamurcia.es", "sede.asambleamurcia.es",
    "boe.es", "transparencia.carm.es", "www.parlamento-larioja.org",
    "www.consejo-estado.es",
}


def _unique_json(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("DUPLICATE_DOCUMENTARY_JSON_KEY")
        obj[key] = value
    return obj


def _load(path: Path, pin: str, expected_low: int, expected_high: int):
    if (path.is_symlink() or not path.is_file()
            or not expected_low <= path.stat().st_size <= expected_high):
        raise ValueError("BAD_DOCUMENTARY_MANIFEST_FILE")
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != pin:
        raise ValueError("R8_PINNED_SOURCE_MATRIX_SHA_MISMATCH")
    return json.loads(
        raw.decode("utf8"), object_pairs_hook=_unique_json,
        parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")),
    )


def _safe_https(uri: str) -> bool:
    if not isinstance(uri, str) or len(uri) > 1500:
        return False
    try:
        p = urlsplit(uri)
        return (p.scheme == "https" and p.hostname in ALLOWED_HOSTS
                and not p.username and not p.password and not p.port
                and not p.fragment)
    except ValueError:
        return False


def _check_regional(obj):
    if (type(obj) != dict
            or obj.get("schema") != "PFL_R8_OFFICIAL_REGIONAL_SOURCE_EVIDENCE_MATRIX_V1"
            or obj.get("as_of") != "2026-10-31"
            or type(obj.get("real_direct_gets")) is not int or obj["real_direct_gets"] != 0
            or obj.get("raw_originals_sha256_available") is not False
            or obj.get("historical_first_public_at") is not None
            or obj.get("verified_complete_population_candidates") != 0):
        raise ValueError("R8_REGIONAL_SCIENTIFIC_PROMOTION")
    sources = obj.get("sources")
    if type(sources) is not list or len(sources) != 6:
        raise ValueError("R8_REGIONAL_COUNT_DRIFT")
    regions = set()
    output = []
    for x in sources:
        if type(x) != dict or x.get("region") not in REGIONS or x["region"] in regions:
            raise ValueError("R8_REGIONAL_UNKNOWN_SOURCE")
        regions.add(x["region"])
        if (x.get("exact_distribution_url") is not None
                or x.get("exact_distribution_license_url") is not None
                or x.get("licence_for_bulk_registry_proven") is not False
                or x.get("full_received_before_mesa") is not False
                or x.get("covers_nonadmitted_pre_mesa_verified") is not False
                or x.get("independent_total") is not None
                or x.get("publisher_total_for_full_register") is not None
                or x.get("direct_get_count") != 0
                or x.get("raw_sha256") is not None
                or x.get("first_public_at") is not None
                or x.get("http_status") is not None):
            raise ValueError("R8_REGIONAL_UNATTESTED_PROMOTION")
        urls = x.get("primary_urls")
        if type(urls) is not list or not 1 <= len(urls) <= 6 or not all(map(_safe_https, urls)):
            raise ValueError("R8_REGIONAL_UNSAFE_ORIGIN")
        for key in ("parliament","documented_system","coverage_limitation","privacy_or_access"):
            if not isinstance(x.get(key), str) or not 0 < len(x[key]) <= 1500:
                raise ValueError("R8_REGIONAL_INVALID_DOCUMENTARY_DESCRIPTION")
        output.append({
            "institution": x["parliament"], "region": x["region"],
            "asset": x["documented_system"],
            "limitation": x["coverage_limitation"],
            "rights": "NO_SOURCE_SPECIFIC_BULK_ENTRY_REGISTER_LICENSE_ATTESTED",
            "evidence_grade": "PUBLIC_DOCUMENTARY_DESCRIPTION_NO_RAW_ORIGINAL",
            "scientifically_admitted": False,
        })
    return output


def _check_national(obj):
    if (type(obj) != dict
            or obj.get("schema") != "pfl.r8.council_state_documentary_matrix.v1"
            or obj.get("audit_day_utc") != "2026-10-31"
            or obj.get("original_downloads") != 0
            or obj.get("local_original_GET") != 0
            or obj.get("local_original_HEAD") != 0
            or obj.get("consents_or_terms_accepted") != 0
            or obj.get("source_outcomes_extracted") != 0
            or obj.get("AB_cycles_consumed") != 0
            or obj.get("trusted_registrar_present") is not False):
        raise ValueError("R8_NATIONAL_SCIENTIFIC_PROMOTION")
    records = obj.get("source_records")
    if type(records) is not list or len(records) != 10:
        raise ValueError("R8_NATIONAL_DOCUMENT_COUNT_DRIFT")
    seen, output = set(), []
    for x in records:
        if type(x) != dict or not isinstance(x.get("id"), str) or x["id"] in seen:
            raise ValueError("R8_NATIONAL_SOURCE_ID_DRIFT")
        seen.add(x["id"])
        if (not _safe_https(x.get("url"))
                or x.get("actual_original_SHA256") is not None
                or x.get("first_public_at") is not None
                or x.get("denominator_all_congress_pre_mesa") is not False
                or x.get("historical_versions_replayed") is not False
                or x.get("raw_original_opened") is not False):
            raise ValueError("R8_NATIONAL_UNATTESTED_PROMOTION")
        if x["id"] in SELECT_NATIONAL:
            output.append({
                "asset": x["id"], "institution": x.get("publisher"),
                "unit": x.get("grain"), "limitation": x.get("limitation"),
                "rights": x.get("permission_status"),
                "evidence_grade": "DOCUMENT_INDEX_ONLY_NO_REPLAYED_ORIGINAL",
                "scientifically_admitted": False,
            })
    if len(output) != len(SELECT_NATIONAL):
        raise ValueError("R8_NATIONAL_CORE_ROUTES_MISSING")
    return output


def status(*, as_of: str | None = None, regional_path: Path | None = None,
           national_path: Path | None = None) -> dict:
    t = utc(as_of) if as_of is not None else None
    base = {
        "schema": "pfl.procedural_r8_documentary_status.v1",
        "as_of": as_of,
        "scientific_cohort_added": False,
        "independent_all_received_denominator": None,
        "source_originals_admitted": 0,
        "real_event_outcomes_admitted": 0,
        "ABH_cycles_executed": 0,
        "first_public_at": None,
    }
    if t is not None and t < SAFE_BY:
        return {**base, "status": "R8_NOT_KNOWN_AT_CUT",
                "regional_routes": [], "national_core_routes": [],
                "regional_source_count": None, "national_documentary_assets_count": None,
                "local_audit_safe_by": None, "source_matrix_sha256": None}
    try:
        regional = _check_regional(_load(regional_path or REGIONAL, REGIONAL_SHA, 3000, 40000))
        national = _check_national(_load(national_path or NATIONAL, NATIONAL_SHA, 3000, 40000))
    except (OSError, TypeError, ValueError, KeyError, AttributeError):
        return {**base, "status": "R8_DOCUMENTARY_MANIFEST_QUARANTINED",
                "regional_routes": [], "national_core_routes": [],
                "regional_source_count": None, "national_documentary_assets_count": None,
                "local_audit_safe_by": None, "source_matrix_sha256": None}
    return {**base, "status": "R8_DOCUMENTARY_ONLY_NO_SOURCE_ADMISSION",
            "regional_routes": regional, "national_core_routes": national,
            "regional_source_count": 6, "national_documentary_assets_count": 10,
            "national_core_displayed": len(national),
            "local_audit_safe_by": SAFE_BY.isoformat(),
            "source_matrix_sha256": {
                "regional": REGIONAL_SHA, "national": NATIONAL_SHA,
            },
            "interpretation": ("Regional registry interfaces have selection and/or rights gates. "
                               "Council of State annual consultations are a separate institutional "
                               "unit; dispatched matters and approved dictamens are not entries. "
                               "No original captured, denominators independently certified, "
                               "historical revision vintages, or outcomes admitted.")}
