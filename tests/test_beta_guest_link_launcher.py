"""Bounded guest-only URL handoff; synthetic observations, no accounts or browser."""
from __future__ import annotations

from contextlib import closing
import http.client
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import parse_qsl, urlencode, urlsplit

import pytest

import run_demo


ROOT = Path(run_demo.__file__).resolve().parent
SCRIPT = ROOT / "run_demo.py"
GUEST_FIELDS = (
    ("pfl_guest", "v1"),
    ("cut", "late"),
    ("valid_at", "2026-09-15"),
    ("family", "all"),
    ("published_until", "as_of"),
    ("scenario", "baseline"),
    ("view", "sources"),
)
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8",
       "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(ROOT / "src")}


def recipe(**changes: str) -> str:
    fields = dict(GUEST_FIELDS)
    fields.update(changes)
    return "?" + urlencode(list(fields.items()))


def cli(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPT), *args],
        cwd=cwd, env=ENV, capture_output=True,
        text=True, encoding="utf-8", errors="replace", timeout=15,
        check=False,
    )


def request(port: int, route: str) -> tuple[int, dict]:
    with closing(http.client.HTTPConnection("127.0.0.1", port, timeout=12)) as client:
        client.request("GET", route)
        response = client.getresponse()
        return response.status, json.loads(response.read().decode("utf-8"))


@pytest.mark.parametrize("value,expected", [
    (recipe(), recipe()[1:]),
    ("http://127.0.0.1:65535/" + recipe(), recipe()[1:]),
    ("http://localhost:3210/" + recipe(), recipe()[1:]),
    (recipe(cut="early", valid_at="2026-10-10", family="CHAIN",
            published_until="2026-09-19T12:00:00Z",
            scenario="privacy_probe", view="compare"),
     recipe(cut="early", valid_at="2026-10-10", family="CHAIN",
            published_until="2026-09-19T12:00:00Z",
            scenario="privacy_probe", view="compare")[1:]),
])
def test_url_parser_rebinds_only_allowlisted_seven_fields(value, expected):
    assert run_demo.resume_guest_query(value) == expected
    assert list(dict(parse_qsl(expected)).keys()) == [key for key, _ in GUEST_FIELDS]
    assert "localhost" not in expected and "127.0.0.1" not in expected


@pytest.mark.parametrize("institutional_view", (
    "chain", "chronicle", "episodes", "admission", "intake", "quality",
))
def test_guest_link_preserves_public_institutional_subview(institutional_view):
    """PREPATCH: source-local institutional tabs became 'sources' on reload.

    The launcher must accept the same exact seven-filter URL that the real
    guest browser can bookmark; no new field, private source ID or receipt.
    """
    bookmarked = recipe(
        cut="early", valid_at="2026-10-10", family="all",
        published_until="2026-09-19T12:00:00Z",
        view=institutional_view,
    )
    expected = bookmarked[1:]
    assert run_demo.resume_guest_query(
        "http://127.0.0.1:41552/" + bookmarked
    ) == expected


def test_out_of_order_encoded_fields_are_normalized_once_without_stale_origin():
    query = recipe(cut="early", family="PP04", scenario="rights_spoof")
    entries = list(reversed(query[1:].split("&")))
    encoded_key = entries.pop()  # encode pfl_guest key to test decoded-key logic
    assert encoded_key.startswith("pfl_guest=")
    entries.append("%70fl_guest=v1")
    original = "http://127.0.0.1:4242/?" + "&".join(entries)
    assert run_demo.resume_guest_query(original) == query[1:]
    # A→B→A normalization is pure: old loopback port and intervening B
    # cannot contaminate a later A even with differently ordered input.
    a = recipe(cut="early", valid_at="2026-10-10", family="CHAIN",
               published_until="2026-09-19T12:00:00Z", view="compare")
    b = recipe(cut="late", valid_at="2026-09-11", family="PP04",
               published_until="2026-10-30T12:00:00Z", scenario="privacy_probe")
    first_a = run_demo.resume_guest_query("http://127.0.0.1:5123/" + a)
    middle_b = run_demo.resume_guest_query(b)
    final_a = run_demo.resume_guest_query(
        "http://localhost:6543/?" + "&".join(reversed(a[1:].split("&")))
    )
    assert first_a == final_a == a[1:]
    assert middle_b == b[1:] and middle_b != first_a
    assert "5123" not in final_a and "6543" not in final_a


