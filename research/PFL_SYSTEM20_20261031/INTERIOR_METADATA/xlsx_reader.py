"""Read-only, ZIP/XML XLSX inspector for an isolated Interior research audit.

Only Python standard library. No spreadsheet libraries, HTTP, person-level exports,
political outcomes, or writes outside the adjacent scratch ``runs`` folder.
Phase 1 inspects package metadata and a header row only. Phase 2 uses frozen
code plus an explicitly scoped metadata-column policy for aggregated diagnostics.
"""

from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
import sys
from typing import Iterator
from xml.etree import ElementTree as ET
from zipfile import ZipFile, BadZipFile, ZIP_STORED, ZIP_DEFLATED


ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT.parent / "PFL-raw-primary" / "interior_20261031"
MANIFEST = ROOT.parent / "PFL-trabajo" / "data" / "source_manifests" / "interior_congreso_20261031.json"
RUN = ROOT / "runs" / "2026-10-31"
M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
P = "{http://schemas.openxmlformats.org/package/2006/relationships}"
MAX_ARCHIVE_BYTES = 8_000_000
MAX_ENTRIES = 100
MAX_MEMBER_BYTES = 35_000_000
MAX_TOTAL_UNCOMPRESSED = 64_000_000
MAX_RATIO = 200
MAX_SHARED_ENTRY_LENGTH = 100_000
MAX_SHARED_ENTRIES = 200_000
MAX_ROWS = 400_000
MAX_COLS = 400
MAX_CELLS_PER_ROW = 600
MAX_HEADER_CHARS = 250
SHA256_HEX = re.compile(r"[0-9a-f]{64}\Z")
CELL_REF = re.compile(r"([A-Z]{1,3})([1-9][0-9]*)\Z")
COL_REF = re.compile(r"[A-Z]{1,3}\Z")
SENSITIVE = ("VOTO", "ESCA", "SEAT", "WINNER", "GANAD", "RESULT", "VALIDOS", "CANDIDAT", "ELECTO", "APELLID", "NOMBRE", "DNI", "NIF", "SEXO", "EDAD", "PERSON", "PARTIDO", "SIGLA", "LISTA", "CARGO", "PUESTO", "DIPUTAD", "PORCENTAJE", "PCT", "ABSTENC", "BLANC", "NULO", "CENSO", "ESCRUT")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1_048_576):
            h.update(chunk)
    return h.hexdigest()


def new_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as out:
        json.dump(data, out, sort_keys=True, ensure_ascii=False, indent=2)
        out.write("\n")


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def number_to_col(index: int) -> str:
    if index < 1 or index > 16384:
        raise ValueError("COLUMN_OUT_OF_RANGE")
    parts = []
    while index:
        index, mod = divmod(index - 1, 26)
        parts.append(chr(65 + mod))
    return "".join(reversed(parts))


def col_to_number(label: str) -> int:
    if not COL_REF.fullmatch(label):
        raise ValueError("INVALID_COLUMN_REF")
    idx = 0
    for char in label:
        idx = idx * 26 + ord(char) - 64
    if idx > 16384:
        raise ValueError("COLUMN_OUT_OF_RANGE")
    return idx


class BoundedReader:
    """Bound bytes emitted by decompression and reject DTD in XML prolog."""

    def __init__(self, reader, limit: int):
        self.reader = reader
        self.limit = limit
        self.total = 0
        self.prefix = b""

    def read(self, n: int = -1) -> bytes:
        n = self.limit - self.total + 1 if n is None or n < 0 else min(n, self.limit - self.total + 1)
        data = self.reader.read(n)
        self.total += len(data)
        if self.total > self.limit:
            raise ValueError("DECOMPRESSED_MEMBER_OVER_LIMIT")
        if len(self.prefix) < 4096:
            self.prefix += data[: 4096 - len(self.prefix)]
            if b"<!DOCTYPE" in self.prefix.upper() or b"<!ENTITY" in self.prefix.upper():
                raise ValueError("DTD_OR_ENTITY_FORBIDDEN")
        return data


