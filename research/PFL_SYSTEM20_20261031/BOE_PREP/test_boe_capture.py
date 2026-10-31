"""Network-free synthetic tests for an archival BOE-A link extractor."""

from __future__ import annotations

from email.message import Message
from io import BytesIO
from pathlib import Path
import unittest
from unittest.mock import patch

import boe_capture as boe


class ExtractionTests(unittest.TestCase):
    def extract(self, markup: str) -> dict[str, object]:
        return boe.extract_links(markup.encode("utf-8"))

    def test_synthetic_fixture_counts_and_duplicate_audit(self) -> None:
        raw = (Path(__file__).parent / "fixtures" / "synthetic_day.html").read_bytes()
        result = boe.extract_links(raw)
        self.assertEqual([row["id"] for row in result["ids"]], ["BOE-A-2026-901234", "BOE-A-2026-901235"])
        metrics = result["metrics"]
        self.assertEqual(metrics["unique_ids"], 2)
        self.assertEqual(metrics["unique_id_link_pairs"], 3)
        self.assertEqual(metrics["id_link_occurrences"], 4)
        self.assertEqual(metrics["duplicate_id_link_occurrences"], 1)
        self.assertEqual(metrics["ids_with_multiple_links"], ["BOE-A-2026-901234"])
        self.assertEqual(metrics["anchors_rejected_multiple_identifiers"], 1)
        self.assertEqual(metrics["anchors_rejected_external_or_non_https"], 1)

    def test_plain_text_is_not_a_record(self) -> None:
        result = self.extract("<p>BOE-A-2026-1234</p><a href='#footnote'>Nota</a>")
        self.assertEqual(result["ids"], [])

    def test_external_javascript_and_insecure_links_rejected(self) -> None:
        sample = (
            '<a href="https://other.example/BOE-A-2026-1234.pdf">externo</a>'
            '<a href="http://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-1235">inseguro</a>'
            '<a href="javascript:alert(1)">script</a>'
        )
        result = self.extract(sample)
        self.assertEqual(result["ids"], [])
        self.assertEqual(result["metrics"]["anchors_rejected_external_or_non_https"], 3)

    def test_identifier_must_be_exact_in_id_query(self) -> None:
        sample = (
            '<a href="/diario_boe/txt.php?id=BOE-A-2026-1234-junk">bad</a>'
            '<a href="/diario_boe/txt.php?reference=BOE-A-2026-1234">irrelevant key</a>'
            '<a href="/diario_boe/txt.php?ID=BOE-A-2026-1234">valid</a>'
        )
        result = self.extract(sample)
        self.assertEqual([item["id"] for item in result["ids"]], ["BOE-A-2026-1234"])
        self.assertEqual(result["metrics"]["unique_id_link_pairs"], 1)

    def test_url_escaped_ampersand_and_fragment_do_not_duplicate(self) -> None:
        sample = (
            '<a href="/diario_boe/txt.php?id=BOE-A-2026-1234&amp;foo=bar#section">one</a>'
            '<a href="/diario_boe/txt.php?id=BOE-A-2026-1234&amp;foo=bar">two</a>'
        )
        result = self.extract(sample)
        self.assertEqual(result["metrics"]["unique_id_link_pairs"], 1)
        self.assertEqual(result["metrics"]["duplicate_id_link_occurrences"], 1)

    def test_multiple_identifiers_in_one_link_discarded(self) -> None:
        result = self.extract('<a href="/pdf/BOE-A-2026-1111.pdf?id=BOE-A-2026-2222">ambiguous</a>')
        self.assertEqual(result["ids"], [])
        self.assertEqual(result["metrics"]["anchors_rejected_multiple_identifiers"], 1)

    def test_cross_year_id_is_reported_not_silently_discarded(self) -> None:
        result = self.extract('<a href="/diario_boe/txt.php?id=BOE-A-2025-321">archived link</a>')
        self.assertEqual(result["metrics"]["ids_year_different_from_edition"], ["BOE-A-2025-321"])

    def test_exact_raw_hash_is_independent_of_html_decoding(self) -> None:
        raw = b'<a href="/diario_boe/txt.php?id=BOE-A-2026-5">\xff</a>'
        self.assertEqual(boe.extract_links(raw)["metrics"]["unique_ids"], 1)
        import hashlib
        self.assertEqual(hashlib.sha256(raw).hexdigest(), hashlib.sha256(bytes(raw)).hexdigest())

    def test_real_get_is_blocked_before_network_layer(self) -> None:
        self.assertFalse(boe.LIVE_FETCH_AUTHORIZED)
        with patch.object(boe, "build_opener", side_effect=AssertionError("network should not be called")) as network:
            with self.assertRaises(PermissionError):
                boe.get_one_page()
            network.assert_not_called()

    def test_provenance_headers_in_fully_mocked_http_adapter(self) -> None:
        """No socket exists here: opener and response are Python test doubles."""
        class FakeResponse:
            status = 200

            def __init__(self):
                self.headers = Message()
                self.headers["Content-Type"] = "text/html; charset=utf-8"
                self.headers["Date"] = "Fri, 30 Oct 2026 12:00:00 GMT"
                self.body = BytesIO(b'<a href="/diario_boe/txt.php?id=BOE-A-2026-9876">X</a>')

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                self.body.close()

            def geturl(self):
                return boe.SOURCE_URL

            def read(self, count):
                return self.body.read(count)

        with patch.object(boe, "LIVE_FETCH_AUTHORIZED", True), patch.object(boe, "build_opener") as opener:
            opener.return_value.open.return_value = FakeResponse()
            data, info = boe.get_one_page()
            opener.assert_called_once()
            opener.return_value.open.assert_called_once()
        self.assertEqual(info["http_status"], 200)
        self.assertEqual(info["http_date"], "Fri, 30 Oct 2026 12:00:00 GMT")
        self.assertEqual(boe.extract_links(data)["metrics"]["unique_ids"], 1)

    def test_real_archiver_also_blocks_without_authorization(self) -> None:
        with self.assertRaises(PermissionError):
            boe.archive_real_capture(b"<html></html>", {"http_status": 200, "effective_url": boe.SOURCE_URL})


if __name__ == "__main__":
    unittest.main()