BAD_GUEST_LINKS = [
    ("duplicate", recipe() + "&cut=early"),
    ("encoded_duplicate", recipe() + "&%63ut=early"),
    ("unknown", recipe() + "&private_source_id=REAL:SECRET_CANARY"),
    ("sha_claim", recipe() + "&receipt_sha256=" + "a" * 64),
    ("missing", recipe().replace("&view=sources", "")),
    ("empty_value", recipe().replace("&cut=late", "&cut=")),
    ("wrong_marker", recipe().replace("pfl_guest=v1", "pfl_guest=v2")),
    ("bad_cut", recipe(cut="future")),
    ("bad_date", recipe(valid_at="2026-12-01")),
    ("future_clock", recipe(cut="early", published_until="2026-10-30T12:00:00Z")),
    ("bad_family", recipe(family="GUEST_IDENTITIES")),
    ("bad_scenario", recipe(scenario="admitted_real")),
    ("bad_view", recipe(view="account")),
    ("invalid_percent", recipe().replace("view=sources", "view=%GG")),
    ("partial_percent", recipe().replace("view=sources", "view=%2")),
    ("encoded_control", recipe().replace("view=sources", "view=%0A")),
    ("raw_newline", recipe() + "\nSENSITIVE_CANARY"),
    ("raw_carriage_return", recipe() + "\rSENSITIVE_CANARY"),
    ("encoded_userinfo", "http://user%40secret@127.0.0.1:4000/" + recipe()),
    ("username", "http://user:secret@127.0.0.1:4000/" + recipe()),
    ("remote_host", "http://198.51.100.1:4000/" + recipe()),
    ("remote_named", "http://example.org:4000/" + recipe()),
    ("https", "https://127.0.0.1:4000/" + recipe()),
    ("no_port", "http://127.0.0.1/" + recipe()),
    ("port_zero", "http://127.0.0.1:0/" + recipe()),
    ("port_too_large", "http://127.0.0.1:99999/" + recipe()),
    ("port_not_number", "http://127.0.0.1:foo/" + recipe()),
    ("bad_path", "http://127.0.0.1:4000/game" + recipe()),
    ("path_relative", "/?" + recipe()[1:]),
    ("fragment", "http://127.0.0.1:4000/" + recipe() + "#CANARY"),
    ("relative_fragment", recipe() + "#CANARY"),
    ("backslash", "http://127.0.0.1:4000\\/" + recipe()),
    ("doubled_separator", recipe().replace("&family=all", "&&family=all")),
    ("trailing_separator", recipe() + "&"),
    ("oversized", recipe() + "&" + "Z" * 1100),
    ("unicode_lookalike", recipe(view="соmpare")),
    ("encoded_slash_path", "http://127.0.0.1:4000/%2F" + recipe()),
]


@pytest.mark.parametrize("label,link", BAD_GUEST_LINKS,
                         ids=[label for label, _ in BAD_GUEST_LINKS])
def test_malformed_rejected_without_echoing_untrusted_content(label, link):
    with pytest.raises(ValueError, match="Enlace de consulta científica no válido") as exc:
        run_demo.resume_guest_query(link)
    assert "SENSITIVE_CANARY" not in str(exc.value)
    assert "SECRET_CANARY" not in str(exc.value)


@pytest.mark.parametrize("bad_link", [
    recipe() + "&username=TOP_SECRET_USERNAME",
    recipe(cut="early", published_until="2026-10-30T12:00:00Z"),
    "http://evil.example:9001/" + recipe(),
    recipe() + "\nINJECTED_SECOND_BANNER",
])
def test_rejection_exits_2_before_socket_or_database(monkeypatch, tmp_path, capsys, bad_link):
    called = []
    monkeypatch.setattr(run_demo, "serve", lambda *args, **kwargs: called.append(args))
    db = tmp_path / "unopened" / "science.sqlite3"
    with pytest.raises(SystemExit) as exc:
        run_demo.main([
            "--science-only", "--port", "0", "--db", str(db),
            "--resume-guest-query", bad_link,
        ])
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "Enlace de consulta científica no válido" in captured.err
    for secret in ("TOP_SECRET_USERNAME", "INJECTED_SECOND_BANNER", "evil.example"):
        assert secret not in captured.out + captured.err
    assert called == []
    assert not db.exists()
    assert not db.parent.exists()


def test_resume_requires_science_only_before_socket_or_database(monkeypatch, tmp_path):
    monkeypatch.setattr(run_demo, "serve", lambda *args, **kwargs:
                        pytest.fail("must not start a Fantasy account server"))
    with pytest.raises(SystemExit) as exc:
        run_demo.main(["--resume-guest-query", recipe(),
                       "--db", str(tmp_path / "not-created.sqlite3")])
    assert exc.value.code == 2
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("scientific_only,raw_query", [
    (False, recipe()[1:]),
    (True, recipe()[1:] + "\r\nINJECTED_BANNER"),
    (True, recipe()[1:] + "\nINJECTED_BANNER"),
    (True, recipe()[1:] + "#INJECTED_FRAGMENT"),
])
def test_direct_serve_cannot_bypass_no_account_boundary_or_inject_banner(
    monkeypatch, tmp_path, scientific_only, raw_query
):
    from politics_fantasy import server as local_server

    monkeypatch.setattr(local_server.accounts, "init_accounts",
                        lambda *_: pytest.fail("accounts DB must not open"))
    monkeypatch.setattr(local_server, "ThreadingHTTPServer",
                        lambda *_args, **_kwargs: pytest.fail("socket must not bind"))
    db = tmp_path / "unopened" / "science.sqlite3"
    with pytest.raises(ValueError, match="Consulta científica reanudable no válida"):
        local_server.serve(db, port=0, scientific_only=scientific_only,
                           resume_guest_query=raw_query)
    assert not db.parent.exists()