class GuardedBook:
    def __init__(self, path: Path):
        self.path = path
        self.z: ZipFile | None = None
        self.names: set[str] = set()
        self.member_metadata: dict[str, dict] = {}

    def __enter__(self):
        if not self.path.is_file() or self.path.stat().st_size > MAX_ARCHIVE_BYTES:
            raise ValueError("MISSING_OR_OVERSIZE_XLSX")
        try:
            self.z = ZipFile(self.path)
            infos = self.z.infolist()
            if not (3 <= len(infos) <= MAX_ENTRIES):
                raise ValueError("UNSAFE_ZIP_ENTRY_COUNT")
            total = 0
            casefold = set()
            for info in infos:
                name = info.filename
                pure = PurePosixPath(name)
                if (name.startswith("/") or "\\" in name or ".." in pure.parts
                        or not name or name.endswith("/") or name in self.names
                        or name.casefold() in casefold or info.flag_bits & 1
                        or info.compress_type not in {ZIP_STORED, ZIP_DEFLATED}
                        or (info.external_attr >> 16) & 0o170000 == 0o120000):
                    raise ValueError("UNSAFE_ZIP_MEMBER")
                casefold.add(name.casefold())
                self.names.add(name)
                total += info.file_size
                if (info.file_size > MAX_MEMBER_BYTES or total > MAX_TOTAL_UNCOMPRESSED
                        or info.file_size > max(1, info.compress_size) * MAX_RATIO):
                    raise ValueError("ZIP_BOMB_LIMIT")
                self.member_metadata[name] = {"compressed_bytes": info.compress_size, "uncompressed_bytes": info.file_size}
            if not {"[Content_Types].xml", "xl/workbook.xml", "xl/_rels/workbook.xml.rels"} <= self.names:
                raise ValueError("NOT_STANDARD_XLSX_PACKAGE")
            if any(name.endswith("vbaProject.bin") for name in self.names):
                raise ValueError("MACROS_NOT_ALLOWED")
            return self
        except (BadZipFile, OSError, RuntimeError):
            if self.z is not None:
                self.z.close()
            raise ValueError("INVALID_ZIP_ARCHIVE") from None
        except Exception:
            if self.z is not None:
                self.z.close()
            raise

    def __exit__(self, *_):
        if self.z is not None:
            self.z.close()

    @contextmanager
    def open_xml(self, name: str):
        if self.z is None or name not in self.names or not name.endswith((".xml", ".rels")):
            raise ValueError("MISSING_OR_INVALID_XML_MEMBER")
        with self.z.open(name) as stream:
            yield BoundedReader(stream, MAX_MEMBER_BYTES)

    def small_xml(self, name: str, limit: int = 1_000_000):
        if self.member_metadata[name]["uncompressed_bytes"] > limit:
            raise ValueError("OVERSIZE_METADATA_XML")
        with self.open_xml(name) as stream:
            return ET.fromstring(stream.read(limit + 1))

    def sheets(self) -> list[dict]:
        workbook = self.small_xml("xl/workbook.xml")
        relationships = self.small_xml("xl/_rels/workbook.xml.rels")
        mapping = {}
        for rel in relationships.findall(f"{P}Relationship"):
            if rel.get("TargetMode") == "External":
                continue
            target = rel.get("Target", "")
            if target.startswith("/"):
                path = target.lstrip("/")
            else:
                path = posixpath.normpath(posixpath.join("xl", target))
            if not path.startswith("xl/worksheets/") or path not in self.names:
                continue
            mapping[rel.get("Id")] = path
        found = []
        for item in workbook.findall(f"{M}sheets/{M}sheet"):
            rid = item.get(f"{REL}id")
            if rid not in mapping:
                raise ValueError("SHEET_RELATIONSHIP_UNRESOLVED")
            found.append({"name": item.get("name"), "sheet_member": mapping[rid], "sheet_state": item.get("state", "visible")})
        if not found:
            raise ValueError("NO_WORKSHEETS")
        return found

    def date_system_1904(self) -> bool:
        workbook = self.small_xml("xl/workbook.xml")
        prop = workbook.find(f"{M}workbookPr")
        raw = prop.get("date1904", "0").lower() if prop is not None else "0"
        if raw not in ("0", "1", "true", "false"):
            raise ValueError("UNKNOWN_WORKBOOK_DATE_SYSTEM")
        return raw in ("1", "true")


