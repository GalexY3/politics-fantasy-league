"""Real process and OS-port tests for the read-only S9 live science doctor.

The doctor is a *consumer*: this test never imports or invokes its functions
in-process, starts no browser, and never alters its implementation. The only
persisted data are disposable, author-closed synthetic S9 fixtures in tmp_path.
"""
from __future__ import annotations

from contextlib import closing, contextmanager
import hashlib
import http.client
import json
import os
from pathlib import Path
from queue import Empty, Queue
import re
import shutil
import subprocess
import sys
from threading import Thread
import time
from urllib.parse import parse_qsl, urlencode, urlsplit

import pytest


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "run_demo.py"
DOCTOR = ROOT / "scripts" / "diagnose_live_science_beta.py"
ENV = {
    **os.environ,
    "PYTHONIOENCODING": "utf-8",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONPATH": str(ROOT / "src"),
}
CANONICAL_PAIRS = (
    ("pfl_guest", "v1"),
    ("cut", "early"),
    ("valid_at", "2026-10-10"),
    ("family", "CHAIN"),
    ("published_until", "2026-09-19T12:00:00Z"),
    ("scenario", "baseline"),
    ("view", "compare"),
)
CANONICAL_QUERY = urlencode(CANONICAL_PAIRS)
FIRST_BANNER = re.compile(
    r"\APolitics Fantasy League · CIENCIA SINTÉTICA SIN CUENTAS"
    r" · http://127\.0\.0\.1:([0-9]{1,5})\Z"
)
ACCOUNT_BANNER = re.compile(
    r"\APolitics Fantasy League · DEMO SINTÉTICA"
    r" · http://127\.0\.0\.1:([0-9]{1,5})\Z"
)
SECOND_BANNER = re.compile(
    r"\AREANUDAR CONSULTA CIENTÍFICA · "
    r"(http://127\.0\.0\.1:[0-9]{1,5}/\?[^\s]+)\Z"
)


class RealScienceProcess:
    """Read a child's first two banners without a blocking stdout.readline."""

    def __init__(self, db: Path, *, resume: str | None = None,
                 science_only: bool = True):
        self.db = db
        self.resume = resume
        self.science_only = science_only
        args = [sys.executable, "-B", "-u", str(LAUNCHER)]
        if science_only:
            args.append("--science-only")
        args.extend(("--port", "0", "--db", str(db)))
        if resume is not None:
            args.extend(("--resume-guest-query", resume))
        self.process = subprocess.Popen(
            args, cwd=ROOT, env=ENV, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            encoding="utf-8", errors="replace", text=True,
        )
        self.messages: Queue[str] = Queue(maxsize=8)
        self.reader = Thread(target=self._read, daemon=True)
        self.reader.start()
        self.port: int | None = None
        self.origin: str | None = None
        self.resumed_url: str | None = None

    def _read(self) -> None:
        assert self.process.stdout is not None
        for text_line in self.process.stdout:
            line = text_line.strip()
            if (line.startswith("Politics Fantasy League · ")
                    or line.startswith("REANUDAR CONSULTA CIENTÍFICA · ")):
                try:
                    self.messages.put_nowait(line[:1500])
                except Exception:
                    return

    def _banner(self, timeout: float = 10.0) -> str:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                pytest.fail("LAUNCHER_EXITED_BEFORE_PUBLIC_BANNER")
            try:
                return self.messages.get(timeout=min(0.1, deadline - time.monotonic()))
            except Empty:
                continue
        pytest.fail("LAUNCHER_BANNER_TIMEOUT")

    def ready(self) -> "RealScienceProcess":
        first = self._banner()
        match = (FIRST_BANNER if self.science_only else ACCOUNT_BANNER).fullmatch(first)
        assert match, "Unexpected science-only first banner"
        self.port = int(match.group(1))
        assert 0 < self.port <= 65535
        self.origin = f"http://127.0.0.1:{self.port}"
        if self.resume is not None:
            second = self._banner()
            matched = SECOND_BANNER.fullmatch(second)
            assert matched, "Unexpected or non-canonical resume banner"
            self.resumed_url = matched.group(1)
            split = urlsplit(self.resumed_url)
            assert split.scheme == "http"
            assert split.netloc == f"127.0.0.1:{self.port}"
            assert split.path == "/" and not split.fragment
            assert tuple(parse_qsl(split.query, keep_blank_values=True)) == CANONICAL_PAIRS
            assert "@" not in self.resumed_url
        # The launcher prints its public banner after bind() but immediately
        # before serve_forever(). Do not race an external doctor subprocess
        # against that final scheduler hand-off. Probe only real loopback 401.
        deadline = time.monotonic() + 8.0
        available = False
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                pytest.fail("LAUNCHER_EXITED_BEFORE_LISTEN")
            try:
                with closing(http.client.HTTPConnection(
                        "127.0.0.1", self.port, timeout=0.7)) as connection:
                    connection.request("GET", "/api/session")
                    response = connection.getresponse()
                    body = json.loads(response.read().decode("utf-8"))
                if (response.status == 401
                        and body.get("authenticated") is False
                        and (body.get("science_only") is True
                             if self.science_only
                             else body.get("science_only") is not True)):
                    available = True
                    break
            except (OSError, TimeoutError, ValueError,
                    http.client.HTTPException):
                pass
            time.sleep(0.06)
        assert available, "LAUNCHER_PUBLIC_SESSION_NOT_READY"
        return self

    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        if self.process.stdout is not None:
            self.process.stdout.close()
        self.reader.join(timeout=1)


