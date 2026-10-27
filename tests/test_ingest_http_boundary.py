"""Real ephemeral localhost server: source catalog is HTTP; raw capture is NOT."""
import http.client
import json
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from http.server import ThreadingHTTPServer

from politics_fantasy.server import handler_factory


class IngestHTTPBoundary(unittest.TestCase):
    def test_readonly_catalog_and_absent_capture_routes(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            server = ThreadingHTTPServer(
                ("127.0.0.1", 0), handler_factory(root / "game.db", None, None)
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            def request(method, route, *, host=None, body=None):
                conn = http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
                headers = {"Host": host or f"127.0.0.1:{server.server_port}"}
                if body is not None:
                    headers["Content-Type"] = "application/json"
                conn.request(method, route, body=body, headers=headers)
                resp = conn.getresponse()
                code, data = resp.status, json.loads(resp.read())
                conn.close()
                return code,data
            try:
                code, stages = request("GET","/api/source-stages")
                self.assertEqual(code, 200)
                self.assertEqual(stages["original_publication_timestamps_verified"], 0)
                self.assertFalse(stages["real_person_scoring"])
                self.assertFalse(stages["release_ready"])
                self.assertEqual(len(stages["records"]), 3)
                self.assertTrue(all(r["first_public_at"] is None for r in stages["records"]))
                code, health = request("GET","/api/health")
                self.assertEqual(code, 200)
                self.assertEqual(health["mode"], "SYNTHETIC_DEMO")
                self.assertFalse(health["real_player_scoring"])
                fake = b'{"url":"https://www.congreso.es/fake","source":"congreso"}'
                for route in ["/api/ingest","/api/source-import","/api/capture"]:
                    code, output = request("POST",route,body=fake)
                    self.assertEqual(code, 404)
                    self.assertEqual(output["error"], "NOT_FOUND")
                for route in ["/api/ingest","/api/quarantine"]:
                    code, output = request("GET",route)
                    self.assertEqual(code,404)
                    self.assertEqual(output["error"],"NOT_FOUND")
                code, err = request("GET","/api/source-stages",host="attacker.invalid")
                self.assertEqual(code,403)
                self.assertEqual(err["error"],"LOCAL_HOST_REQUIRED")
                self.assertFalse((root / "manifest.jsonl").exists())
                self.assertFalse((root / "quarantine_reviews.jsonl").exists())
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