def parse_cell(cell) -> tuple[str, str | int | float | bool | None]:
    """Preserve type; never execute formulae; reject bad shared indices."""
    kind = cell.get("t", "n")
    if kind not in ("n", "s", "inlineStr", "str", "b", "e", "d"):
        raise ValueError("UNKNOWN_CELL_TYPE")
    v = cell.find(f"{M}v")
    formula = cell.find(f"{M}f")
    if formula is not None:
        # Never trust cached formula values for documentary provenance.
        return ("formula", None)
    if kind == "inlineStr":
        inline = cell.find(f"{M}is")
        return ("text", "".join(t.text or "" for t in inline.iter(f"{M}t")) if inline is not None else "")
    raw = v.text if v is not None else None
    if raw is None:
        return ("blank", None)
    if kind == "s":
        if not raw.isdigit():
            raise ValueError("INVALID_SHARED_STRING_INDEX")
        idx = int(raw)
        if idx >= MAX_SHARED_ENTRIES:
            raise ValueError("SHARED_STRING_INDEX_TOO_LARGE")
        return ("shared", idx)
    if kind == "b":
        if raw not in ("0", "1"):
            raise ValueError("INVALID_BOOLEAN_CELL")
        return ("boolean", raw == "1")
    if kind == "e":
        return ("error", None)
    if kind == "d":
        return ("date_text", raw)
    if kind == "str":
        return ("text", raw)
    try:
        number = float(raw)
        if not __import__("math").isfinite(number):
            raise ValueError("NONFINITE_NUMERIC_CELL")
        return ("number", int(number) if number.is_integer() else number)
    except (ValueError, OverflowError) as exc:
        raise ValueError("INVALID_NUMERIC_CELL") from exc


def iter_rows(book: GuardedBook, sheet_member: str, *, chosen: set[int] | None = None, max_rows: int = MAX_ROWS) -> Iterator[tuple[int, dict[int, tuple]]]:
    """Streaming XML: skip values of all unchosen cells, discard every row."""
    with book.open_xml(sheet_member) as stream:
        events = ET.iterparse(stream, events=("start", "end"))
        root = None
        last_number = 0
        count = 0
        for event, node in events:
            if root is None and event == "start":
                root = node
            if event != "end" or node.tag != f"{M}row":
                continue
            count += 1
            if count > max_rows:
                raise ValueError("ROW_LIMIT")
            value = node.get("r")
            row_number = int(value) if value and value.isdecimal() else last_number + 1
            if row_number <= last_number:
                raise ValueError("OUT_OF_ORDER_ROWS")
            last_number = row_number
            selected: dict[int, tuple] = {}
            seen = set()
            col_fallback = 0
            for c in node.findall(f"{M}c"):
                ref = c.get("r")
                match = CELL_REF.fullmatch(ref) if ref else None
                col = col_to_number(match.group(1)) if match else col_fallback + 1
                col_fallback = col
                if col in seen:
                    raise ValueError("DUPLICATE_CELL_IN_ROW")
                seen.add(col)
                if len(seen) > MAX_CELLS_PER_ROW:
                    raise ValueError("ROW_CELL_LIMIT")
                if chosen is None or col in chosen:
                    selected[col] = parse_cell(c)
            yield (row_number, selected)
            if root is not None:
                root.clear()


def find_dimension(book: GuardedBook, sheet_member: str) -> str | None:
    with book.open_xml(sheet_member) as stream:
        for event, node in ET.iterparse(stream, events=("start",)):
            if node.tag == f"{M}dimension":
                return node.get("ref")
            if node.tag == f"{M}sheetData":
                return None
    return None