def test_subprocess_rejects_bad_guest_link_without_leaking_it_or_opening_database(tmp_path):
    db = tmp_path / "forbidden" / "science.sqlite3"
    secret = "SECRET_USERNAME_CANARY"
    result = cli(
        "--science-only", "--port", "0", "--db", str(db),
        "--resume-guest-query", recipe() + "&username=" + secret,
    )
    assert result.returncode == 2
    assert "Enlace de consulta científica no válido" in result.stderr
    assert secret not in result.stderr + result.stdout
    assert str(db) not in result.stderr + result.stdout
    assert "Politics Fantasy League ·" not in result.stdout
    assert not db.exists()
    assert not db.parent.exists()


@pytest.mark.parametrize("old_input", [
    "http://127.0.0.1:5678/" + recipe(cut="early", valid_at="2026-10-10",
                                     family="CHAIN", view="compare"),
    recipe(cut="late", published_until="2026-10-30T12:00:00Z",
           family="CHRONICLE", scenario="privacy_probe", view="sources"),
])
def test_real_science_only_subprocess_rebinds_port_zero_and_serves_synthetic_gets(
    tmp_path, old_input
):
    db = tmp_path / "guest" / "science.sqlite3"
    process = subprocess.Popen([
        sys.executable, "-B", str(SCRIPT), "--science-only", "--port", "0",
        "--db", str(db), "--resume-guest-query", old_input,
    ], cwd=ROOT, env=ENV, text=True, encoding="utf-8",
       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        first = process.stdout.readline()
        second = process.stdout.readline()
        pattern = r"http://127\.0\.0\.1:(\d+)"
        matched = re.search(pattern, first)
        assert matched, "first banner must retain existing loopback port format"
        port = int(matched.group(1))
        assert port > 0
        assert first == (f"Politics Fantasy League · CIENCIA SINTÉTICA SIN CUENTAS"
                         f" · http://127.0.0.1:{port}\n")
        assert second == (f"REANUDAR CONSULTA CIENTÍFICA · "
                          f"http://127.0.0.1:{port}/?"
                          f"{run_demo.resume_guest_query(old_input)}\n")
        assert "5678" not in second
        assert "#" not in second and "@" not in second
        assert set(dict(parse_qsl(urlsplit(second.split(' · ', 1)[1].strip()).query))) == {
            key for key, _ in GUEST_FIELDS
        }
        status, health = request(port, "/api/health")
        assert status == 200
        assert health["mode"] == "SYNTHETIC_SCIENCE_ONLY"
        assert health["accounts_enabled"] is False
        status, session = request(port, "/api/session")
        assert status == 401
        assert session["science_only"] is True
        selection = dict(parse_qsl(run_demo.resume_guest_query(old_input)))
        status, registry = request(
            port, "/api/scientific-registry?cut=" + selection["cut"]
            + "&valid_at=" + selection["valid_at"]
            + "&family=" + selection["family"]
            + "&published_until=" + selection["published_until"]
        )
        assert status == 200
        assert registry["cut"] == selection["cut"]
        assert registry["family"] == selection["family"]
        assert registry["R5"] == "STOP_R5"
        assert registry["release_gates_passed"] == 0
        assert registry["scientific_ab_cycles"] == 0
        assert not db.exists()
        assert not (db.parent / "accounts.sqlite3").exists()
        assert (db.parent / "scientific_registry_synthetic.sqlite3").is_file()
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


def test_no_resume_arg_preserves_old_main_dispatch(monkeypatch):
    calls = []
    monkeypatch.setattr(run_demo, "serve", lambda *args, **kwargs:
                        calls.append((args, kwargs)))
    run_demo.main(["--science-only", "--port", "0"])
    assert calls == [((run_demo.ROOT / "data" / "science_beta" / "science.db",),
                      {"port": 0, "scientific_only": True})]


def test_no_resume_arg_preserves_first_two_banner_lines_in_real_runtime(tmp_path):
    db = tmp_path / "baseline" / "science.sqlite3"
    process = subprocess.Popen([
        sys.executable, "-B", str(SCRIPT), "--science-only", "--port", "0",
        "--db", str(db),
    ], cwd=ROOT, env=ENV, text=True, encoding="utf-8",
       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        first = process.stdout.readline()
        second = process.stdout.readline()
        matched = re.fullmatch(
            r"Politics Fantasy League · CIENCIA SINTÉTICA SIN CUENTAS"
            r" · http://127\.0\.0\.1:(\d+)\n", first)
        assert matched is not None
        assert int(matched.group(1)) > 0
        assert second == (
            "SOLO localhost; NO publicar a internet. "
            "Sin cuentas, mercado ni operaciones POST.\n"
        )
        assert not db.exists()
        assert not (db.parent / "accounts.sqlite3").exists()
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