@contextmanager
def science_server(db: Path, *, resume: str | None = None,
                   science_only: bool = True):
    server = RealScienceProcess(db, resume=resume, science_only=science_only)
    try:
        yield server.ready()
    finally:
        server.stop()


def run_doctor(origin: str, *, guest_query: str | None = None,
               emit_verified_guest_url: bool = False,
               timeout: float = 25.0) -> tuple[int, dict]:
    args = [
        sys.executable, "-B", str(DOCTOR), "--origin", origin,
    ]
    if guest_query is not None:
        args.extend(("--guest-query", guest_query))
    if emit_verified_guest_url:
        args.append("--emit-verified-guest-url")
    process = subprocess.run(
        args, cwd=ROOT, env=ENV, stdin=subprocess.DEVNULL,
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout, check=False,
    )
    assert not process.stderr, "The doctor must not expose traces or paths"
    assert len(process.stdout) < 20_000, "The doctor must emit bounded JSON"
    assert process.stdout.count("\n") <= 2
    payload = json.loads(process.stdout)
    assert type(payload) is dict and payload.get("status") in ("PASS", "FAIL")
    assert "synthetic_registry_synthetic.sqlite3" not in process.stdout
    assert "SECRET_CANARY" not in process.stdout
    assert "SYN:CHAIN_" not in process.stdout
    return process.returncode, payload


def _require_synthetic_stop(payload: dict) -> None:
    assert payload["schema"] == "pfl.synthetic_live_science_beta_diagnostic.v1"
    assert payload["science_only"] is True
    assert payload["evidence_class"] == "SYNTHETIC_LAB_ONLY"
    assert payload["comparison_kind"] == (
        "AUTHOR_STIPULATED_SNAPSHOT_VISIBILITY_NOT_REAL_CHANGE"
    )
    assert payload["R5"] == "STOP_R5"
    assert payload["release_gates_passed"] == 0
    assert payload["scientific_ab_cycles"] == 0
    assert payload["rights_for_public_display_admitted"] is False
    assert payload["publisher_identity_verified"] is False


def _source_digests(payload: dict) -> tuple[str, str]:
    """Extract public aggregate receipts only, never raw source IDs or rows."""
    early, late = payload["early"], payload["late"]
    assert type(early) is dict and type(late) is dict
    pattern = re.compile(r"[a-f0-9]{64}\Z")
    a, b = early["sha256"], late["sha256"]
    assert type(a) is str and pattern.fullmatch(a)
    assert type(b) is str and pattern.fullmatch(b)
    assert early["visible_public_descriptors"] == 1
    assert late["visible_public_descriptors"] == 1
    return a, b


