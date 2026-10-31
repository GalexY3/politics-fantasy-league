"""Verify a pair of previously captured public Spanish XLSX source blobs.

No network, spreadsheet row parsing or source redistribution. Byte replay
is not an authentication, licensing, person-identity or coverage certificate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit
from zipfile import ZipFile, BadZipFile


EXPECTED_BASE = "https://descargas.interior.gob.es/datasets/resultados_electorales/"
MAX_BYTES = 25_000_000
MAX_UNCOMPRESSED = 150_000_000
HASH = re.compile(r"[0-9a-f]{64}\Z")


class SourceReplayError(ValueError):
    pass


def verify_one(directory: Path, source: dict) -> dict:
    name = source.get("filename")
    if not isinstance(name, str) or name not in {
        "Elecciones-Congreso.xlsx",
        "Elecciones-Congreso-cargos-electos.xlsx",
    }:
        raise SourceReplayError("NOT_WHITELISTED_FILENAME")
    url = source.get("official_url")
    if not isinstance(url, str) or url != EXPECTED_BASE + name:
        raise SourceReplayError("UNEXPECTED_SOURCE_URI")
    expected_hash = source.get("sha256")
    if not isinstance(expected_hash, str) or HASH.fullmatch(expected_hash) is None:
        raise SourceReplayError("INVALID_DECLARED_SHA256")
    expected_size = source.get("byte_length")
    if not isinstance(expected_size, int) or not 0 < expected_size <= MAX_BYTES:
        raise SourceReplayError("BAD_DECLARED_SIZE")
    original = directory / name
    if original.is_symlink():
        raise SourceReplayError("SYMLINK_ORIGINAL_NOT_ALLOWED")
    if not original.is_file() or original.stat().st_size != expected_size:
        raise SourceReplayError("ORIGINAL_MISSING_OR_LENGTH_DIFFERS")
    digest = hashlib.sha256()
    with original.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != expected_hash:
        raise SourceReplayError("ORIGINAL_SHA256_MISMATCH")
    try:
        with ZipFile(original) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(set(names)) != len(names):
                raise SourceReplayError("DUPLICATE_ZIP_MEMBERS")
            if sum(i.file_size for i in infos) > MAX_UNCOMPRESSED:
                raise SourceReplayError("ZIP_BOMB_TOO_LARGE")
            for item in names:
                parts = PurePosixPath(item).parts
                if not item or item.startswith("/") or "\\" in item or ".." in parts:
                    raise SourceReplayError("UNSAFE_ARCHIVE_MEMBER")
            if not {"[Content_Types].xml", "_rels/.rels", "xl/workbook.xml"}.issubset(names):
                raise SourceReplayError("NOT_VALID_OOXML_WORKBOOK")
            if not any(p.startswith("xl/worksheets/sheet") and p.endswith(".xml") for p in names):
                raise SourceReplayError("MISSING_WORKSHEET_PART")
            if archive.testzip() is not None:
                raise SourceReplayError("BROKEN_ARCHIVE_CRC")
            worksheet_parts = sum(p.startswith("xl/worksheets/sheet") and p.endswith(".xml") for p in names)
    except BadZipFile as exc:
        raise SourceReplayError("NOT_A_ZIP_FILE") from exc
    return {
        "distribution": source["id"], "file": name, "sha256": expected_hash,
        "bytes": expected_size, "worksheet_parts": worksheet_parts,
        "status": "SOURCE_BYTES_REPLAYED_AND_OOXML_STRUCTURE_VALID",
        "rows_analyzed": False, "identity_linkage_verified": False,
        "first_public_at_verified": False, "rights_of_individual_fields_adjudicated": False,
    }


def replay(directory: Path, manifest_path: Path) -> dict:
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    if document.get("schema") != "pfl.source_capture_manifest.v1":
        raise SourceReplayError("MANIFEST_SCHEMA_UNKNOWN")
    items = document.get("distribution")
    if not isinstance(items, list) or len(items) != 2 or len({i.get("id") for i in items}) != 2:
        raise SourceReplayError("MANIFEST_DISTRIBUTIONS_INCORRECT")
    if {i["filename"] for i in items} != {"Elecciones-Congreso.xlsx", "Elecciones-Congreso-cargos-electos.xlsx"}:
        raise SourceReplayError("MISSING_DISTRIBUTION")
    results = [verify_one(directory, i) for i in items]
    return {
        "status": "TWO_LOCAL_ORIGINAL_BYTE_REPLAYS_PASS",
        "originals": results, "source_admissibility_science": "NOT_YET_ADJUDICATED",
        "ab_cycles_charged": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--originals-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=Path("data/source_manifests/interior_congreso_20261031.json"))
    args = parser.parse_args()
    print(json.dumps(replay(args.originals_dir, args.manifest), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