def header_row_shapes(book: GuardedBook, sheet_member: str, *, limit: int = 25) -> list[dict]:
    """Inspect cell coordinates only, never their values, in top structural rows."""
    shapes = []
    with book.open_xml(sheet_member) as stream:
        context = ET.iterparse(stream, events=("start", "end"))
        root = None
        for event, node in context:
            if root is None and event == "start":
                root = node
            if event == "end" and node.tag == f"{M}row":
                cells = node.findall(f"{M}c")
                coords = [c.get("r", "") for c in cells]
                shapes.append({"row": int(node.get("r", str(len(shapes) + 1))), "cells_present": len(cells),
                               "first_cell": coords[0] if coords else None, "last_cell": coords[-1] if coords else None})
                if root is not None:
                    root.clear()
                if len(shapes) >= limit:
                    break
    return shapes


def shared_values(book: GuardedBook, wanted: set[int]) -> dict[int, str]:
    if not wanted:
        return {}
    path = "xl/sharedStrings.xml"
    if path not in book.names:
        raise ValueError("SHARED_STRINGS_MISSING")
    found = {}
    index = 0
    with book.open_xml(path) as stream:
        events = ET.iterparse(stream, events=("start", "end"))
        root = None
        for event, node in events:
            if root is None and event == "start":
                root = node
            if event == "end" and node.tag == f"{M}si":
                if index in wanted:
                    string = "".join(t.text or "" for t in node.iter(f"{M}t"))
                    if len(string) > MAX_SHARED_ENTRY_LENGTH:
                        raise ValueError("SHARED_ENTRY_EXCEEDS_LIMIT")
                    found[index] = string
                    if len(found) == len(wanted):
                        break
                index += 1
                if index >= MAX_SHARED_ENTRIES:
                    raise ValueError("SHARED_ENTRIES_LIMIT")
                if root is not None:
                    root.clear()
    if set(found) != wanted:
        raise ValueError("UNRESOLVED_SHARED_STRINGS")
    return found


def convert_cell(pair: tuple, shared: dict[int, str]) -> object:
    kind, data = pair
    return shared[data] if kind == "shared" else data


def read_header(book: GuardedBook, sheet: str) -> dict:
    # The initial decorated title rows are not column headers. Identify a
    # dense row using coordinates only; inspect values in that row alone.
    shapes = header_row_shapes(book, sheet, limit=25)
    candidates = [r["row"] for r in shapes if 4 <= r["cells_present"] <= MAX_COLS]
    if not candidates:
        raise ValueError("NO_DENSE_HEADER_ROW_IN_FIRST_25_ROWS")
    candidate = candidates[0]
    first = next(((row, cells) for row, cells in iter_rows(book, sheet, max_rows=25) if row == candidate), None)
    if first is None:
        raise ValueError("UNABLE_TO_READ_DENSE_HEADER_ROW")
    header_row, cells = first
    wanted = {value for kind, value in cells.values() if kind == "shared"}
    pool = shared_values(book, wanted)
    headers = []
    for index, cell in sorted(cells.items()):
        if index > MAX_COLS:
            raise ValueError("HEADER_COLUMN_LIMIT")
        value = convert_cell(cell, pool)
        text = "" if value is None else str(value)
        if len(text) > MAX_HEADER_CHARS:
            raise ValueError("HEADER_TOO_LONG")
        headers.append({"column": number_to_col(index), "index": index, "header": text, "cell_type": cell[0]})
    return {"header_row": header_row, "header_cells": headers, "header_row_selection": "first_row_with_4_or_more_cells_in_first_25", "structural_row_shapes": shapes}


def inspect_file(path: Path, expected_sha: str) -> dict:
    actual = sha_file(path)
    if not SHA256_HEX.fullmatch(expected_sha) or actual != expected_sha:
        raise ValueError("MANIFEST_SHA256_MISMATCH")
    with GuardedBook(path) as book:
        sheets = []
        for sheet in book.sheets():
            xml = sheet["sheet_member"]
            sheets.append({**sheet, "zip_sizes": book.member_metadata[xml], "declared_dimension": find_dimension(book, xml), **read_header(book, xml)})
        return {
            "filename": path.name, "original_sha256_verified": True, "original_sha256": actual,
            "original_bytes": path.stat().st_size, "zip_entries": len(book.names),
            "uncompressed_total_bytes_declared": sum(v["uncompressed_bytes"] for v in book.member_metadata.values()),
            "workbook_date_system_1904": book.date_system_1904(),
            "worksheets": sheets,
            "inspected_only_headers_dimensions_zip_metadata": True,
            "worksheet_data_cells_read_in_phase1": False,
        }


