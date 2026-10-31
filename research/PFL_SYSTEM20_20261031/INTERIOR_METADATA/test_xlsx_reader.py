"""Fully synthetic tests for standard-library XLSX archive/worksheet handling."""

from contextlib import ExitStack, redirect_stdout
from datetime import datetime
from io import BytesIO, StringIO
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile, ZIP_DEFLATED

import xlsx_reader as x


CONTENT = b'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>'
WORKBOOK = b'''<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Ficticia" sheetId="1" r:id="rId1"/></sheets></workbook>'''
RELS = b'''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'''
SHARED = b'''<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>ANO</t></si><si><r><t>COD_</t></r><r><t>AMBITO</t></r></si><si><t>RegionSynthetic</t></si></sst>'''
SHEET = b'''<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><dimension ref="A1:D4"/><sheetData>
<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c><c r="C1" t="inlineStr"><is><t>FLAG</t></is></c><c r="D1" t="str"><v>NOTES</v></c></row>
<row r="2"><c r="A2"><v>1977</v></c><c r="B2" t="s"><v>2</v></c><c r="C2" t="b"><v>1</v></c><c r="D2" t="e"><v>#REF!</v></c></row>
<row r="3"><c r="A3"><v>1982</v></c><c r="B3" t="s"><v>2</v></c><c r="C3" t="b"><v>0</v></c><c r="D3"><f>1+1</f><v>2</v></c></row>
<row r="4"><c r="A4"/><c r="B4" t="inlineStr"><is><t>Other</t></is></c></row>
</sheetData></worksheet>'''


def create_archive(*, sheet=SHEET, shared=SHARED, additional=None, workbook=WORKBOOK, rels=RELS) -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as package:
        files = {"[Content_Types].xml": CONTENT, "xl/workbook.xml": workbook,
                 "xl/_rels/workbook.xml.rels": rels, "xl/worksheets/sheet1.xml": sheet,
                 "xl/sharedStrings.xml": shared}
        files.update(additional or {})
        for name, content in files.items():
            package.writestr(name, content)
    return buffer.getvalue()


