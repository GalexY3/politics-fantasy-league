"""No-network adversarial tests for the one-shot PE/2025 capture instrument."""
from __future__ import annotations

from email.message import Message
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import capture_pe_2025 as instrument


class Response:
    status = 200
    def __init__(self, data: bytes, *, url: str = instrument.CANONICAL,
                 mime: str = "text/csv"):
        self.data, self.url = data, url
        self.headers = Message()
        self.headers["Content-Type"] = mime
        self.headers["Date"] = "Sat, 31 Oct 2026 06:00:00 GMT"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def geturl(self):
        return self.url

    def read(self, size):
        return self.data[:size]


class Opener:
    def __init__(self, answer):
        self.answer = answer
        self.calls = []

    def open(self, request, timeout):
        self.calls.append((request.full_url, timeout))
        if isinstance(self.answer, BaseException):
            raise self.answer
        return self.answer


class Capture2025Tests(unittest.TestCase):
    def test_destination_must_be_new_outside_git_and_inside_approved_root(self):
        for bad in (instrument.REPO, instrument.REPO / "data" / "raw",
                    instrument.APPROVED_ROOT.parent / "another"):
            with self.assertRaises(ValueError):
                instrument.checked_destination(bad)
        with tempfile.TemporaryDirectory(dir=instrument.APPROVED_ROOT) as tmp:
            with self.assertRaises(ValueError):
                instrument.checked_destination(Path(tmp))
            self.assertEqual(instrument.checked_destination(Path(tmp) / "new"),
                             Path(tmp) / "new")

    def test_reject_bad_mime_html_empty_and_oversize(self):
        self.assertTrue(instrument.content_ok(b"a,b\n1,2\n", "text/csv; charset=utf-8"))
        self.assertFalse(instrument.content_ok(b"<html>oops", "text/csv"))
        self.assertFalse(instrument.content_ok(b"<!DOCTYPE html>", "text/csv"))
        self.assertFalse(instrument.content_ok(b"a,b\n", "text/html"))
        self.assertFalse(instrument.content_ok(b"", "text/csv"))
        self.assertFalse(instrument.content_ok(b"z" * (instrument.MAX_BYTES+1), "text/csv"))

    def test_one_success_writes_original_and_receipt_with_no_population_claim(self):
        synthetic = b"ID_INICIATIVA,LEGISLATURA\nfake,11\n"
        opener = Opener(Response(synthetic))
        with tempfile.TemporaryDirectory(dir=instrument.APPROVED_ROOT) as tmp:
            dest = Path(tmp) / "capture"
            with patch.object(instrument, "build_opener", return_value=opener):
                result = instrument.capture_once(dest)
            self.assertEqual(result["http_status"], 200)
            self.assertEqual(len(opener.calls), 1)
            self.assertEqual(opener.calls[0][0], instrument.CANONICAL)
            self.assertEqual((dest / instrument.FILENAME).read_bytes(), synthetic)
            r = json.loads((dest / "capture_receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(r["raw_sha256"], sha256(synthetic).hexdigest())
            self.assertIsNone(r["first_public_at"])
            self.assertFalse(r["publisher_population_total_verified"])
            self.assertFalse(r["interactive_terms_accepted"])
            with self.assertRaises(ValueError):
                instrument.capture_once(dest)

    def test_forbidden_redirect_cannot_silently_download(self):
        opener = Opener(Response(b"a,b\n", url="https://other.example/file.csv"))
        with tempfile.TemporaryDirectory(dir=instrument.APPROVED_ROOT) as tmp:
            dest = Path(tmp) / "capture"
            with patch.object(instrument, "build_opener", return_value=opener):
                result = instrument.capture_once(dest)
            self.assertEqual(result["state"], "CAPTURE_FAILED_NO_RETRY")
            self.assertFalse((dest / instrument.FILENAME).exists())
            self.assertEqual(len(opener.calls), 1)

    def test_403_quarantines_and_does_not_retry(self):
        error = HTTPError(instrument.CANONICAL, 403, "Forbidden", {}, None)
        opener = Opener(error)
        try:
            with tempfile.TemporaryDirectory(dir=instrument.APPROVED_ROOT) as tmp:
                dest = Path(tmp) / "capture"
                with patch.object(instrument, "build_opener", return_value=opener):
                    result = instrument.capture_once(dest)
                self.assertEqual(result["state"], "HTTP_BLOCKED_NO_RETRY")
                self.assertEqual(result["http_status"], 403)
                self.assertEqual(len(opener.calls), 1)
                self.assertFalse((dest / instrument.FILENAME).exists())
        finally:
            error.close()


if __name__ == "__main__":
    unittest.main()