def manifest_sources():
    meta = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if meta.get("catalogue_licence_ref") != "http://publications.europa.eu/resource/authority/licence/CC_BY_4_0":
        raise ValueError("MANIFEST_LICENCE_EXPECTATION_MISMATCH")
    files = meta["distribution"]
    if len(files) != 2 or len({f["filename"] for f in files}) != 2:
        raise ValueError("MANIFEST_DISTRIBUTION_COUNT_MISMATCH")
    for source in files:
        if source["filename"] not in ("Elecciones-Congreso.xlsx", "Elecciones-Congreso-cargos-electos.xlsx"):
            raise ValueError("UNEXPECTED_SOURCE_FILENAME")
        file = SOURCE_ROOT / source["filename"]
        if file.stat().st_size != source["byte_length"]:
            raise ValueError("MANIFEST_ORIGINAL_SIZE_MISMATCH")
    return meta, files


def freeze_hashes() -> dict:
    names = ("xlsx_reader.py", "test_xlsx_reader.py")
    return {name: sha_file(ROOT / name) for name in names}


def phase1() -> int:
    RUN.mkdir(parents=True, exist_ok=True)
    report_path = RUN / "phase1_final.json"
    if report_path.exists():
        raise ValueError("PHASE1_ALREADY_EXECUTED")
    source_manifest, distributions = manifest_sources()
    scanned = [inspect_file(SOURCE_ROOT / entry["filename"], entry["sha256"]) for entry in distributions]
    report = {
        "phase": "PHASE1_HEADERS_ONLY", "executed_utc": utc_now(),
        "manifest_path": str(MANIFEST), "manifest_sha256": sha_file(MANIFEST),
        "source_captured_on": source_manifest["captured_on"],
        "source_catalogue_licence": source_manifest["catalogue_licence_ref"],
        "source_first_public_at": source_manifest["first_public_at"],
        "latest_http_last_modified_is_first_publication": False,
        "outputs": scanned,
        "outcomes_read": False, "no_person_rows_exported": True,
    }
    new_json(report_path, report)
    print(json.dumps({"phase": report["phase"], "files": [{"filename": item["filename"], "sheets": len(item["worksheets"]), "sha256": item["original_sha256"], "headers": item["worksheets"][0]["header_cells"]} for item in scanned]}, ensure_ascii=False, indent=2))
    return 0


