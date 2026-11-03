"""One-command, disposable, REAL-HTTP scientific beta smoke.

This is not a research experiment, a public deployment, or evidence that a
Spanish political corpus was scientifically admitted. It uses only hardcoded
fictional sources and an ephemeral loopback server backed by temporary SQLite.

    python scripts/beta_scientific_smoke.py

Unlike the historical browser/playable smokes, this deliberately verifies the
scientific Pythonâ†”Node endpoint and S9 v4 durable ingestion/read/denial route.
"""
from __future__ import annotations

from contextlib import contextmanager, closing
import hashlib
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import os
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from politics_fantasy import accounts  # noqa: E402
from politics_fantasy.scientific_registry import registry_path  # noqa: E402
from politics_fantasy.server import handler_factory  # noqa: E402


class SmokeFailure(Exception):
    """A checked beta invariant failed; no source payload is attached."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise SmokeFailure(code)


@contextmanager
def local_beta():
    # No connection to the user's game DB, original documents or account store.
    with TemporaryDirectory(prefix="pfl-beta-science-") as directory:
        root = Path(directory)
        game = root / "game.sqlite3"
        account_db = root / "accounts.sqlite3"
        accounts.init_accounts(account_db)
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            handler_factory(game, None, None, account_db),
        )
        server.daemon_threads = True
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield server.server_port, registry_path(game)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


def get(port: int, path: str, *, host: str | None = None) -> tuple[int, dict]:
    client = HTTPConnection("127.0.0.1", port, timeout=15)
    headers = {"Host": host or f"127.0.0.1:{port}"}
    try:
        client.request("GET", path, headers=headers)
        response = client.getresponse()
        raw = response.read()
        return response.status, json.loads(raw.decode("utf-8"))
    finally:
        client.close()


def validate_receipt(payload: dict, *, expected_intakes: int) -> str:
    require(payload.get("schema") == "pfl.synthetic_scientific_registry.v1", "REGISTRY_CONTRACT")
    require(payload.get("evidence_class") == "SYNTHETIC_LAB_ONLY", "REGISTRY_EVIDENCE_CLASS")
    require(payload.get("R5") == "STOP_R5", "REGISTRY_R5")
    require(payload.get("scientific_ab_cycles") == 0, "REGISTRY_AB_CYCLES")
    require(payload.get("release_gates_passed") == 0, "REGISTRY_RELEASE_GATES")
    require(payload.get("real_source_ingestion_allowed") is False, "REGISTRY_REAL_INGESTION")
    require(payload.get("independent_denominator") is None, "REGISTRY_DENOMINATOR")
    registry = payload["registry"]
    require(registry["schema_version"] == 4 and registry["persistent"] is True,
            "REGISTRY_SCHEMA_VERSION")
    require(registry["recorded_distribution_count"] == 6
            and registry["internal_uncatalogued_fixture_receipts"] == 1,
            "CANONICAL_FIXTURE_CHANGED")
    require(registry["source_bytes_exposed"] is False
            and registry["private_source_ids_exposed"] is False,
            "REGISTRY_PRIVACY")
    intake = payload["snapshot"]["synthetic_intake"]
    require(intake["intake_count"] == expected_intakes, "INTAKE_COUNT")
    require(intake["history_event_count"] == expected_intakes * 2, "INTAKE_APPEND_ONLY")
    require(intake["source_rows_added_to_canonical"] == 0
            and intake["real_source_ingestion_allowed"] is False
            and intake["scientific_admission_allowed"] is False
            and intake["rights_for_public_display"] is False,
            "INTAKE_REAL_PROMOTION")
    require(intake["graph"]["cross_issuer_links_created"] is False,
            "INTAKE_CROSS_ISSUER_LINK")
    receipt = payload["snapshot_receipt"]
    canonical = receipt["canonical_json"].encode("utf-8")
    sha = hashlib.sha256(canonical).hexdigest()
    require(sha == receipt["sha256"] == payload["snapshot_receipt_sha256"],
            "REGISTRY_RECEIPT_SHA")
    require(len(canonical) == receipt["bytes"], "REGISTRY_RECEIPT_LENGTH")
    assert_snapshot = json.loads(canonical)
    require(assert_snapshot["snapshot"] == payload["snapshot"]
            and assert_snapshot["distributions"] == registry["distributions"],
            "REGISTRY_CANONICAL_SCOPE")
    public = json.dumps(payload, ensure_ascii=False)
    for secret in ("AUTHOR_ALPHA:FILE_1", "AUTHOR_BETA:FILE_1",
                   "A:LOCAL_ACTOR", "SYN:S9_INTERNAL_STAGE"):
        require(secret not in public, "REGISTRY_PRIVATE_IDENTIFIER_LEAK")
    return sha


def enroll(db: Path, fixture: str) -> dict:
    # A separate Python process exercises the actual user-facing CLI, rather
    # than calling the same seed function that builds the initial registry.
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src"),
           "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(
        [sys.executable, "-B", "-m", "politics_fantasy.scientific_registry",
         "--db", str(db), "--enroll", fixture],
        cwd=ROOT, env=env, encoding="utf-8", capture_output=True,
        check=False, timeout=20,
    )
    require(result.returncode == 0, "SANDBOX_ENROLLMENT_COMMAND")
    return json.loads(result.stdout)


def run() -> dict:
    checks: list[str] = []
    with local_beta() as (port, db):
        status, health = get(port, "/api/health")
        require(status == 200 and health.get("real_player_scoring") is False,
                "LOCAL_HEALTH")
        checks.append("loopback_health")

        status, readiness = get(port, "/api/beta-readiness")
        require(status == 200 and readiness.get("ok") is True
                and readiness.get("local_runtime", {}).get("status")
                    == "READY_FOR_LOCAL_PREFLIGHT"
                and readiness.get("public_release", {}).get("eligible") is False
                and readiness.get("public_release", {}).get("gates_total") == 6
                and readiness.get("scientific_admission", {}).get("r5_status") == "STOP_R5"
                and readiness.get("scientific_admission", {}).get("system20_valid_ab_cycles") == 0,
                "LOCAL_READINESS_MUST_NOT_PROMOTE_RELEASE")
        checks.append("local_preflight_distinct_from_public_release")

        code, lab = get(port, "/api/scientific-integration-lab?cut=late&scenario=baseline")
        require(code == 200 and lab.get("R5") == "STOP_R5"
                and lab.get("scientific_AB_cycles") == 0
                and lab.get("release_gates_passed") == 0
                and lab.get("real_people_scoring_enabled") is False,
                "PYTHON_NODE_SCIENTIFIC_BRIDGE")
        require(len(lab["warehouse"]["b0_b3_witness_sets"]["sets_by_knowledge_cut"]["late"]["sets"]) == 20,
                "SCIENTIFIC_S7_WITNESSES")
        checks.append("real_http_python_node_lab_s7")

        code, baseline = get(port, "/api/scientific-registry?cut=late")
        require(code == 200, "REGISTRY_INITIAL_HTTP")
        baseline_sha = validate_receipt(baseline, expected_intakes=0)
        checks.append("durable_v4_empty_overlay")

        for fixture, expected in (("sandbox_alpha_v1", "SANDBOX_VALIDATED"),
                                  ("sandbox_beta_v1", "SANDBOX_VALIDATED"),
                                  ("sandbox_bad_issuer", "SANDBOX_REJECTED")):
            reply = enroll(db, fixture)
            require(reply["status"] == expected
                    and reply["event_count_appended"] == 2
                    and reply["real_source_admitted"] is False,
                    "AUTHOR_CLOSED_ENROLLMENT")
        checks.append("three_independent_cli_enrollments")
        code, after = get(port, "/api/scientific-registry?cut=late&valid_at=2026-10-10")
        require(code == 200, "REGISTRY_REOPEN_HTTP")
        later_sha = validate_receipt(after, expected_intakes=3)
        intake = after["snapshot"]["synthetic_intake"]
        require(intake["logical_source_count"] == 2
                and intake["validated_count"] == 2
                and intake["rejected_count"] == 1
                and intake["logical_decisions_count"] == 0,
                "INTAKE_ONTOLOGY")
        require(later_sha != baseline_sha, "INTAKE_RECEIPT_NOT_UPDATED")
        checks.append("accepted_rejected_and_receipt_changed")
        code, early = get(port, "/api/scientific-registry?cut=early")
        require(code == 200 and early["snapshot"]["synthetic_intake"]["intake_count"] == 0,
                "REGISTRY_FUTURE_LEAK")
        validate_receipt(early, expected_intakes=0)
        checks.append("early_cut_no_future_intakes")

        require(get(port, "/api/scientific-registry?cut=invalid")[0] == 400,
                "REGISTRY_INVALID_QUERY_ACCEPTED")
        require(get(port, "/api/health", host="foreign.invalid")[0] == 403,
                "LOOPBACK_HOST_VALIDATION")
        checks.append("http_400_and_host_403")

        # Fault injection is confined to the temporary DB. The actual server
        # must produce 503, not a seemingly valid stale receipt.
        with closing(sqlite3.connect(db)) as connection:
            with connection:
                trigger = connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name LIMIT 1"
                ).fetchone()
                require(trigger is not None, "NO_IMMUTABLE_TRIGGER")
                connection.execute('DROP TRIGGER "' + trigger[0].replace('"', '""') + '"')
        code, error = get(port, "/api/scientific-registry?cut=late")
        require(code == 503 and error.get("error") == "SYNTHETIC_REGISTRY_UNAVAILABLE",
                "REGISTRY_TAMPER_NOT_CLOSED")
        checks.append("tampered_schema_http_503")

    return {
        "schema": "pfl.beta_scientific_http_smoke.v1",
        "status": "PASS",
        "scope": "EPHEMERAL_AUTHOR_CLOSED_LOOPBACK_ONLY",
        "synthetic": True,
        "checks": checks,
        "checks_passed": len(checks),
        "initial_receipt_sha256": baseline_sha,
        "enrolled_receipt_sha256": later_sha,
        "new_empirical_sources": 0,
        "scientific_ab_cycles": 0,
        "release_gates_passed": 0,
        "R5": "STOP_R5",
    }


def main() -> int:
    try:
        report = run()
    except Exception as exc:
        # Do not leak temp paths, local source bytes, cookie or account data.
        report = {
            "schema": "pfl.beta_scientific_http_smoke.v1",
            "status": "FAIL",
            "error_code": exc.args[0] if isinstance(exc, SmokeFailure) else type(exc).__name__,
            "R5": "STOP_R5",
        }
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
