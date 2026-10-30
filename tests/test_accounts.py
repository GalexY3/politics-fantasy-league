"""P1 local multiaccount isolation acceptance. No real persons or public hosting."""
import http.cookiejar
import json
import sqlite3
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from politics_fantasy import accounts
from politics_fantasy.server import handler_factory


@pytest.fixture
def local_accounts(tmp_path):
    auth = tmp_path / "auth.sqlite3"
    game = tmp_path / "legacy-game.sqlite3"
    accounts.init_accounts(auth)
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), handler_factory(game, None, None, auth))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        yield auth, game, base
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def client():
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def request(opener, base, route, payload=None, csrf=None, origin=None,
            extra_headers=None):
    headers = {"X-PFL-Request": "1"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if csrf is not None:
        headers["X-PFL-CSRF"] = csrf
    if origin is not None:
        headers["Origin"] = origin
    headers.update(extra_headers or {})
    req = urllib.request.Request(
        base + route, data=json.dumps(payload).encode() if payload is not None else None,
        headers=headers, method="POST" if payload is not None else "GET")
    try:
        with opener.open(req, timeout=5) as res:
            return res.status, json.load(res)
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def login_new(opener, base, username, password="twelve-chars-plus-2026"):
    assert request(opener, base, "/api/register", {"username": username, "password": password})[0] == 201
    status, body = request(opener, base, "/api/login", {"username": username, "password": password})
    assert status == 200 and body["result"]["username"] == username
    return body["result"]["csrf"]


def test_unauthenticated_game_never_exposes_clubs(local_accounts):
    _, _, base = local_accounts
    op = client()
    assert request(op, base, "/api/state")[0] == 401
    assert request(op, base, "/api/buy", {"club_id": "demo", "figure_id": "F04"})[0] == 401
    assert request(op, base, "/api/session")[0] == 401
    assert request(op, base, "/api/health")[0] == 200


def test_two_account_sessions_clubs_and_inventory_are_physically_isolated(local_accounts):
    auth, _, base = local_accounts
    alice, bob = client(), client()
    acs = login_new(alice, base, "alice_123")
    bcs = login_new(bob, base, "bob_456")
    status, aclub = request(alice, base, "/api/clubs", {"name": "Equipo Azul"}, acs)
    assert status == 200
    status, bclub = request(bob, base, "/api/clubs", {"name": "Equipo Rojo"}, bcs)
    assert status == 200
    ai, bi = aclub["result"]["id"], bclub["result"]["id"]
    assert ai != bi
    ast = request(alice, base, "/api/state")[1]
    bst = request(bob, base, "/api/state")[1]
    assert "Equipo Azul" in [c["name"] for c in ast["clubs"]]
    assert "Equipo Rojo" not in [c["name"] for c in ast["clubs"]]
    assert "Equipo Rojo" in [c["name"] for c in bst["clubs"]]
    assert "Equipo Azul" not in [c["name"] for c in bst["clubs"]]
    assert ast["authentication"] == bst["authentication"] == "LOCAL_ACCOUNT_ISOLATED"
    # Identical fictional fixture figures do NOT imply a shared account DB.
    assert request(alice, base, "/api/buy", {"club_id": ai, "figure_id": "F04"}, acs)[0] == 200
    assert next(f for f in request(alice, base, "/api/state")[1]["figures"]
                if f["id"] == "F04")["owner_id"] == ai
    assert next(f for f in request(bob, base, "/api/state")[1]["figures"]
                if f["id"] == "F04")["owner_id"] is None
    assert request(bob, base, "/api/buy", {"club_id": ai, "figure_id": "F05"}, bcs)[0] == 404
    with sqlite3.connect(auth) as db:
        ids = [r[0] for r in db.execute("SELECT user_id FROM account")]
    assert len(ids) == 2
    assert all(accounts.game_path(auth, uid).is_file() for uid in ids)


def test_csrf_cannot_be_omitted_or_borrowed(local_accounts):
    _, _, base = local_accounts
    alice, bob = client(), client()
    acs = login_new(alice, base, "alice_abc")
    bcs = login_new(bob, base, "bob_abc")
    assert request(alice, base, "/api/clubs", {"name": "Sin CSRF"})[0] == 403
    assert request(alice, base, "/api/clubs", {"name": "CSRF ajeno"}, bcs)[0] == 403
    assert request(alice, base, "/api/clubs", {"name": "Peticion cruzada"}, acs,
                   origin="https://evil.example")[0] == 403
    assert request(alice, base, "/api/clubs", {"name": "Autorizado"}, acs)[0] == 200


def test_login_bad_password_and_duplicate_account(local_accounts):
    _, _, base = local_accounts
    alice = client()
    _ = login_new(alice, base, "alice_bad")
    assert request(client(), base, "/api/login",
                   {"username": "alice_bad", "password": "wrong-password!!"})[0] == 401
    assert request(client(), base, "/api/register",
                   {"username": "ALICE_BAD", "password": "twelve-chars-plus-2026"})[0] == 409
    assert request(client(), base, "/api/register",
                   {"username": "bad", "password": "short"})[0] == 400


def test_logout_revokes_cookie_and_session(local_accounts):
    _, _, base = local_accounts
    op = client()
    csrf = login_new(op, base, "alice_logout")
    assert request(op, base, "/api/session")[0] == 200
    assert request(op, base, "/api/logout", {}, csrf)[0] == 200
    assert request(op, base, "/api/session")[0] == 401
    assert request(op, base, "/api/state")[0] == 401


def test_account_data_survives_separate_http_session(local_accounts):
    _, _, base = local_accounts
    first = client()
    csrf = login_new(first, base, "alice_resume")
    assert request(first, base, "/api/clubs", {"name": "Persistente"}, csrf)[0] == 200
    csrf2 = request(client(), base, "/api/login",
                    {"username": "alice_resume", "password": "twelve-chars-plus-2026"})[1]["result"]["csrf"]
    assert csrf2 != csrf
    other = client()
    assert request(other, base, "/api/state")[0] == 401
    # Login using a new browser/cookie jar, not the existing session.
    status, body = request(other, base, "/api/login", {
        "username": "alice_resume", "password": "twelve-chars-plus-2026"})
    assert status == 200 and body["result"]["csrf"]
    names = [c["name"] for c in request(other, base, "/api/state")[1]["clubs"]]
    assert "Persistente" in names


def test_prevent_register_cross_site_form_or_origin(local_accounts):
    _, _, base = local_accounts
    op = client()
    assert request(op, base, "/api/register", {
        "username": "alice_cross", "password": "twelve-chars-plus-2026"},
        origin="https://evil.example")[0] == 403
    assert request(op, base, "/api/register", {
        "username": "alice_cross", "password": "twelve-chars-plus-2026"},
        extra_headers={"X-PFL-Request": "0"})[0] == 403
    assert request(op, base, "/api/register", {
        "username": "alice_cross", "password": "twelve-chars-plus-2026"})[0] == 201