def test_doctor_real_process_stopped_port_and_rebound_guest_link(tmp_path):
    """No success against a dead socket; recovery requires a new bound port."""
    db = tmp_path / "science" / "science.db"
    assert not db.exists()
    assert DOCTOR.is_file(), "The independent doctor must already be installed"

    with science_server(db) as first:
        assert first.origin is not None
        old_origin = first.origin
        old_port = first.port
        old_guest_url = f"{old_origin}/?{CANONICAL_QUERY}"
        code, before = run_doctor(old_origin, guest_query=old_guest_url)
        assert code == 0 and before["status"] == "PASS", before.get("error_code")
        _require_synthetic_stop(before)
        assert "verified_guest_url" not in before
        code, linked_before = run_doctor(
            old_origin, guest_query=old_guest_url,
            emit_verified_guest_url=True)
        assert code == 0 and linked_before["status"] == "PASS"
        assert linked_before["verified_guest_url"] == old_guest_url
        assert _source_digests(linked_before) == _source_digests(before)
        before_digests = _source_digests(before)
        before_counts = (
            before["early"]["visible_public_descriptors"],
            before["late"]["visible_public_descriptors"],
        )
        scientific_sqlite = db.parent / "scientific_registry_synthetic.sqlite3"
        assert scientific_sqlite.is_file()
        sqlite_sha = hashlib.sha256(scientific_sqlite.read_bytes()).hexdigest()
        assert not db.exists(), "Science-only launcher must not create a Fantasy game DB"
        assert not (db.parent / "accounts.sqlite3").exists()

    # A stopped process's OLD origin must never yield a stale PASS. No browser
    # or old URL cache may make an unavailable local server look live.
    stopped_code, stopped = run_doctor(
        old_origin, guest_query=old_guest_url, emit_verified_guest_url=True)
    assert stopped_code != 0 and stopped["status"] == "FAIL"
    assert stopped["error_code"] == "SERVER_UNAVAILABLE"
    assert "verified_guest_url" not in stopped
    assert not (db.parent / "accounts.sqlite3").exists()

    with science_server(db, resume=old_guest_url) as second:
        assert second.port is not None and second.resumed_url
        assert second.origin is not None
        assert second.resumed_url.startswith(f"{second.origin}/?")
        assert urlsplit(second.resumed_url).query == CANONICAL_QUERY
        assert second.port != old_port, "This runtime test requires a re-bound dynamic port"
        assert second.origin != old_origin
        code, after = run_doctor(second.origin, guest_query=old_guest_url)
        assert code == 0 and after["status"] == "PASS", after.get("error_code")
        assert "verified_guest_url" not in after
        code, linked_after = run_doctor(
            second.origin, guest_query=old_guest_url,
            emit_verified_guest_url=True)
        assert code == 0 and linked_after["status"] == "PASS"
        assert linked_after["verified_guest_url"] == (
            f"{second.origin}/?{CANONICAL_QUERY}")
        assert tuple(parse_qsl(urlsplit(linked_after["verified_guest_url"]).query)) == CANONICAL_PAIRS
        assert _source_digests(linked_after) == _source_digests(after)
        _require_synthetic_stop(after)
        assert _source_digests(after) == before_digests
        assert (
            after["early"]["visible_public_descriptors"],
            after["late"]["visible_public_descriptors"],
        ) == before_counts
        assert hashlib.sha256(scientific_sqlite.read_bytes()).hexdigest() == sqlite_sha
        assert not db.exists()
        assert not (db.parent / "accounts.sqlite3").exists()
        assert not (db.parent / "accounts").exists()


@pytest.mark.parametrize("url", (
    "https://127.0.0.1:32567",
    "http://198.51.100.1:32567",
    "http://example.invalid:32567",
    "http://127.0.0.1:32567/api/state",
    "http://user:SECRET_CANARY@127.0.0.1:32567",
))
def test_doctor_refuses_remote_credentials_https_or_unknown_path_without_network(
        tmp_path, url):
    assert DOCTOR.is_file()
    code, body = run_doctor(
        url, guest_query=f"http://127.0.0.1:54732/?{CANONICAL_QUERY}",
        emit_verified_guest_url=True)
    assert code != 0 and body["status"] == "FAIL"
    assert "verified_guest_url" not in body
    assert body.get("public_release_eligible") is not True
    assert not list(tmp_path.iterdir()), "Invalid origin must not create local files"


