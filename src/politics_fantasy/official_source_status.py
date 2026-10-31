"""Public aggregate publication metadata for the Spanish research observatory.

Reading this manifest does NOT read originals from the private local raw lake
or admit individual identities, historical completeness, legal rights or scoring.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[2] / "data/source_manifests/interior_congreso_20261031.json"
IDS = {"INTERIOR_CONGRESO_ELECTED", "INTERIOR_CONGRESO_RESULTS"}
HASH = re.compile(r"[0-9a-f]{64}\Z")
URL_PREFIX = "https://descargas.interior.gob.es/datasets/resultados_electorales/"


def published_sources(path: Path | None = None) -> dict:
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
        return {
            "ok": True, "status": "TWO_SPANISH_OFFICIAL_SOURCES_CAPTURED",
            "manifest_class": "CAPTURE_METADATA_NOT_SOURCE_CERTIFICATION",
            "publisher": "Ministerio del Interior", "distribution_count": 2,
            "official_catalogue": doc["official_catalogue"],
            "licence_reference": doc["catalogue_licence_ref"],
            "source_data": out, "source_corpus_admitted": False,
            "congress_initiative_population_verified": False,
            "first_public_at_verified": False,
            "real_person_scoring": False,
            "interpretation": "Source bytes captured outside Git; identities, field schemas, historical dates and Congress initiatives remain unvalidated.",
        }
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return blocked