def phase2():
    # An explicit policy is generated only after reviewing the actual headers.
    if not (RUN / "phase1_final.json").exists() or not (RUN / "frozen_code.json").exists():
        raise ValueError("PHASE1_AND_FROZEN_CODE_REQUIRED")
    freeze = json.loads((RUN / "frozen_code.json").read_text(encoding="utf-8"))
    if freeze.get("code_sha256") != freeze_hashes():
        raise ValueError("CODE_CHANGED_SINCE_FREEZE")
    policy_file = ROOT / "metadata_policy.json"
    policy = json.loads(policy_file.read_text(encoding="utf-8"))
    if policy.get("schema") != "INTERIOR_METADATA_ONLY_V1":
        raise ValueError("METADATA_POLICY_INVALID")
    source_meta, distributions = manifest_sources()
    phase1_report = json.loads((RUN / "phase1_final.json").read_text(encoding="utf-8"))
    if (sha_file(RUN / "phase1_final.json") != freeze.get("phase1_sha256")
            or sha_file(MANIFEST) != phase1_report["manifest_sha256"]):
        raise ValueError("SOURCE_OR_PHASE1_CHANGED_SINCE_FREEZE")
    outputs = []
    for source in distributions:
        filename = source["filename"]
        if sha_file(SOURCE_ROOT / filename) != source["sha256"]:
            raise ValueError("ORIGINAL_CHANGED_SINCE_MANIFEST")
        item = next(x for x in phase1_report["outputs"] if x["filename"] == filename)
        config = policy["sources"].get(filename)
        if config is None:
            outputs.append({"filename": filename, "status": "NOT_ELIGIBLE_FOR_PHASE2_NO_METADATA_SELECTION"})
            continue
        sheetname = config.get("sheet")
        chosen_names = config.get("columns")
        year_name = config.get("year")
        key_names = config.get("dedup_key")
        if (not isinstance(chosen_names, list) or len(chosen_names) > 10 or not chosen_names
                or len(chosen_names) != len(set(chosen_names)) or year_name not in chosen_names
                or not isinstance(key_names, list)
                or any(k not in chosen_names for k in key_names)):
            raise ValueError("INVALID_METADATA_SELECTION")
        sheet = next((s for s in item["worksheets"] if s["name"] == sheetname), None)
        if sheet is None:
            raise ValueError("POLICY_UNKNOWN_SHEET")
        headers = sheet["header_cells"]
        header_cols = [h["column"] for h in headers]
        if len(header_cols) != len(set(header_cols)):
            raise ValueError("DUPLICATE_HEADER_COLUMNS")
        header_lookup = {h["column"]: h["header"] for h in headers}
        for name in chosen_names:
            if name not in header_cols or not column_is_safe(header_lookup[name]):
                raise ValueError("OUTCOME_OR_PERSON_METADATA_COLUMN_FORBIDDEN")
        lookup = {h["column"]: h["index"] for h in headers}
        selected = {lookup[name] for name in chosen_names}
        with GuardedBook(SOURCE_ROOT / filename) as book:
            # First stream reads only approved metadata cells and their shared indices.
            wanted = set()
            for number, cells in iter_rows(book, sheet["sheet_member"], chosen=selected):
                if number <= sheet["header_row"]:
                    continue
                wanted.update(value for kind, value in cells.values() if kind == "shared")
            shared = shared_values(book, wanted)
            year_counts = Counter()
            missing = Counter()
            valid_year_rows = 0
            metadata_key_duplicates = 0
            metadata_key_missing = 0
            years_invalid = 0
            sampled = 0
            key_hashes = set()
            for number, cells in iter_rows(book, sheet["sheet_member"], chosen=selected):
                if number <= sheet["header_row"]:
                    continue
                sampled += 1
                if sampled > MAX_ROWS:
                    raise ValueError("PHASE2_ROW_LIMIT")
                values = {name: convert_cell(cells[lookup[name]], shared) if lookup[name] in cells else None for name in chosen_names}
                for name, value in values.items():
                    if value is None or isinstance(value, str) and not value.strip():
                        missing[name] += 1
                year = extract_year(values[year_name], allow_excel_serial=header_lookup[year_name].casefold() == "fecha", date_system_1904=item["workbook_date_system_1904"])
                if year is not None:
                    valid_year_rows += 1
                    year_counts[year] += 1
                else:
                    years_invalid += 1
                key_values = [values[name] for name in key_names]
                if not key_names:
                    pass
                elif any(value is None or isinstance(value, str) and not value.strip() for value in key_values):
                    metadata_key_missing += 1
                else:
                    # Do not emit keys or raw values. This is diagnostic collision
                    # counting only, NOT proof of duplicate electoral observations.
                    key = hashlib.sha256(json.dumps(key_values, ensure_ascii=False, sort_keys=True).encode("utf-8")).digest()
                    if key in key_hashes:
                        metadata_key_duplicates += 1
                    else:
                        key_hashes.add(key)
            outputs.append({
                "filename": filename, "sheet": sheetname,
                "status": "AGGREGATE_EXPLORATORY_ONLY", "rows_scanned": sampled,
                "valid_year_rows": valid_year_rows, "invalid_or_missing_year_rows": years_invalid,
                "year_counts": dict(sorted(year_counts.items())),
                "missingness_counts": dict(sorted(missing.items())),
                "metadata_key_names": key_names,
                "metadata_key_collision_rows": metadata_key_duplicates,
                "metadata_key_missing_rows": metadata_key_missing,
                "metadata_key_unique_nonmissing": len(key_hashes),
                "duplicate_claim": "NONE: collisions in selected non-person metadata are not duplicated original rows" if key_names else "NOT_TESTABLE: no safe natural key among selected metadata",
                "metadata_columns_by_letter": {name: header_lookup[name] for name in chosen_names},
                "person_rows_or_outcome_values_exported": False,
            })
    report = {
        "phase": "PHASE2_AGGREGATE_NON_OUTCOME", "executed_utc": utc_now(),
        "policy_sha256": sha_file(policy_file), "frozen_code_sha256": freeze["code_sha256"],
        "original_manifest_sha256": sha_file(MANIFEST),
        "raw_originals_recaptured": False, "download_requests": 0,
        "source_first_public_at": None, "licence_ref": source_meta["catalogue_licence_ref"],
        "outputs": outputs, "causal_or_abh_conclusions": False,
    }
    new_json(RUN / "phase2.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


def column_is_safe(header: str) -> bool:
    from unicodedata import normalize
    clean = "".join(c for c in normalize("NFKD", header.upper()) if ord(c) < 128)
    return bool(clean.strip()) and not any(fragment in clean for fragment in SENSITIVE)


def extract_year(value: object, *, allow_excel_serial: bool = False, date_system_1904: bool = False) -> str | None:
    if type(value) is int and 1970 <= value <= 2026:
        return str(value)
    if allow_excel_serial and type(value) in (int, float) and 25_000 <= value <= 50_000:
        origin = datetime(1904, 1, 1) if date_system_1904 else datetime(1899, 12, 30)
        parsed = origin + timedelta(days=float(value))
        return str(parsed.year) if 1970 <= parsed.year <= 2026 else None
    if isinstance(value, str):
        text = value.strip()
        if re.fullmatch(r"(?:19[789][0-9]|20[012][0-9])", text) and 1970 <= int(text) <= 2026:
            return text
        try:
            for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
                try:
                    parsed = datetime.strptime(text, fmt)
                    if 1970 <= parsed.year <= 2026:
                        return str(parsed.year)
                except ValueError:
                    continue
        except ValueError:
            return None
    return None


def freeze() -> None:
    if not (RUN / "phase1_final.json").exists():
        raise ValueError("PHASE1_REQUIRED_BEFORE_FREEZE")
    result = subprocess.run([sys.executable, "-m", "unittest", "-v", "test_xlsx_reader.py"],
                            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, timeout=30, check=False)
    test_log = result.stdout
    if result.returncode != 0:
        raise ValueError("TESTS_FAILED_FREEZE_REJECTED")
    new_json(RUN / "tests_receipt.json", {
        "executed_utc": utc_now(), "command": "python -m unittest -v test_xlsx_reader.py",
        "exit_code": result.returncode, "test_log_sha256": hashlib.sha256(test_log.encode("utf-8")).hexdigest(),
        "tests_passed": True,
    })
    new_json(RUN / "frozen_code.json", {
        "freeze_utc": utc_now(), "code_sha256": freeze_hashes(),
        "phase1_sha256": sha_file(RUN / "phase1_final.json"),
        "test_command": "python -m unittest -v test_xlsx_reader.py", "tests_passed": True,
        "test_log_sha256": hashlib.sha256(test_log.encode("utf-8")).hexdigest(),
    })


if __name__ == "__main__":
    if sys.argv[1:] == ["phase1"]:
        sys.exit(phase1())
    if sys.argv[1:] == ["freeze"]:
        freeze()
        sys.exit(0)
    if sys.argv[1:] == ["phase2"]:
        phase2()
        sys.exit(0)
    print("Usage: python xlsx_reader.py phase1|freeze|phase2", file=sys.stderr)
    sys.exit(2)
