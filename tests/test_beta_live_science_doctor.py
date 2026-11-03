"""Live science-only beta diagnosis: bounded GETs and independent SHA audits.

The diagnostic itself is read-only. This test module alone creates disposable
SQLite source-generated fixtures and, for one smoke, a local synthetic server.
"""
from __future__ import annotations

from contextlib import closing
import copy
import http.client
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import parse_qsl, urlencode, urlsplit

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "diagnose_live_science_beta.py"
spec = importlib.util.spec_from_file_location("diagnose_live_science_beta", SCRIPT)
assert spec is not None and spec.loader is not None
doctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor)

from politics_fantasy.scientific_registry import query_registry  # noqa: E402
from politics_fantasy.scientific_integration_lab import report  # noqa: E402

ENV = {**os.environ, "PYTHONIOENCODING": "utf-8",
       "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(ROOT / "src")}


@pytest.fixture(scope="module")
def stable_lab():
    return report(cut="late", scenario="baseline")


@pytest.fixture()
def mocked_routes(tmp_path, stable_lab):
    data = tmp_path / "isolated-fixture" / "scientific.sqlite3"
    early = query_registry(data, cut="early", valid_at="2026-09-15",
                           family="all", published_until="as_of")
    late = query_registry(data, cut="late", valid_at="2026-09-15",
                          family="all", published_until="as_of")
    values = {
        "/api/session": (401, {
            "authenticated": False, "science_only": True,
            "error": "LOCAL_SCIENCE_ONLY",
        }),
        "/api/health": (200, {
            "ok": True, "mode": "SYNTHETIC_SCIENCE_ONLY",
            "accounts_enabled": False, "real_player_scoring": False,
        }),
        "/api/beta-readiness": (200, {
            "schema": "pfl.beta_readiness.v1",
            "ok": True,
            "local_runtime": {
                "status": "READY_FOR_LOCAL_PREFLIGHT",
                "scope": "LOOPBACK_SYNTHETIC_SCIENCE_ONLY",
                "checks": {
                    "loopback_binding": True, "web_assets_present": True,
                    "accounts_disabled_intentionally": True,
                },
                "anonymous_readiness_get": True,
                "full_user_journey_attested": False,
            },
            "scientific_admission": {
                "r5_status": "STOP_R5", "system20_valid_ab_cycles": 0,
                "empirical_study_eligible": False,
            },
            "public_release": {
                "status": "BLOCKED_PENDING_INDEPENDENT_ATTESTATION",
                "eligible": False, "gates_total": 6,
                "gates_with_attestation_records": 0,
                "public_hosting_authorized": False,
                "real_person_scoring": False,
            },
        }),
        "/api/scientific-integration-lab?cut=late&scenario=baseline":
            (200, copy.deepcopy(stable_lab)),
        "/api/scientific-registry?cut=early&valid_at=2026-09-15"
        "&family=all&published_until=as_of": (200, early),
        "/api/scientific-registry?cut=late&valid_at=2026-09-15"
        "&family=all&published_until=as_of": (200, late),
    }
    return values


def mocked_get(monkeypatch, routes):
    seen = []

    def get(port, route):
        seen.append((port, route))
        assert port == 49494
        return copy.deepcopy(routes[route])

    monkeypatch.setattr(doctor, "_get_json", get)
    return seen


def test_pass_independently_verifies_running_science_only_synthetic_snapshots(
    monkeypatch, mocked_routes,
):
    seen = mocked_get(monkeypatch, mocked_routes)
    result = doctor.diagnose(
        49494, doctor.parse_guest_recipe(None))
    assert list(route for _, route in seen) == list(mocked_routes)
    assert result == {
        "schema": doctor.SCHEMA, "status": "PASS",
        "evidence_class": "SYNTHETIC_LAB_ONLY",
        "comparison_kind": doctor.COMPARISON_KIND,
        "science_only": True,
        "early": {
            "sha256": mocked_routes[list(mocked_routes)[-2]][1][
                "snapshot_receipt"]["sha256"],
            "visible_public_descriptors": 2,
        },
        "late": {
            "sha256": mocked_routes[list(mocked_routes)[-1]][1][
                "snapshot_receipt"]["sha256"],
            "visible_public_descriptors": 6,
        },
        "R5": "STOP_R5", "release_gates_passed": 0,
        "scientific_ab_cycles": 0,
        "rights_for_public_display_admitted": False,
        "external_authenticity_certified": False,
        "publisher_identity_verified": False,
    }
    assert "source_id" not in json.dumps(result)
    assert "127.0.0.1" not in json.dumps(result)


@pytest.mark.parametrize("origin", [
    "http://localhost:8787",
    "http://127.0.0.1:0",
    "http://127.0.0.1:65536",
    "http://127.0.0.1:-1",
    "http://127.0.0.1",
    "https://127.0.0.1:8787",
    "http://127.0.0.1:8787/",
    "http://127.0.0.1:8787/?x=1",
    "http://127.0.0.1:8787/#x",
    "http://user:password@127.0.0.1:8787",
    "http://192.168.0.1:8787",
    "http://127.0.0.2:8787",
    "http://127.0.0.1:8787\r\nINJECTED_CANARY",
    "http://127.0.0.1:1;@evil.invalid:2",
])
def test_origin_rejected_without_network(monkeypatch, origin):
    monkeypatch.setattr(doctor, "_get_json", lambda *_:
                        pytest.fail("invalid origin must not attempt a GET"))
    with pytest.raises(doctor.DoctorError, match="ORIGIN_INVALID"):
        doctor.parse_origin(origin)


@pytest.mark.parametrize("guest_query", [
    "?pfl_guest=v1&cut=late",
    doctor.DEFAULT_QUERY + "&source_id=PRIVATE_CANARY",
    doctor.DEFAULT_QUERY + "&cut=early",
    doctor.DEFAULT_QUERY.replace("view=compare", "view=%GG"),
    doctor.DEFAULT_QUERY.replace("cut=late", "cut=early").replace(
        "published_until=as_of", "published_until=2026-10-30T12%3A00%3A00Z"),
    "https://127.0.0.1:8888/" + doctor.DEFAULT_QUERY,
    "http://actor.invalid:7777/" + doctor.DEFAULT_QUERY,
])
def test_untrusted_bookmark_is_rejected_before_network(monkeypatch, guest_query):
    monkeypatch.setattr(doctor, "_get_json", lambda *_:
                        pytest.fail("malformed guest query cannot fetch"))
    with pytest.raises(doctor.DoctorError, match="GUEST_QUERY_INVALID"):
        doctor.parse_guest_recipe(guest_query)


def test_relative_and_old_bookmark_are_normalized_using_real_launcher():
    relative = doctor.DEFAULT_QUERY.replace("view=compare", "view=sources")
    old = "http://127.0.0.1:64222/" + relative
    assert doctor.parse_guest_recipe(relative) == doctor.parse_guest_recipe(old)
    assert doctor.parse_guest_recipe(old)["view"] == "sources"


@pytest.mark.parametrize("view", (
    "chain", "chronicle", "episodes", "admission", "intake", "quality",
))
def test_running_science_doctor_accepts_existing_public_institutional_subview(view):
    # The same versioned seven-field recipe must be usable by browser,
    # dynamic-port launcher and GET-only running-instance verifier.
    recipe = doctor.DEFAULT_QUERY.replace("view=compare", "view=" + view)
    parsed = doctor.parse_guest_recipe(
        "http://127.0.0.1:49881/" + recipe
    )
    assert parsed["view"] == view
    assert parsed["cut"] == "late"
    assert parsed["family"] == "all"
    assert parsed["published_until"] == "as_of"


@pytest.mark.parametrize("view", (
    "sources", "compare", "chain", "chronicle",
    "episodes", "admission", "intake", "quality",
))
def test_opt_in_verified_url_rebases_all_eight_views_with_canonical_keys(view):
    # An old loopback origin, mixed input key order and existing case-sensitive
    # enum values must become exactly the original seven-key canonical recipe.
    fields = {
        "view": view, "scenario": "privacy_probe",
        "published_until": "2026-09-19T12:00:00Z",
        "family": "CHAIN", "valid_at": "2026-10-10",
        "cut": "early", "pfl_guest": "v1",
    }
    old = "http://127.0.0.1:54321/?" + urlencode(list(fields.items()))
    parsed = doctor.parse_guest_recipe(old)
    rebound = doctor.verified_guest_url(49494, parsed)
    assert rebound.startswith("http://127.0.0.1:49494/?")
    assert "54321" not in rebound
    split = urlsplit(rebound)
    assert split.path == "/" and not split.fragment
    assert tuple(parse_qsl(split.query, strict_parsing=True)) == tuple(
        (key, fields[key]) for key in doctor.run_demo.GUEST_QUERY_KEYS)
    assert split.query == urlencode([
        (key, fields[key]) for key in doctor.run_demo.GUEST_QUERY_KEYS
    ])
    assert len(parse_qsl(split.query)) == 7
    assert "published_until=2026-09-19T12%3A00%3A00Z" in split.query


def test_opt_in_cli_emits_verified_link_only_after_complete_synthetic_pass(
    monkeypatch, mocked_routes, capsys,
):
    seen = mocked_get(monkeypatch, mocked_routes)
    old = "http://127.0.0.1:54321/" + doctor.DEFAULT_QUERY
    rc = doctor.main([
        "--origin", "http://127.0.0.1:49494",
        "--guest-query", old,
        "--emit-verified-guest-url",
    ])
    output = capsys.readouterr()
    assert rc == 0 and output.err == ""
    assert output.out.count("\n") == 1
    result = json.loads(output.out)
    assert result["status"] == "PASS"
    assert result["R5"] == "STOP_R5"
    assert len(seen) == len(mocked_routes), "Do not emit before final SHA verified GET"
    assert result["verified_guest_url"] == (
        "http://127.0.0.1:49494/?" +
        doctor.run_demo.resume_guest_query(doctor.DEFAULT_QUERY))
    assert "54321" not in output.out
    assert "source_id" not in output.out
    assert result["rights_for_public_display_admitted"] is False


def test_cli_default_pass_keeps_identical_private_json_contract(
    monkeypatch, mocked_routes, capsys,
):
    mocked_get(monkeypatch, mocked_routes)
    rc = doctor.main([
        "--origin", "http://127.0.0.1:49494",
        "--guest-query", doctor.DEFAULT_QUERY,
    ])
    output = capsys.readouterr()
    assert rc == 0 and output.err == ""
    result = json.loads(output.out)
    assert result["status"] == "PASS"
    assert "verified_guest_url" not in result
    assert "127.0.0.1" not in output.out and "49494" not in output.out
    assert result == doctor.diagnose(49494, doctor.parse_guest_recipe(None))


@pytest.mark.parametrize("failure", (
    "HTTP_400", "HTTP_503", "SHA", "ACCOUNT", "SERVER_UNAVAILABLE",
))
def test_opt_in_never_emits_url_when_verification_fails(
    monkeypatch, mocked_routes, capsys, failure,
):
    endpoint = next(key for key in mocked_routes
                    if key.startswith("/api/scientific-registry?cut=late"))
    if failure == "HTTP_400":
        mocked_routes[endpoint] = (400, None)
    elif failure == "HTTP_503":
        mocked_routes[endpoint] = (503, None)
    elif failure == "SHA":
        mocked_routes[endpoint][1]["snapshot_receipt"]["sha256"] = "0" * 64
    elif failure == "ACCOUNT":
        mocked_routes["/api/session"] = (200, {"authenticated": True})
    else:
        monkeypatch.setattr(doctor, "_get_json", lambda *_: (
            _ for _ in ()).throw(doctor.DoctorError("SERVER_UNAVAILABLE")))
    if failure != "SERVER_UNAVAILABLE":
        mocked_get(monkeypatch, mocked_routes)
    rc = doctor.main([
        "--origin", "http://127.0.0.1:49494",
        "--guest-query", doctor.DEFAULT_QUERY,
        "--emit-verified-guest-url",
    ])
    output = capsys.readouterr()
    assert rc == 1 and output.err == ""
    result = json.loads(output.out)
    assert result["status"] == "FAIL"
    assert "verified_guest_url" not in result
    assert "http://127.0.0.1:49494" not in output.out


@pytest.mark.parametrize("invalid", (
    "--unknown-flag", "--origin", "http://evil.invalid:49494",
))
def test_opt_in_rejects_invalid_arguments_without_url(invalid, capsys):
    argv = ["--origin", "http://127.0.0.1:49494",
            "--emit-verified-guest-url"]
    if invalid == "--unknown-flag":
        argv += [invalid]
    elif invalid == "--origin":
        argv = ["--emit-verified-guest-url"]
    else:
        argv = ["--origin", invalid, "--emit-verified-guest-url"]
    rc = doctor.main(argv)
    output = capsys.readouterr()
    assert rc == 1 and output.err == ""
    body = json.loads(output.out)
    assert body["status"] == "FAIL"
    assert "verified_guest_url" not in body


@pytest.mark.parametrize("field,value,error", [
    ("/api/session", {"authenticated": True}, "SCIENCE_ONLY_REQUIRED"),
    ("/api/session", {"science_only": False}, "SCIENCE_ONLY_REQUIRED"),
    ("/api/health", {"accounts_enabled": True}, "SCIENCE_ONLY_REQUIRED"),
    ("/api/beta-readiness", {
        "scientific_admission": {"r5_status": "RELEASED"},
    }, "READINESS_UNVERIFIED"),
    ("/api/beta-readiness", {
        "public_release": {"gates_with_attestation_records": 1},
    }, "READINESS_UNVERIFIED"),
    ("/api/scientific-integration-lab?cut=late&scenario=baseline", {
        "real_corpus_ingestion_allowed": True,
    }, "LAB_UNVERIFIED"),
    ("/api/scientific-integration-lab?cut=late&scenario=baseline", {
        "explorer": {"admission": {
            "real_distribution_rights_admitted": True,
        }},
    }, "LAB_UNVERIFIED"),
    ("/api/scientific-integration-lab?cut=late&scenario=baseline", {
        "rights": {"reuse_admitted": True},
    }, "LAB_UNVERIFIED"),
    ("/api/scientific-integration-lab?cut=late&scenario=baseline", {
        "explorer": {"observatory": {
            "real_actor_identity_verified": True,
        }},
    }, "LAB_UNVERIFIED"),
])
def test_fake_mode_rights_or_gates_fail_closed(
    monkeypatch, mocked_routes, field, value, error,
):
    status, payload = mocked_routes[field]
    assert isinstance(payload, dict)
    if field == "/api/session":
        payload.update(value)
    else:
        for key, replacement in value.items():
            if isinstance(replacement, dict) and isinstance(payload.get(key), dict):
                for sub_key, sub_value in replacement.items():
                    if isinstance(sub_value, dict) and isinstance(payload[key].get(sub_key), dict):
                        payload[key][sub_key].update(sub_value)
                    else:
                        payload[key][sub_key] = sub_value
            else:
                payload[key] = replacement
    mocked_routes[field] = (status, payload)
    mocked_get(monkeypatch, mocked_routes)
    with pytest.raises(doctor.DoctorError, match=error):
        doctor.diagnose(49494, doctor.parse_guest_recipe(None))


def test_forged_sha_and_rights_or_fictional_identity_never_pass(
    monkeypatch, mocked_routes,
):
    endpoint = next(key for key in mocked_routes
                    if key.startswith("/api/scientific-registry?cut=late"))
    originals = copy.deepcopy(mocked_routes)
    attacks = [
        lambda x: x["snapshot_receipt"].update(sha256="0" * 64),
        lambda x: x["registry"].update(private_source_ids_exposed=True),
        lambda x: x["registry"]["distributions"][0].update(
            real_publisher_authenticated=True),
        lambda x: x.update(cut="early"),
        lambda x: x.update(as_of="2026-10-15T12:00:00Z"),
        lambda x: x["models"].update(empirical_model_admitted=True),
        lambda x: x["models"].update(real_actor_identity_verified=True),
        lambda x: x["registry"].update(real_source_rows_admitted=True),
        lambda x: x.update(snapshot_receipt_sha256="f" * 64),
        lambda x: x["registry"].update(schema_version=5),
    ]
    for attack in attacks:
        mocked_routes.clear()
        mocked_routes.update(copy.deepcopy(originals))
        attack(mocked_routes[endpoint][1])
        mocked_get(monkeypatch, mocked_routes)
        with pytest.raises(doctor.DoctorError, match="RECEIPT_UNVERIFIED"):
            doctor.diagnose(49494, doctor.parse_guest_recipe(None))


@pytest.mark.parametrize("status,endpoint,expected", [
    (400, "/api/scientific-registry?cut=early&valid_at=2026-09-15"
     "&family=all&published_until=as_of", "HTTP_400_INVALID_QUERY"),
    (503, "/api/scientific-registry?cut=late&valid_at=2026-09-15"
     "&family=all&published_until=as_of", "HTTP_503_REGISTRY_UNAVAILABLE"),
    (503, "/api/scientific-integration-lab?cut=late&scenario=baseline",
     "HTTP_503_LAB_UNAVAILABLE"),
    (503, "/api/beta-readiness", "HTTP_503_READINESS_UNAVAILABLE"),
])
def test_stable_http_failure_categories(
    monkeypatch, mocked_routes, status, endpoint, expected,
):
    mocked_routes[endpoint] = (status, None)
    mocked_get(monkeypatch, mocked_routes)
    with pytest.raises(doctor.DoctorError, match=expected):
        doctor.diagnose(49494, doctor.parse_guest_recipe(None))


class FakeResponse:
    def __init__(self, payload: bytes, status: int = 200, *,
                 content_length: str | None = None):
        self._payload = payload
        self.status = status
        self.length = content_length

    def getheader(self, key: str, default: str = "") -> str | None:
        if key == "Content-Type":
            return "application/json"
        if key == "Content-Length":
            return self.length
        return default

    def read(self, limit: int) -> bytes:
        return self._payload[:limit]


class FakeConnection:
    def __init__(self, response: FakeResponse, port: int, timeout: float):
        self.response = response
        self.port = port
        self.timeout = timeout
        self.calls = []

    def request(self, method: str, path: str, headers: dict) -> None:
        self.calls.append((method, path, headers))

    def getresponse(self) -> FakeResponse:
        return self.response

    def close(self) -> None:
        return


@pytest.mark.parametrize("body,error", [
    (b'{"x":1,"x":2}', "RESPONSE_INVALID"),
    (b'{"x":NaN}', "RESPONSE_INVALID"),
    (b'{"x":Infinity}', "RESPONSE_INVALID"),
    (b'{"x":1e999}', "RESPONSE_INVALID"),
    (b'{"x":', "RESPONSE_INVALID"),
    (b'{' + b'a' * (doctor.MAX_RESPONSE_BYTES + 1),
     "RESPONSE_TOO_LARGE"),
], ids=["duplicate", "nan", "infinity", "exponent-overflow",
        "truncated", "oversize"])
def test_response_is_bounded_and_rejects_duplicate_nonfinite_json(
    monkeypatch, body, error,
):
    holder = []

    def make_conn(_host, port, timeout):
        conn = FakeConnection(FakeResponse(body), port, timeout)
        holder.append(conn)
        return conn

    monkeypatch.setattr(doctor.http.client, "HTTPConnection", make_conn)
    with pytest.raises(doctor.DoctorError, match=error):
        doctor._get_json(48484, "/api/health")
    assert len(holder) == 1
    assert holder[0].timeout < 2.0
    assert holder[0].calls[0][0] == "GET"
    assert holder[0].calls[0][1] == "/api/health"
    assert "Authorization" not in holder[0].calls[0][2]


def test_no_redirect_or_remote_fetch(monkeypatch):
    calls = []

    def conn(_host, port, timeout):
        calls.append((port, timeout))
        return FakeConnection(FakeResponse(b"", status=302), port, timeout)

    monkeypatch.setattr(doctor.http.client, "HTTPConnection", conn)
    with pytest.raises(doctor.DoctorError, match="SERVER_UNAVAILABLE"):
        doctor._required(8787, "/api/beta-readiness", kind="readiness")
    assert calls == [(8787, doctor.CONNECT_TIMEOUT_SECONDS)]


def test_cli_prints_only_one_safe_json_line_and_returns_exit1(
    monkeypatch, capsys,
):
    monkeypatch.setattr(doctor, "_get_json", lambda *_:
                        (_ for _ in ()).throw(doctor.DoctorError(
                            "SERVER_UNAVAILABLE")))
    rc = doctor.main([
        "--origin", "http://127.0.0.1:4422",
        "--guest-query", doctor.DEFAULT_QUERY,
    ])
    captured = capsys.readouterr()
    assert rc == 1
    assert captured.err == ""
    assert captured.out.count("\n") == 1
    result = json.loads(captured.out)
    assert result == {
        "schema": doctor.SCHEMA, "status": "FAIL",
        "error_code": "SERVER_UNAVAILABLE",
    }
    assert "4422" not in captured.out


def test_real_running_science_only_beta_is_verified_over_http(tmp_path):
    """Only this test launches a disposable beta; the doctor never launches it."""
    db = tmp_path / "fixture_only" / "science.sqlite3"
    server = subprocess.Popen([
        sys.executable, "-B", str(ROOT / "run_demo.py"),
        "--science-only", "--port", "0", "--db", str(db),
    ], cwd=ROOT, env=ENV, stdout=subprocess.PIPE,
       stderr=subprocess.PIPE, text=True, encoding="utf-8")
    try:
        first = server.stdout.readline()
        match = re.search(r"http://127\.0\.0\.1:(\d+)", first)
        assert match is not None
        port = int(match.group(1))
        result = subprocess.run([
            sys.executable, "-B", str(SCRIPT),
            "--origin", f"http://127.0.0.1:{port}",
        ], cwd=tmp_path, env=ENV, capture_output=True,
            text=True, encoding="utf-8", timeout=15, check=False)
        assert result.returncode == 0, result.stdout
        assert result.stderr == ""
        assert result.stdout.count("\n") == 1
        summary = json.loads(result.stdout)
        assert summary["status"] == "PASS"
        assert summary["early"]["visible_public_descriptors"] == 2
        assert summary["late"]["visible_public_descriptors"] == 6
        assert summary["R5"] == "STOP_R5"
        assert summary["rights_for_public_display_admitted"] is False
        assert len(summary["early"]["sha256"]) == 64
        assert len(summary["late"]["sha256"]) == 64
        assert f"127.0.0.1:{port}" not in result.stdout
        # A bookmarked old loopback URL is a filter recipe only, not a
        # second origin. The same LIVE server must check new selected clocks,
        # new scientific scenario, and both SHA receipts independently.
        old_bookmark = (
            "http://127.0.0.1:45678/?pfl_guest=v1&cut=early"
            "&valid_at=2026-10-10&family=all"
            "&published_until=2026-09-19T12%3A00%3A00Z"
            "&scenario=privacy_probe&view=compare"
        )
        restored = subprocess.run([
            sys.executable, "-B", str(SCRIPT),
            "--origin", f"http://127.0.0.1:{port}",
            "--guest-query", old_bookmark,
        ], cwd=tmp_path, env=ENV, capture_output=True,
            text=True, encoding="utf-8", timeout=15, check=False)
        assert restored.returncode == 0, restored.stdout
        selected = json.loads(restored.stdout)
        assert selected["status"] == "PASS"
        assert selected["early"]["visible_public_descriptors"] == 2
        assert selected["late"]["visible_public_descriptors"] == 2
        assert selected["early"]["sha256"] != summary["early"]["sha256"]
        assert selected["late"]["sha256"] != summary["late"]["sha256"]
        assert "45678" not in restored.stdout
        assert not db.exists()
        assert not (db.parent / "accounts.sqlite3").exists()
        assert (db.parent / "scientific_registry_synthetic.sqlite3").exists()
        # Confirm that only the server's synthetic registry fixture was
        # created; doctor never creates an additional account/game DB.
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)
        if server.stdout:
            server.stdout.close()
        if server.stderr:
            server.stderr.close()
