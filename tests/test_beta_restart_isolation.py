"""Real two-process restart of the local beta, with persistent synthetic S9 v4.

All SQLite files live under pytest's temporary directory. An independent
author-closed CLI process enrolls synthetic intake records while the first
server runs. A separate disposable copy is corrupted only after both normal
server launches have finished; this must return HTTP 503.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
from http.client import HTTPConnection
import json
import os
from pathlib import Path
from queue import Empty, Queue
import re
import shutil
import sqlite3
import subprocess
import sys
from threading import Thread

ROOT = Path(__file__).resolve().parents[1]
RUN_DEMO = ROOT / "run_demo.py"
PASSWORD = "fictional-only-passphrase-2026"
REGISTRY_NAME = "scientific_registry_synthetic.sqlite3"
PRIVATE_IDENTIFIERS = (
    "AUTHOR_ALPHA:FILE_1", "AUTHOR_BETA:FILE_1",
    "AUTHOR_REJECTED:FILE_1", "SYN:S9_INTERNAL_STAGE",
    "A:LOCAL_ACTOR", "REAL:UNVERIFIED_FIXTURE",
)


def _environment() -> dict[str, str]:
    return {
        **os.environ,
        "PYTHONPATH": str(ROOT / "src"),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONIOENCODING": "utf-8",
    }


@contextmanager
def running_beta(game_db: Path, *, science_only: bool = False):
    """Start the real launcher on an OS-selected loopback port, then stop it."""
    arguments = ([sys.executable, "-B", str(RUN_DEMO), "--science-only"]
                 if science_only else [sys.executable, "-B", str(RUN_DEMO)])
    process = subprocess.Popen(
        [*arguments, "--port", "0", "--db", str(game_db)],
        cwd=ROOT, env=_environment(), stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, encoding="utf-8",
    )
    first_line: Queue[str] = Queue(maxsize=1)
    reader = Thread(target=lambda: first_line.put(process.stdout.readline()),
                    daemon=True)
    reader.start()
    try:
        try:
            banner = first_line.get(timeout=15)
        except Empty as exc:
            raise AssertionError("Local server did not report its loopback port") from exc
        match = re.search(r"http://127\.0\.0\.1:(\d+)", banner)
        assert match is not None, "Local launcher did not bind 127.0.0.1"
        port = int(match.group(1))
        assert 1 <= port <= 65535
        assert process.poll() is None, "Local launcher exited after announcing a port"
        yield port, process.pid
    finally:
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        process.stdout.close()
        process.stderr.close()


class Client:
    """HTTP over loopback; independent cookies model separate local browsers."""

    def __init__(self):
        self.cookie: str | None = None

    def request(self, port: int, method: str, path: str, *,
                payload: dict | None = None, csrf: str | None = None) -> tuple[int, dict, str]:
        connection = HTTPConnection("127.0.0.1", port, timeout=30)
        headers = {"Host": f"127.0.0.1:{port}"}
        if self.cookie:
            headers["Cookie"] = self.cookie
        if csrf is not None:
            headers["X-PFL-CSRF"] = csrf
        body = None
        if payload is not None:
            headers.update({"Content-Type": "application/json", "X-PFL-Request": "1"})
            body = json.dumps(payload).encode("utf-8")
        try:
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            cookie = response.getheader("Set-Cookie")
            if cookie is not None:
                self.cookie = cookie.split(";", 1)[0]
            status = response.status
            cache = response.getheader("Cache-Control")
            content = json.loads(response.read().decode("utf-8"))
            return status, content, cache
        finally:
            connection.close()


def get(client: Client, port: int, path: str, *, status: int = 200) -> dict:
    code, body, cache = client.request(port, "GET", path)
    assert code == status, f"Unexpected GET status for {path.split('?')[0]}: {code}"
    assert cache == "no-store"
    return body


def _register_login(client: Client, port: int, name: str) -> str:
    status, _, _ = client.request(
        port, "POST", "/api/register",
        payload={"username": name, "password": PASSWORD},
    )
    assert status == 201
    status, result, _ = client.request(
        port, "POST", "/api/login",
        payload={"username": name, "password": PASSWORD},
    )
    assert status == 200
    assert result["result"]["username"] == name
    return result["result"]["csrf"]


def _enroll_from_separate_process(scientific_db: Path, fixture: str) -> dict:
    result = subprocess.run(
        [sys.executable, "-B", "-m", "politics_fantasy.scientific_registry",
         "--db", str(scientific_db), "--enroll", fixture],
        cwd=ROOT, env=_environment(), capture_output=True, encoding="utf-8",
        timeout=20, check=False,
    )
    assert result.returncode == 0, "Closed author CLI failed to enroll its fixture"
    return json.loads(result.stdout)


def _receipt_sha(payload: dict) -> str:
    receipt = payload["snapshot_receipt"]
    assert receipt["schema"] == "pfl.synthetic_registry_snapshot_receipt.v1"
    canonical = receipt["canonical_json"].encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()
    assert receipt["bytes"] == len(canonical)
    assert payload["snapshot_receipt_sha256"] == receipt["sha256"] == digest
    decoded = json.loads(canonical)
    assert decoded["snapshot"] == payload["snapshot"]
    assert decoded["distributions"] == payload["registry"]["distributions"]
    assert payload["registry"]["schema_version"] == 4
    assert payload["registry"]["recorded_distribution_count"] == 6
    assert payload["R5"] == "STOP_R5"
    assert payload["scientific_ab_cycles"] == 0
    assert payload["release_gates_passed"] == 0
    assert payload["real_source_ingestion_allowed"] is False
    assert payload["registry"]["private_source_ids_exposed"] is False
    public = json.dumps(payload, ensure_ascii=False)
    assert all(private not in public for private in PRIVATE_IDENTIFIERS)
    return digest


def _intake(payload: dict, count: int, *, valid: int, rejected: int) -> dict:
    _receipt_sha(payload)
    data = payload["snapshot"]["synthetic_intake"]
    assert data["intake_count"] == count
    assert data["history_event_count"] == count * 2
    assert data["validated_count"] == valid
    assert data["rejected_count"] == rejected
    assert data["source_rows_added_to_canonical"] == 0
    assert data["logical_decisions_count"] == 0
    assert data["graph"]["cross_issuer_links_created"] is False
    assert data["scientific_admission_allowed"] is False
    assert data["rights_for_public_display"] is False
    assert data["independent_denominator"] is None
    return data


def _science_lab(client: Client, port: int) -> dict:
    result = get(client, port, "/api/scientific-integration-lab?cut=late&scenario=baseline")
    assert result["R5"] == "STOP_R5"
    assert result["scientific_AB_cycles"] == 0
    assert result["release_gates_passed"] == 0
    assert result["real_people_scoring_enabled"] is False
    assert (len(result["warehouse"]["b0_b3_witness_sets"]
                ["sets_by_knowledge_cut"]["late"]["sets"]) == 20)
    return result


def _sqlite_tables(path: Path) -> set[str]:
    # Read-only, no implicit database creation or writes.
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
        return {row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}


def test_two_real_server_processes_retain_s9_sha_and_isolate_local_accounts(tmp_path):
    assert shutil.which("node"), "Node is required by the actual Python↔Node lab endpoint"
    game_db = tmp_path / "game.sqlite3"
    auth_db = tmp_path / "accounts.sqlite3"
    science_db = tmp_path / REGISTRY_NAME
    anonymous, alice, bob = Client(), Client(), Client()
    expected_clubs = ("Equipo sintético A", "Equipo sintético B")
    registry_query = "/api/scientific-registry?cut=late&valid_at=2026-10-10"

    with running_beta(game_db) as (port, first_pid):
        assert get(anonymous, port, "/api/session", status=401) == {
            "authenticated": False, "error": "AUTH_REQUIRED"}
        assert get(anonymous, port, "/api/state", status=401) == {"error": "AUTH_REQUIRED"}
        assert get(anonymous, port, "/api/health")["real_player_scoring"] is False
        _science_lab(anonymous, port)
        before = get(anonymous, port, registry_query)
        before_sha = _receipt_sha(before)
        _intake(before, 0, valid=0, rejected=0)

        csrf_a = _register_login(alice, port, "beta_local_a")
        csrf_b = _register_login(bob, port, "beta_local_b")
        code, created_a, _ = alice.request(
            port, "POST", "/api/clubs", csrf=csrf_a, payload={"name": expected_clubs[0]})
        assert code == 200
        code, created_b, _ = bob.request(
            port, "POST", "/api/clubs", csrf=csrf_b, payload={"name": expected_clubs[1]})
        assert code == 200
        assert created_a["result"]["id"] != created_b["result"]["id"]
        state_a = get(alice, port, "/api/state")
        state_b = get(bob, port, "/api/state")
        assert state_a["authentication"] == state_b["authentication"] == "LOCAL_ACCOUNT_ISOLATED"
        clubs_a = {row["name"] for row in state_a["clubs"]}
        clubs_b = {row["name"] for row in state_b["clubs"]}
        assert expected_clubs[0] in clubs_a and expected_clubs[1] not in clubs_a
        assert expected_clubs[1] in clubs_b and expected_clubs[0] not in clubs_b
        a_club_id = created_a["result"]["id"]
        code, _, _ = alice.request(
            port, "POST", "/api/buy",
            csrf=csrf_a, payload={"club_id": a_club_id, "figure_id": "F04"})
        assert code == 200
        code, denied, _ = bob.request(
            port, "POST", "/api/buy",
            csrf=csrf_b, payload={"club_id": a_club_id, "figure_id": "F05"})
        assert code == 404 and denied["error"] == "UNKNOWN_ENTITY"
        assert (next(x for x in get(alice, port, "/api/state")["figures"]
                     if x["id"] == "F04")["owner_id"] == a_club_id)
        assert (next(x for x in get(bob, port, "/api/state")["figures"]
                     if x["id"] == "F04")["owner_id"] is None)
        assert get(anonymous, port, "/api/state", status=401)["error"] == "AUTH_REQUIRED"

        # The offline author-only CLI is a distinct OS process. HTTP has no
        # scientific intake write route, including when an account is logged in.
        for fixture, outcome in (
            ("sandbox_alpha_v1", "SANDBOX_VALIDATED"),
            ("sandbox_beta_v1", "SANDBOX_VALIDATED"),
            ("sandbox_alpha_v2", "SANDBOX_VALIDATED"),
            ("sandbox_bad_issuer", "SANDBOX_REJECTED"),
        ):
            result = _enroll_from_separate_process(science_db, fixture)
            assert result["status"] == outcome
            assert result["event_count_appended"] == 2
            assert result["idempotent_replay"] is False
            assert result["real_source_admitted"] is False

        after = get(anonymous, port, registry_query)
        after_sha = _receipt_sha(after)
        intake = _intake(after, 4, valid=3, rejected=1)
        assert after_sha != before_sha
        assert intake["logical_source_count"] == 2
        assert intake["documentary_revision_count"] == 3
        assert intake["graph"]["logical_source_count_valid_at"] == 2
        assert get(alice, port, registry_query)["snapshot_receipt_sha256"] == after_sha
        assert get(bob, port, registry_query)["snapshot_receipt_sha256"] == after_sha

        # valid_at is legal/fixture validity, not when a documentary event
        # became known. Explicit as_of is derived from the allowlisted cut.
        early = get(anonymous, port, "/api/scientific-registry?cut=early&valid_at=2026-10-10")
        _intake(early, 0, valid=0, rejected=0)
        assert early["as_of"] < after["as_of"]
        before_publication = get(
            anonymous, port,
            "/api/scientific-registry?cut=late&valid_at=2026-10-10"
            "&published_until=2026-10-30T12%3A00%3A00Z",
        )
        _intake(before_publication, 0, valid=0, rejected=0)
        assert before_publication["snapshot_receipt_sha256"] != after_sha
        on_11 = get(anonymous, port, "/api/scientific-registry?cut=late&valid_at=2026-09-11")
        on_15 = get(anonymous, port, "/api/scientific-registry?cut=late&valid_at=2026-09-15")
        assert _intake(on_11, 4, valid=3, rejected=1)["graph"]["logical_source_count_valid_at"] == 1
        assert _intake(on_15, 4, valid=3, rejected=1)["graph"]["logical_source_count_valid_at"] == 1
        assert on_11["snapshot_receipt_sha256"] != on_15["snapshot_receipt_sha256"]
        assert after_sha != on_15["snapshot_receipt_sha256"]
        assert get(anonymous, port, "/api/scientific-registry?cut=late&family=CHAIN"
                   )["snapshot"]["synthetic_intake"]["intake_count"] == 0
        for invalid in (
            "?as_of=2026-11-01T12%3A00%3A00Z",
            "?cut=late&cut=early",
            "?valid_at=2030-01-01",
            "?published_until=now",
            "?cut=early&published_until=2026-10-30T12%3A00%3A00Z",
        ):
            error = get(anonymous, port, "/api/scientific-registry" + invalid, status=400)
            assert error == {"error": "INVALID_SYNTHETIC_REGISTRY_QUERY"}
        post_code, post_error, _ = alice.request(
            port, "POST", "/api/scientific-registry", payload={"fixture": "sandbox_alpha_v1"},
            csrf=csrf_a,
        )
        assert post_code == 404 and post_error == {"error": "NOT_FOUND"}
        assert get(anonymous, port, registry_query)["snapshot_receipt_sha256"] == after_sha

    # All OS processes have released their handles. The scientific DB is not
    # the account DB, game DB, or either account's private fantasy SQLite.
    assert science_db.exists() and auth_db.exists()
    with sqlite3.connect(auth_db) as db:
        assert db.execute("SELECT count(*) FROM account").fetchone()[0] == 2
        assert db.execute("SELECT count(*) FROM account_session").fetchone()[0] == 2
    account_game_dbs = sorted((tmp_path / "accounts").glob("*.sqlite3"))
    assert len(account_game_dbs) == 2
    assert len({x.resolve() for x in [auth_db, science_db, *account_game_dbs]}) == 4
    assert {"account", "account_session"} <= _sqlite_tables(auth_db)
    assert "distribution" not in _sqlite_tables(auth_db)
    assert {"registry_meta", "synthetic_intake_event"} <= _sqlite_tables(science_db)
    assert not {"account", "account_session", "club"} & _sqlite_tables(science_db)
    for account_game in account_game_dbs:
        assert {"club", "figure"} <= _sqlite_tables(account_game)
        assert "synthetic_intake_event" not in _sqlite_tables(account_game)
    first_db_sha = hashlib.sha256(science_db.read_bytes()).hexdigest()

    # A second, separate OS server process uses the SAME original SQLite
    # directory. No new enrollment, simulated reseed or direct state patch.
    with running_beta(game_db) as (port2, second_pid):
        assert second_pid != first_pid
        assert get(anonymous, port2, "/api/session", status=401)["authenticated"] is False
        assert get(anonymous, port2, "/api/state", status=401)["error"] == "AUTH_REQUIRED"
        _science_lab(anonymous, port2)
        again = get(anonymous, port2, registry_query)
        restart_sha = _receipt_sha(again)
        assert restart_sha == after_sha
        after_restart = _intake(again, 4, valid=3, rejected=1)
        assert after_restart == intake
        assert get(anonymous, port2, "/api/scientific-registry?cut=early"
                   )["snapshot"]["synthetic_intake"]["intake_count"] == 0
        assert get(anonymous, port2, "/api/scientific-registry?cut=late"
                   "&published_until=2026-10-30T12%3A00%3A00Z"
                   )["snapshot"]["synthetic_intake"]["intake_count"] == 0
        assert get(alice, port2, "/api/session")["authenticated"] is True
        assert get(bob, port2, "/api/session")["authenticated"] is True
        resumed_a = get(alice, port2, "/api/state")
        resumed_b = get(bob, port2, "/api/state")
        resumed_names_a = {row["name"] for row in resumed_a["clubs"]}
        resumed_names_b = {row["name"] for row in resumed_b["clubs"]}
        assert expected_clubs[0] in resumed_names_a and expected_clubs[1] not in resumed_names_a
        assert expected_clubs[1] in resumed_names_b and expected_clubs[0] not in resumed_names_b
        assert next(x for x in resumed_a["figures"] if x["id"] == "F04")["owner_id"] == a_club_id
        assert next(x for x in resumed_b["figures"] if x["id"] == "F04")["owner_id"] is None
        assert get(alice, port2, registry_query)["snapshot_receipt_sha256"] == restart_sha
        assert get(bob, port2, registry_query)["snapshot_receipt_sha256"] == restart_sha
        assert get(anonymous, port2, "/api/state", status=401)["error"] == "AUTH_REQUIRED"
    second_db_sha = hashlib.sha256(science_db.read_bytes()).hexdigest()
    assert first_db_sha == second_db_sha, "Scientific SQLite bytes changed on read/restart"

    # Corrupt ONLY an offline copy: original S9 database remains untouched.
    tamper_root = tmp_path / "disposable_tamper_copy"
    tamper_root.mkdir()
    copied_science = tamper_root / REGISTRY_NAME
    shutil.copy2(science_db, copied_science)
    with sqlite3.connect(copied_science) as db:
        db.execute("DROP TRIGGER registry_distribution_immutable_update")
    with running_beta(tamper_root / "copy-game.sqlite3") as (tamper_port, _):
        rejected = get(anonymous, tamper_port, registry_query, status=503)
        assert rejected == {"error": "SYNTHETIC_REGISTRY_UNAVAILABLE"}
    assert hashlib.sha256(science_db.read_bytes()).hexdigest() == first_db_sha
    assert hashlib.sha256(copied_science.read_bytes()).hexdigest() != first_db_sha
    # Short, source-ID-free, account-free technical receipt for pytest -s.
    print(
        "BETA_RESTART_ISOLATION "
        f"server_processes=2 accounts=2 fantasy_db_files=2 intake=4 "
        f"accepted=3 rejected=1 history_events=8 schema_v=4 "
        f"receipt_sha256={restart_sha} sqlite_sha256={second_db_sha} "
        "invalid_query_http=400 invalid_post_http=404 tampered_copy_http=503"
    )


def test_science_only_two_process_restart_and_recovery_without_fantasy_store(tmp_path):
    """Visitor-only startup→ingest→restart has a persistent, exact S9 receipt.

    This is a new acceptance control, not an invented PREPATCH regression.
    Any deliberately corrupted registry is an isolated disposable COPY.
    """
    game_unused = tmp_path / "science-only" / "unused-game.sqlite3"
    science_db = game_unused.parent / REGISTRY_NAME
    account_db = game_unused.parent / "accounts.sqlite3"
    browser = Client()
    late_query = "/api/scientific-registry?cut=late&valid_at=2026-10-10"
    early_query = "/api/scientific-registry?cut=early&valid_at=2026-10-10"

    with running_beta(game_unused, science_only=True) as (port1, pid1):
        health = get(browser, port1, "/api/health")
        assert health["mode"] == "SYNTHETIC_SCIENCE_ONLY"
        assert health["accounts_enabled"] is False
        assert get(browser, port1, "/api/session", status=401)["science_only"] is True
        assert get(browser, port1, "/api/state", status=404) == {
            "error": "SCIENCE_ONLY_ROUTE_UNAVAILABLE"}
        _science_lab(browser, port1)
        original = get(browser, port1, late_query)
        original_sha = _receipt_sha(original)
        _intake(original, 0, valid=0, rejected=0)
        for fixture in ("sandbox_alpha_v1", "sandbox_beta_v1"):
            result = _enroll_from_separate_process(science_db, fixture)
            assert result["status"] == "SANDBOX_VALIDATED"
            assert result["real_source_admitted"] is False
        late = get(browser, port1, late_query)
        enrolled_sha = _receipt_sha(late)
        assert enrolled_sha != original_sha
        _intake(late, 2, valid=2, rejected=0)
        assert get(browser, port1, late_query)["snapshot_receipt_sha256"] == enrolled_sha
        early = get(browser, port1, early_query)
        _intake(early, 0, valid=0, rejected=0)
        assert get(browser, port1,
                   "/api/scientific-registry?cut=late&family=CHAIN"
                   )["snapshot"]["synthetic_intake"]["intake_count"] == 0
        status, error, _ = browser.request(
            port1, "POST", "/api/scientific-registry", payload={})
        assert status == 404 and error == {"error": "SCIENCE_ONLY_WRITE_UNAVAILABLE"}
        assert get(browser, port1,
                   "/api/scientific-registry?cut=nonsense",
                   status=400) == {"error": "INVALID_SYNTHETIC_REGISTRY_QUERY"}
        assert not game_unused.exists() and not account_db.exists()
        assert not (game_unused.parent / "accounts").exists()

    original_bytes_sha = hashlib.sha256(science_db.read_bytes()).hexdigest()
    with running_beta(game_unused, science_only=True) as (port2, pid2):
        assert pid1 != pid2
        assert get(browser, port2, "/api/health")["accounts_enabled"] is False
        assert get(browser, port2, "/api/session", status=401)["science_only"] is True
        _science_lab(browser, port2)
        persisted = get(browser, port2, late_query)
        assert _receipt_sha(persisted) == enrolled_sha
        assert persisted["snapshot"]["synthetic_intake"] == late["snapshot"]["synthetic_intake"]
        _intake(get(browser, port2, early_query), 0, valid=0, rejected=0)
        assert not game_unused.exists() and not account_db.exists()
    assert hashlib.sha256(science_db.read_bytes()).hexdigest() == original_bytes_sha
    assert {"registry_meta", "synthetic_intake_event"} <= _sqlite_tables(science_db)
    assert not {"account", "club", "account_session"} & _sqlite_tables(science_db)

    # Corrupt only a private disposable database, NEVER the verified original.
    copy_root = tmp_path / "science-only-corrupted-copy"
    copy_root.mkdir()
    copy_db = copy_root / REGISTRY_NAME
    shutil.copy2(science_db, copy_db)
    with sqlite3.connect(copy_db) as handle:
        handle.execute("DROP TRIGGER registry_distribution_immutable_update")
    with running_beta(copy_root / "unused.sqlite3", science_only=True) as (port3, _):
        assert get(browser, port3, late_query, status=503) == {
            "error": "SYNTHETIC_REGISTRY_UNAVAILABLE"}
        assert not (copy_root / "accounts.sqlite3").exists()
    assert hashlib.sha256(science_db.read_bytes()).hexdigest() == original_bytes_sha
