"""BR30J local HTTP test: real Python handler on loopback ephemeral port.

Only run in a local CI runner. Does NOT publish an internet-facing web service.
"""
from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

from politics_fantasy.server import handler_factory


def test_loopback_evidence_endpoint_synthetic_and_anonymous(tmp_path: Path):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_factory(tmp_path / "db.sqlite", None, None))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=8)
        conn.request("GET", "/api/evidence-readiness")
        response = conn.getresponse()
        payload = json.loads(response.read())
        conn.close()
        assert response.status == 200
        assert payload["origin"] == "SYNTHETIC_ONLY"
        assert payload["real_people_verified"] == 0
        assert payload["real_person_scoring"] is False
        assert payload["entities"] == 7
        assert "Alma Imaginaria" not in json.dumps(payload)

        conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=8)
        conn.request("GET", "/api/evidence-readiness", headers={"Host": "attacker.invalid"})
        bad = conn.getresponse()
        bad.read()
        conn.close()
        assert bad.status == 403
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=8)
