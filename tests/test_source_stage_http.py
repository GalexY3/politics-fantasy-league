"""Read-only HTTP source-stage tests; run with PYTHONPATH=src.

Loopback-only transient server, no DB setup, no external requests.
"""
import http.client
import json
import threading
import unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.parse import urlsplit, unquote

from politics_fantasy.server import handler_factory


class SourceStagesHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            handler_factory(Path("/unused/not_created.db"), None, None),
        )
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, method, path, host=None, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        conn.putrequest(method, path, skip_host=True)
        conn.putheader("Host", host or f"127.0.0.1:{self.server.server_port}")
        if body is not None:
            conn.putheader("Content-Length", str(len(body)))
        conn.endheaders(body)
        response = conn.getresponse()
        status = response.status
        payload = json.loads(response.read().decode("utf-8"))
        conn.close()
        return status, payload

    def test_local_source_stages_quarantined(self):
        status, payload = self.request("GET", "/api/source-stages")
        self.assertEqual(status, 200)
        self.assertEqual(len(payload["records"]), 3)
        self.assertEqual(
            {record["evidence_ref"] for record in payload["records"]},
            {"CCYL:BOCCL-12-000986", "CCYL:BOCCL-12-001042", "SENADO-XV-P82-20260915"},
        )
        self.assertTrue(all(not record["evidence_ref"].startswith("ESE/") for record in payload["records"]))
        self.assertEqual(payload["original_publication_timestamps_verified"], 0)
        self.assertFalse(payload["real_person_scoring"])
        self.assertFalse(payload["release_ready"])
        self.assertTrue(all(record["first_public_at"] is None for record in payload["records"]))

    def test_query_cannot_supply_fake_first_public_timestamp(self):
        status, payload = self.request(
            "GET", "/api/source-stages?first_public_at=2000-01-01T00%3A00%3A00Z&trusted_registry=true"
        )
        self.assertEqual(status, 200)
        self.assertTrue(all(record["first_public_at"] is None for record in payload["records"]))

    def test_cve_document_urls_are_served_on_loopback_without_certifying_time(self):
        status, payload = self.request("GET", "/api/source-stages")
        self.assertEqual(status, 200)
        records = {record["cve"]: record for record in payload["records"] if record.get("cve")}
        self.assertEqual(set(records), {"BOCCL-12-000986", "BOCCL-12-001042"})
        for cve, record in records.items():
            url = urlsplit(record["source_url"])
            self.assertEqual((url.scheme, url.hostname, url.port), ("https", "www.ccyl.es", None))
            self.assertIsNone(url.username)
            self.assertIsNone(url.password)
            self.assertIn(cve + ".xml", unquote(url.query))
            self.assertIsNone(record["first_public_at"])
        self.assertFalse(payload["real_person_scoring"])
        self.assertFalse(payload["release_ready"])

    def test_bad_host_rejected_before_source_route(self):
        status, payload = self.request("GET", "/api/source-stages", host="attacker.example")
        self.assertEqual(status, 403)
        self.assertEqual(payload["error"], "LOCAL_HOST_REQUIRED")

    def test_post_is_not_source_mutation_endpoint(self):
        status, payload = self.request("POST", "/api/source-stages", body=b"{}")
        self.assertEqual(status, 404)
        self.assertEqual(payload["error"], "NOT_FOUND")


if __name__ == "__main__":
    unittest.main()