class SafeReaderTests(unittest.TestCase):
    def with_book(self, raw, callback):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "synthetic.xlsx"
            file.write_bytes(raw)
            with x.GuardedBook(file) as book:
                return callback(book)

    def test_package_headers_and_shared_strings(self):
        def inspect(b):
            self.assertEqual(b.sheets()[0]["name"], "Ficticia")
            sheet = b.sheets()[0]["sheet_member"]
            self.assertEqual(x.find_dimension(b, sheet), "A1:D4")
            return x.read_header(b, sheet)
        header = self.with_book(create_archive(), inspect)
        self.assertEqual([c["header"] for c in header["header_cells"]], ["ANO", "COD_AMBITO", "FLAG", "NOTES"])
        self.assertEqual([c["column"] for c in header["header_cells"]], ["A", "B", "C", "D"])
        self.assertEqual(header["header_row"], 1)

    def test_selected_cells_preserve_types_and_skip_other_values(self):
        def inspect(book):
            member = book.sheets()[0]["sheet_member"]
            rows = list(x.iter_rows(book, member, chosen={1, 3, 4}))
            return rows
        rows = self.with_book(create_archive(), inspect)
        self.assertEqual(rows[1][1][1], ("number", 1977))
        self.assertEqual(rows[1][1][3], ("boolean", True))
        self.assertEqual(rows[1][1][4], ("error", None))
        self.assertEqual(rows[2][1][4], ("formula", None))
        self.assertNotIn(2, rows[1][1])

    def test_shared_string_selectivity(self):
        self.assertEqual(self.with_book(create_archive(), lambda b: x.shared_values(b, {2})), {2: "RegionSynthetic"})
        with self.assertRaisesRegex(ValueError, "UNRESOLVED_SHARED_STRINGS"):
            self.with_book(create_archive(), lambda b: x.shared_values(b, {99}))

    def test_xml_doctype_blocked(self):
        bad = b'<!DOCTYPE worksheet [ <!ENTITY x "evil"> ]>' + SHEET
        with self.assertRaisesRegex(ValueError, "DTD_OR_ENTITY_FORBIDDEN"):
            self.with_book(create_archive(sheet=bad), lambda b: list(x.iter_rows(b, b.sheets()[0]["sheet_member"])))

    def test_zip_path_escape_and_duplicates(self):
        with self.assertRaisesRegex(ValueError, "UNSAFE_ZIP_MEMBER"):
            self.with_book(create_archive(additional={"../secret.xml": b"fake"}), lambda b: b.sheets())

    def test_zip_bomb_ratio_rejected(self):
        with self.assertRaisesRegex(ValueError, "ZIP_BOMB_LIMIT"):
            self.with_book(create_archive(additional={"xl/huge.xml": b"A" * 400_000}), lambda b: b.sheets())

    def test_missing_sheet_relationship_rejected(self):
        bad = RELS.replace(b"worksheets/sheet1.xml", b"worksheets/doesnotexist.xml")
        with self.assertRaisesRegex(ValueError, "SHEET_RELATIONSHIP_UNRESOLVED"):
            self.with_book(create_archive(rels=bad), lambda b: b.sheets())

    def test_duplicate_cell_in_row_rejected(self):
        bad = SHEET.replace(b'<c r="A2"><v>1977</v></c>', b'<c r="A2"><v>1977</v></c><c r="A2"><v>1982</v></c>')
        with self.assertRaisesRegex(ValueError, "DUPLICATE_CELL_IN_ROW"):
            self.with_book(create_archive(sheet=bad), lambda b: list(x.iter_rows(b, b.sheets()[0]["sheet_member"])))

    def test_bad_shared_index_and_boolean_rejected(self):
        invalid = SHEET.replace(b'<v>0</v></c><c r="B1"', b'<v>not-an-index</v></c><c r="B1"')
        with self.assertRaisesRegex(ValueError, "INVALID_SHARED_STRING_INDEX"):
            self.with_book(create_archive(sheet=invalid), lambda b: x.read_header(b, b.sheets()[0]["sheet_member"]))
        invalid = SHEET.replace(b'<c r="C2" t="b"><v>1</v></c>', b'<c r="C2" t="b"><v>77</v></c>')
        with self.assertRaisesRegex(ValueError, "INVALID_BOOLEAN_CELL"):
            self.with_book(create_archive(sheet=invalid), lambda b: list(x.iter_rows(b, b.sheets()[0]["sheet_member"])))

    def test_date_year_extraction_and_unsafe_columns(self):
        self.assertEqual(x.extract_year(1977), "1977")
        self.assertEqual(x.extract_year("23/07/2023"), "2023")
        self.assertEqual(x.extract_year("2023-07-23"), "2023")
        self.assertIsNone(x.extract_year("2027"))
        self.assertIsNone(x.extract_year(True))
        excel_1900_serial = (datetime(2023, 7, 23) - datetime(1899, 12, 30)).days
        excel_1904_serial = (datetime(2023, 7, 23) - datetime(1904, 1, 1)).days
        self.assertEqual(x.extract_year(excel_1900_serial, allow_excel_serial=True), "2023")
        self.assertEqual(x.extract_year(excel_1904_serial, allow_excel_serial=True, date_system_1904=True), "2023")
        self.assertIsNone(x.extract_year(excel_1900_serial, allow_excel_serial=False))
        self.assertTrue(x.column_is_safe("CÓDIGO PROVINCIA"))
        for field in ("VOTOS", "Escaños", "Nombre del candidato", "Resultados", "Partido", "Censo"):
            self.assertFalse(x.column_is_safe(field), field)

    def test_hash_digest_replay_and_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "a.xlsx"
            file.write_bytes(create_archive())
            import hashlib
            digest = hashlib.sha256(file.read_bytes()).hexdigest()
            self.assertEqual(x.sha_file(file), digest)
            self.assertEqual(x.inspect_file(file, digest)["worksheets"][0]["header_cells"][0]["header"], "ANO")
            with self.assertRaisesRegex(ValueError, "MANIFEST_SHA256_MISMATCH"):
                x.inspect_file(file, "0" * 64)

    def test_header_only_never_scans_second_row(self):
        bad_second = SHEET.replace(b'<c r="C2" t="b"><v>1</v></c>', b'<c r="C2" t="b"><v>99</v></c>')
        header = self.with_book(create_archive(sheet=bad_second), lambda b: x.read_header(b, b.sheets()[0]["sheet_member"]))
        self.assertEqual(len(header["header_cells"]), 4)

    def test_titled_sheet_real_headers_selected_from_row_four(self):
        top = b'''<row r="1"/><row r="2"><c r="A2" t="inlineStr"><is><t>Fictional election</t></is></c></row><row r="3"><c r="A3" t="inlineStr"><is><t>Subtitle</t></is></c></row>'''
        titled = SHEET.replace(b'<row r="1">', top + b'<row r="4">', 1)
        titled = titled.replace(b'r="A1"', b'r="A4"').replace(b'r="B1"', b'r="B4"').replace(b'r="C1"', b'r="C4"').replace(b'r="D1"', b'r="D4"')
        # Row 4 is deliberately followed by a malformed data row. Only the
        # header can be inspected without touching outcome-like data cells.
        titled = titled.replace(b'<row r="2"><c r="A2"><v>1977</v></c>', b'<row r="5"><c r="A5"><v>1977</v></c>')
        titled = titled.replace(b'r="B2"', b'r="B5"').replace(b'r="C2"', b'r="C5"').replace(b'r="D2"', b'r="D5"')
        titled = titled.replace(b'<row r="3"><c r="A3"><v>1982</v></c>', b'<row r="6"><c r="A6"><v>1982</v></c>')
        titled = titled.replace(b'r="B3"', b'r="B6"').replace(b'r="C3"', b'r="C6"').replace(b'r="D3"', b'r="D6"')
        titled = titled.replace(b'<row r="4"><c r="A4"/>', b'<row r="7"><c r="A7"/>').replace(b'r="B4" t="inlineStr"', b'r="B7" t="inlineStr"')
        titled = titled.replace(b'<c r="C5" t="b"><v>1</v></c>', b'<c r="C5" t="b"><v>999</v></c>')
        def inspect(book):
            sheet = book.sheets()[0]["sheet_member"]
            header = x.read_header(book, sheet)
            return header["header_row"], len(header["header_cells"])
        self.assertEqual(self.with_book(create_archive(sheet=titled), inspect), (4, 4))

    def test_phase2_fixture_aggregate_without_outcomes_or_person_rows(self):
        appended = SHEET.replace(b'</sheetData>', b'<row r="5"><c r="A5"><v>1977</v></c><c r="B5" t="s"><v>2</v></c></row></sheetData>')
        sample = create_archive(sheet=appended)
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            sources = base / "source"
            runs = base / "runs"
            sources.mkdir()
            runs.mkdir()
            files = ("Elecciones-Congreso-cargos-electos.xlsx", "Elecciones-Congreso.xlsx")
            entries = []
            outputs = []
            for name in files:
                path = sources / name
                path.write_bytes(sample)
                digest = hashlib.sha256(sample).hexdigest()
                entries.append({"filename": name, "byte_length": len(sample), "sha256": digest})
                outputs.append(x.inspect_file(path, digest))
            manifest = base / "manifest.json"
            manifest.write_text(json.dumps({
                "catalogue_licence_ref": "http://publications.europa.eu/resource/authority/licence/CC_BY_4_0",
                "distribution": entries,
            }), encoding="utf-8")
            phase1 = {
                "manifest_sha256": x.sha_file(manifest),
                "outputs": outputs,
            }
            (runs / "phase1_final.json").write_text(json.dumps(phase1), encoding="utf-8")
            code_hashes = {"xlsx_reader.py": "fictional_sha_1", "test_xlsx_reader.py": "fictional_sha_2"}
            (runs / "frozen_code.json").write_text(json.dumps({
                "phase1_sha256": x.sha_file(runs / "phase1_final.json"), "code_sha256": code_hashes,
            }), encoding="utf-8")
            (base / "metadata_policy.json").write_text(json.dumps({
                "schema": "INTERIOR_METADATA_ONLY_V1",
                "sources": {name: {"sheet": "Ficticia", "columns": ["A", "B"], "year": "A", "dedup_key": ["A", "B"]} for name in files},
            }), encoding="utf-8")
            with ExitStack() as stack:
                for attr, obj in (("ROOT", base), ("SOURCE_ROOT", sources), ("RUN", runs), ("MANIFEST", manifest)):
                    stack.enter_context(patch.object(x, attr, obj))
                stack.enter_context(patch.object(x, "freeze_hashes", return_value=code_hashes))
                with redirect_stdout(StringIO()):
                    x.phase2()
            aggregate = json.loads((runs / "phase2.json").read_text(encoding="utf-8"))
            self.assertEqual(len(aggregate["outputs"]), 2)
            for result in aggregate["outputs"]:
                self.assertEqual(result["rows_scanned"], 4)
                self.assertEqual(result["valid_year_rows"], 3)
                self.assertEqual(result["invalid_or_missing_year_rows"], 1)
                self.assertEqual(result["year_counts"], {"1977": 2, "1982": 1})
                self.assertEqual(result["metadata_key_collision_rows"], 1)
                self.assertEqual(result["metadata_key_missing_rows"], 1)
                self.assertEqual(result["missingness_counts"], {"A": 1})
                self.assertFalse(result["person_rows_or_outcome_values_exported"])


if __name__ == "__main__":
    unittest.main()
