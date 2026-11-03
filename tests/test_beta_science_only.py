"""Actual loopback runtime: scientific beta without Fantasy account storage.

This is a new optional beta capability, not a purported PREPATCH defect.
All local state is created below pytest's temporary directory.
"""
from __future__ import annotations

from contextlib import closing
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def _request(port: int, route: str, *, method: str = "GET",
             body: bytes | None = None) -> tuple[int, dict]:
    with closing(http.client.HTTPConnection("127.0.0.1", port, timeout=20)) as client:
        client.request(method, route, body=body, headers={
            "Host": f"127.0.0.1:{port}",
            "Content-Type": "application/json",
            "X-PFL-Request": "1",
        })
        response = client.getresponse()
        return response.status, json.loads(response.read().decode("utf-8"))


def test_science_only_actual_launcher_anonymous_and_separate_from_accounts(tmp_path):
    base = tmp_path / "scientific_run"
    db = base / "science.sqlite3"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8",
           "PYTHONDONTWRITEBYTECODE": "1"}
    process = subprocess.Popen([
        sys.executable, "-B", str(ROOT / "run_demo.py"),
        "--science-only", "--port", "0", "--db", str(db)],
        cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8",
    )
    try:
        line = process.stdout.readline()
        match = re.search(r"http://127\.0\.0\.1:(\d+)", line)
        assert match, f"Expected loopback URL, got {line[:100]!r}"
        port = int(match.group(1))
        code, health = _request(port, "/api/health")
        assert code == 200
        assert health["mode"] == "SYNTHETIC_SCIENCE_ONLY"
        assert health["accounts_enabled"] is False
        assert health["real_player_scoring"] is False

        code, session = _request(port, "/api/session")
        assert code == 401
        assert session["authenticated"] is False
        assert session["science_only"] is True
        for forbidden in ("/api/state", "/api/lab", "/api/field",
                          "/api/progress", "/api/actors",
                          "/api/official-nominations"):
            status, body = _request(port, forbidden)
            assert status == 404, forbidden
            assert body["error"] == "SCIENCE_ONLY_ROUTE_UNAVAILABLE"

        for write_path in ("/api/register", "/api/login", "/api/clubs",
                           "/api/buy", "/api/lineup",
                           "/api/simulate-round", "/api/scientific-registry"):
            status, body = _request(port, write_path, method="POST", body=b"{}")
            assert status == 404, write_path
            assert body["error"] == "SCIENCE_ONLY_WRITE_UNAVAILABLE"

        code, readiness = _request(port, "/api/beta-readiness")
        assert code == 200
        assert readiness["ok"] is True
        checks = readiness["local_runtime"]["checks"]
        assert checks == {
            "loopback_binding": True,
            "web_assets_present": True,
            "accounts_disabled_intentionally": True,
        }
        assert readiness["local_runtime"]["scope"] == "LOOPBACK_SYNTHETIC_SCIENCE_ONLY"
        assert readiness["scientific_admission"]["r5_status"] == "STOP_R5"
        assert readiness["public_release"]["eligible"] is False

        code, late = _request(port, "/api/scientific-registry?cut=late")
        assert code == 200
        assert late["registry"]["schema_version"] == 4
        assert late["R5"] == "STOP_R5"
        assert late["scientific_ab_cycles"] == 0
        assert late["release_gates_passed"] == 0
        receipt = late["snapshot_receipt"]
        assert (hashlib.sha256(receipt["canonical_json"].encode()).hexdigest()
                == late["snapshot_receipt_sha256"] == receipt["sha256"])
        code, early = _request(port, "/api/scientific-registry?cut=early")
        assert code == 200
        assert (early["registry"]["visible_distribution_count"]
                < late["registry"]["visible_distribution_count"])
        code, lab = _request(port, "/api/scientific-integration-lab?cut=late&scenario=baseline")
        assert code == 200
        assert lab["R5"] == "STOP_R5"
        assert lab["scientific_AB_cycles"] == 0
        assert len(lab["warehouse"]["b0_b3_witness_sets"]["sets_by_knowledge_cut"]["late"]["sets"]) == 20

        # This visitor-only server has not even opened an account or game DB.
        assert not (base / "accounts.sqlite3").exists()
        assert not (base / "accounts").exists()
        assert not db.exists()
        assert (base / "scientific_registry_synthetic.sqlite3").is_file()
        assert _request(port, "/api/scientific-registry?cut=nonsense")[0] == 400
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()


def test_science_only_default_database_is_outside_fantasy_demo(monkeypatch):
    import run_demo

    actual = []
    monkeypatch.setattr(run_demo, "serve", lambda db, *, port, scientific_only:
                        actual.append((db, port, scientific_only)))
    run_demo.main(["--science-only"])
    assert actual == [(run_demo.ROOT / "data" / "science_beta" / "science.db",
                       8787, True)]
    assert "data/demo" not in actual[0][0].as_posix()
