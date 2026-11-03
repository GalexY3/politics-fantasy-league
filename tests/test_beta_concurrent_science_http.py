"""Real concurrent, anonymous scientific reads on one durable SQLite registry.

The local browser may request multiple cuts and family filters while a user
changes a comparison or reloads the Observatorio. The default server is
threaded; a registry that only succeeds sequentially is not a stable beta.
This is a new stress requirement, not a purported historical PREPATCH bug.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import closing
import hashlib
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
from threading import Barrier, Thread
from urllib.parse import urlencode

from politics_fantasy.server import handler_factory
from politics_fantasy.scientific_registry import enroll_synthetic_fixture


def _get(port: int, path: str) -> tuple[int, dict]:
    with closing(HTTPConnection("127.0.0.1", port, timeout=20)) as client:
        client.request("GET", path, headers={"Host": f"127.0.0.1:{port}"})
        response = client.getresponse()
        return response.status, json.loads(response.read())


def _sha_verified(payload: dict) -> bool:
    receipt = payload["snapshot_receipt"]
    b = receipt["canonical_json"].encode("utf-8")
    return (len(b) == receipt["bytes"]
            and hashlib.sha256(b).hexdigest() == receipt["sha256"]
            == payload["snapshot_receipt_sha256"]
            and json.loads(b)["snapshot"] == payload["snapshot"])


def test_concurrent_anonymous_filters_and_subsequent_reopen(tmp_path):
    game_db = tmp_path / "unused-game.sqlite3"
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        handler_factory(game_db, None, None, None, scientific_only=True),
    )
    server.daemon_threads = True
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        port = server.server_port
        paths = []
        for cut in ("early", "late"):
            for family in ("all", "PP04", "CHAIN", "CHRONICLE"):
                for valid_at in ("2026-09-11", "2026-10-10"):
                    query = urlencode({"cut": cut, "family": family,
                                       "valid_at": valid_at,
                                       "published_until": "as_of"})
                    paths.append("/api/scientific-registry?" + query)
        # 16 simultaneous GETs against the SAME initially absent DB.
        barrier = Barrier(len(paths))

        def once(path: str):
            barrier.wait(timeout=15)
            return path, _get(port, path)

        with ThreadPoolExecutor(max_workers=len(paths)) as pool:
            # Submit ALL futures before waiting: a lazy submit generator would
            # otherwise wait on the first request and deadlock the barrier.
            futures = [pool.submit(once, path) for path in paths]
            results = [future.result(timeout=35) for future in futures]
        observed = {}
        for path, (status, data) in results:
            assert status == 200, (path, status, data.get("error"))
            assert _sha_verified(data)
            assert data["R5"] == "STOP_R5"
            assert data["release_gates_passed"] == 0
            assert data["scientific_ab_cycles"] == 0
            assert data["real_source_ingestion_allowed"] is False
            assert data["registry"]["private_source_ids_exposed"] is False
            assert data["registry"]["source_bytes_exposed"] is False
            assert data["snapshot"]["synthetic_intake"]["intake_count"] == 0
            observed[path] = data["snapshot_receipt_sha256"]
        assert len(observed) == len(paths)
        # A fresh GET after all simultaneous reads must be deterministic,
        # not a partially seeded or locked registry.
        for path in paths:
            status, data = _get(port, path)
            assert status == 200
            assert _sha_verified(data)
            assert data["snapshot_receipt_sha256"] == observed[path]
        # A new, explicitly enrolled author-closed revision is visible under
        # the right fictional knowledge cut, not retroactively in the past.
        science_db = tmp_path / "scientific_registry_synthetic.sqlite3"
        result = enroll_synthetic_fixture(science_db, "sandbox_alpha_v1")
        assert result["status"] == "SANDBOX_VALIDATED"
        with ThreadPoolExecutor(max_workers=len(paths)) as pool:
            futures = [pool.submit(_get, port, path) for path in paths]
            reopened = [future.result(timeout=35) for future in futures]
        changed = 0
        for path, (status, data) in zip(paths, reopened):
            assert status == 200
            assert _sha_verified(data)
            # The authored intake overlay is a separate family=all journal;
            # filtering for a canonical family never creates a fictitious
            # PP04/CHAIN/CHRONICLE documentary admission.
            if "cut=early" in path or "family=all" not in path:
                assert data["snapshot"]["synthetic_intake"]["intake_count"] == 0
                assert data["snapshot_receipt_sha256"] == observed[path]
            else:
                assert data["snapshot"]["synthetic_intake"]["intake_count"] == 1
                assert data["snapshot"]["synthetic_intake"]["source_rows_added_to_canonical"] == 0
                assert data["snapshot_receipt_sha256"] != observed[path]
                changed += 1
        assert changed == 2  # late/all at the two specified valid_at dates
        assert not game_db.exists(), "Science-only GET created a Fantasy game database"
        assert not (tmp_path / "accounts.sqlite3").exists()
        assert (tmp_path / "scientific_registry_synthetic.sqlite3").is_file()
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=8)
