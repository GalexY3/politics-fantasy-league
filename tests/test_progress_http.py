"""Live loopback-only endpoint test for progress report.

Uses only the local handler; does not enable or test public hosting.
"""
import http.client
import json
import threading
from http.server import ThreadingHTTPServer

from politics_fantasy.server import handler_factory


def test_progress_http_loopback_and_host_guard(tmp_path):
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        handler_factory(tmp_path / "demo.sqlite", None, None)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=8)
        conn.request("GET", "/api/progress")
        response = conn.getresponse()
        payload = json.loads(response.read())
        conn.close()
        assert response.status == 200
        assert payload["ok"] is True
        assert abs(payload["progress_pct"] - 36.90) < 1e-8
        assert payload["track_count"] == 9
        assert len(payload["release_blockers"]) == 6
        assert payload["real_people_scoring_ready"] is False

        conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=8)
        conn.request("GET", "/api/progress", headers={"Host": "untrusted.example"})
        bad = conn.getresponse()
        bad.read()
        conn.close()
        assert bad.status == 403
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=8)
