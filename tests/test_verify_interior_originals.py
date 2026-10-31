"""Synthetic fail-closed tests; source originals are never committed."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from scripts.verify_interior_originals import (
    SourceReplayError, replay, verify_one, EXPECTED_BASE
)


class InteriorSourceByteReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.name = "Elecciones-Congreso.xlsx"
        self.original = self.directory / self.name
        with ZipFile(self.original, "w") as a:
            a.writestr("[Content_Types].xml", "<Types/>")
            a.writestr("_rels/.rels", "<Relationships/>")
            a.writestr("xl/workbook.xml", "<workbook/>")
            a.writestr("xl/worksheets/sheet1.xml", "<worksheet/>")
        import hashlib
        self.item = {
            "id": "TEST", "filename": self.name,
            "official_url": EXPECTED_BASE + self.name,
            "sha256": hashlib.sha256(self.original.read_bytes()).hexdigest(),
            "byte_length": self.original.stat().st_size,
        }

    def test_known_bytes_pass_structure_but_not_corpus_admission(self):
        status = verify_one(self.directory, self.item)
        self.assertEqual(status["worksheet_parts"], 1)
        self.assertFalse(status["rows_analyzed"])
        self.assertFalse(status["first_public_at_verified"])

    def test_reject_tampering(self):
        self.original.write_bytes(self.original.read_bytes() + b"tampering")
        with self.assertRaisesRegex(SourceReplayError, "ORIGINAL_"):
            verify_one(self.directory, self.item)

    def test_reject_wrong_source(self):
        self.item["official_url"] = "https://another.example/Elecciones-Congreso.xlsx"
        with self.assertRaisesRegex(SourceReplayError, "UNEXPECTED_SOURCE_URI"):
            verify_one(self.directory, self.item)

    def test_reject_path_traversal(self):
        self.item["filename"] = "../../other.xlsx"
        with self.assertRaisesRegex(SourceReplayError, "NOT_WHITELISTED"):
            verify_one(self.directory, self.item)

    def test_reject_no_workbook_parts(self):
        with ZipFile(self.original, "w") as a:
            a.writestr("hello.txt", "fake")
        import hashlib
        self.item["sha256"] = hashlib.sha256(self.original.read_bytes()).hexdigest()
        self.item["byte_length"] = self.original.stat().st_size
        with self.assertRaisesRegex(SourceReplayError, "NOT_VALID_OOXML"):
            verify_one(self.directory, self.item)

    def test_bad_manifest_does_not_validate(self):
        manifest = self.directory / "manifest.json"
        manifest.write_text(json.dumps({"schema": "pfl.source_capture_manifest.v1", "distribution": [self.item]}))
        with self.assertRaisesRegex(SourceReplayError, "MANIFEST_DISTRIBUTIONS_INCORRECT"):
            replay(self.directory, manifest)


if __name__ == "__main__":
    unittest.main()
