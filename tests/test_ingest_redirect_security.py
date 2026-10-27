"""Offline urllib redirect and source-host security, no external network."""
import io
import json
import tempfile
import unittest
from email.message import Message
from pathlib import Path
from unittest.mock import patch
from urllib.request import HTTPSHandler, build_opener

from politics_fantasy import ingest


class Response:
    status = 200
    code = 200
    msg = "OK"
    headers = {"Content-Type": "application/json"}
    def __init__(self, url, content=b'{"fake":true}'):
        self.url, self.content = url, content
        self.read_count = 0
    def __enter__(self): return self
    def __exit__(self, *args): return None
    def close(self): return None
    def geturl(self): return self.url
    def info(self): return self.headers
    def read(self, n=-1):
        self.read_count += 1
        return self.content if n == -1 else self.content[:n]


class OfflineHTTPS(HTTPSHandler):
    def __init__(self, moves):
        super().__init__()
        self.moves = moves
        self.contacted = []
    def https_open(self, req):
        url = req.full_url
        self.contacted.append(url)
        if url not in self.moves:
            raise AssertionError("UNEXPECTED_NETWORK_TARGET: " + url)
        action = self.moves[url]
        if isinstance(action, str):
            headers = Message()
            headers["Location"] = action
            # Actual urllib redirect machinery is invoked here. Target HTTPS
            # handler must NOT be called until SourceScopedRedirects approves.
            return self.parent.error("https", req, Response(url), 302, "Found", headers)
        return Response(url, action)


class IngestRedirectSecurity(unittest.TestCase):
    START = "https://www.congreso.es/start"
    def run_offline(self, moves, *, source="congreso"):
        transport = OfflineHTTPS(moves)
        def factory(guard):
            return build_opener(guard, transport)
        with tempfile.TemporaryDirectory() as td:
            with patch.object(ingest, "build_opener", side_effect=factory):
                with patch.object(ingest.time, "sleep", return_value=None):
                    try:
                        result = ingest.import_url(url=self.START, source=source, root=Path(td), min_interval=1)
                        saved = (Path(td)/result["raw_object"]).read_bytes()
                        return transport.contacted, result, saved
                    except Exception as exc:
                        return transport.contacted, exc, list(Path(td).rglob("manifest.jsonl"))

    def test_mismatch_source_host_before_any_contact(self):
        calls, out, _ = self.run_offline({self.START: b"ok"}, source="senado")
        self.assertEqual(calls, [])
        self.assertIsInstance(out, ValueError)

    def test_offsite_redirect_denied_before_contact(self):
        evil = "https://evil.invalid/collect"
        calls, out, manifests = self.run_offline({self.START:evil})
        self.assertEqual(calls, [self.START])
        self.assertIsInstance(out, ValueError)
        self.assertEqual(manifests, [])

    def test_cross_official_publisher_denied(self):
        target = "https://www.senado.es/from-congreso"
        calls, out, _ = self.run_offline({self.START: target})
        self.assertEqual(calls, [self.START])
        self.assertIsInstance(out, ValueError)

    def test_downgrade_and_private_ipv4_denied(self):
        for destination in ["http://www.congreso.es/next",
                            "https://127.0.0.1/next",
                            "https://www.congreso.es:444/next",
                            "https://www.congreso.es.evil.invalid/next"]:
            with self.subTest(destination=destination):
                calls, out, _ = self.run_offline({self.START: destination})
                self.assertEqual(calls, [self.START])
                self.assertIsInstance(out, ValueError)

    def test_same_source_https_redirect_allowed_with_full_chain(self):
        final = "https://www.congreso.es/end"
        calls, record, saved = self.run_offline({self.START: final, final: b'{"ok":1}'})
        self.assertEqual(calls, [self.START, final])
        self.assertEqual(saved, b'{"ok":1}')
        self.assertEqual(record["source_id"], "congreso")
        self.assertEqual(record["redirect_chain"], [self.START, final])
        self.assertTrue(record["redirect_chain_checked_before_contact"])
        self.assertIsNone(record["first_public_at"])
        self.assertFalse(record["release_grade"])

    def test_final_url_hidden_by_injected_opener_denied_before_read(self):
        r = Response("https://www.congreso.es/end")
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "UNVERIFIED_INJECTED_REDIRECT"):
                ingest.import_url(url=self.START, source="congreso", root=Path(td),
                                  min_interval=1, opener=lambda *args, **kw: r)
            self.assertEqual(r.read_count, 0)

    def test_invalid_start_authority_and_credentials(self):
        for url in ["http://www.congreso.es/x", "https://www.congreso.es.evil.invalid/x",
                    "https://hacker@www.congreso.es/x", "https://www.congreso.es:444/x",
                    "https://www.congreso.es\\@evil.invalid/x",
                    "https://www.congreso.es/#fragment"]:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    ingest.import_url(url=url, source="congreso", root=Path("/unused"),
                                      opener=lambda *a,**k: self.fail("network opened"))

    def test_redirect_limit_five(self):
        hops = [f"https://www.congreso.es/{i}" for i in range(7)]
        moves = {self.START: hops[0], **{hops[i]:hops[i+1] for i in range(6)}}
        calls, result, _ = self.run_offline(moves)
        self.assertIsInstance(result, ValueError)
        self.assertEqual(str(result), "TOO_MANY_REDIRECTS")
        self.assertEqual(calls, [self.START, *hops[:5]])

    def test_bad_rate_and_timeout_finite(self):
        for v in [float("nan"), float("inf"), True, 0.1]:
            with self.subTest(rate=v):
                with self.assertRaises(ValueError):
                    ingest.import_url(url=self.START, source="congreso", root=Path("/unused"),
                                      min_interval=v, opener=lambda *a,**k: self.fail("network"))
        with self.assertRaises(ValueError):
            ingest.import_url(url=self.START, source="congreso", root=Path("/unused"),
                              timeout=float("nan"),opener=lambda *a,**k: self.fail("network"))


if __name__ == "__main__":
    unittest.main()