@pytest.mark.parametrize("bad_guest_recipe", (
    f"?{CANONICAL_QUERY}&rights_for_public_display_admitted=true",
    f"?{CANONICAL_QUERY}&cut=late",
    f"http://example.invalid:48000/?{CANONICAL_QUERY}",
    f"?{CANONICAL_QUERY.replace('family=CHAIN', 'family=REAL_PEOPLE')}",
    f"?{CANONICAL_QUERY.replace('view=compare', 'view=account')}",
))
def test_doctor_rejects_bad_guest_recipe_before_attempting_any_connection(
        tmp_path, bad_guest_recipe):
    assert DOCTOR.is_file()
    # Port 1 is deliberately not started here. GUEST_QUERY_INVALID, rather
    # than SERVER_UNAVAILABLE, proves selection validation precedes I/O.
    code, body = run_doctor(
        "http://127.0.0.1:1", guest_query=bad_guest_recipe,
        emit_verified_guest_url=True)
    assert code == 1 and body["status"] == "FAIL"
    assert "verified_guest_url" not in body
    assert body["error_code"] == "GUEST_QUERY_INVALID"
    assert not list(tmp_path.iterdir())


def test_doctor_default_query_still_requires_verified_read_only_science(tmp_path):
    db = tmp_path / "default-query" / "science.db"
    with science_server(db) as server:
        assert server.origin
        code, payload = run_doctor(server.origin)
        assert code == 0 and payload["status"] == "PASS"
        _require_synthetic_stop(payload)
        assert payload["early"]["visible_public_descriptors"] == 2
        assert payload["late"]["visible_public_descriptors"] == 6
        assert "verified_guest_url" not in payload
        code, linked = run_doctor(
            server.origin, emit_verified_guest_url=True)
        assert code == 0 and linked["status"] == "PASS"
        assert linked["verified_guest_url"] == (
            f"{server.origin}/?" + urlencode((
                ("pfl_guest", "v1"), ("cut", "late"),
                ("valid_at", "2026-09-15"), ("family", "all"),
                ("published_until", "as_of"), ("scenario", "baseline"),
                ("view", "compare"))))
        assert not db.exists()
        assert not (db.parent / "accounts.sqlite3").exists()


def test_doctor_rejects_a_real_account_enabled_server(tmp_path):
    """A real Fantasy session-capable endpoint must not masquerade as S9 guest."""
    db = tmp_path / "isolated-account-mode" / "game.db"
    with science_server(db, science_only=False) as account_server:
        assert account_server.origin is not None
        code, diagnosis = run_doctor(
            account_server.origin, emit_verified_guest_url=True)
        assert code != 0 and diagnosis["status"] == "FAIL"
        assert diagnosis["error_code"] == "SCIENCE_ONLY_REQUIRED"
        assert "verified_guest_url" not in diagnosis
        # Account DB exists only in this isolated *negative-control* fixture.
        assert (db.parent / "accounts.sqlite3").exists()


def test_doctor_fails_closed_on_tampered_copy_of_synthetic_registry(tmp_path):
    """A corrupt copy is not evidence; the legitimate registry is unchanged."""
    trusted_db = tmp_path / "clean" / "science.db"
    with science_server(trusted_db) as clean:
        assert clean.origin
        code, healthy = run_doctor(
            clean.origin, guest_query=f"{clean.origin}/?{CANONICAL_QUERY}")
        assert code == 0 and healthy["status"] == "PASS", healthy.get("error_code")
        original = trusted_db.parent / "scientific_registry_synthetic.sqlite3"
        original_hash = hashlib.sha256(original.read_bytes()).hexdigest()

    tampered_root = tmp_path / "corrupted-copy"
    tampered_root.mkdir()
    damaged = tampered_root / "scientific_registry_synthetic.sqlite3"
    shutil.copy2(original, damaged)
    with damaged.open("r+b") as handle:
        handle.write(b"NOT_AN_AUTHORED_SQLITE_FILE")
    assert hashlib.sha256(damaged.read_bytes()).hexdigest() != original_hash
    with science_server(tampered_root / "science.db") as compromised:
        assert compromised.origin
        code, failed = run_doctor(
            compromised.origin,
            guest_query=f"{compromised.origin}/?{CANONICAL_QUERY}",
            emit_verified_guest_url=True)
        assert code != 0 and failed["status"] == "FAIL"
        assert failed["error_code"] == "HTTP_503_REGISTRY_UNAVAILABLE"
        assert "verified_guest_url" not in failed
    assert hashlib.sha256(original.read_bytes()).hexdigest() == original_hash
    assert not (trusted_db.parent / "accounts.sqlite3").exists()
    assert not (tampered_root / "accounts.sqlite3").exists()
