"""Anonymous local beta preflight, with separate scientific/release gates."""
from __future__ import annotations

from contextlib import contextmanager
import json
from http.server import ThreadingHTTPServer
import sqlite3
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from politics_fantasy import accounts
from politics_fantasy.beta_readiness import (
    RELEASE_GATES, BetaReadinessUnavailable, beta_readiness,
)
from politics_fantasy.server import WEB, handler_factory


@contextmanager
def local_server(tmp_path, *, initialized=True):
    account_db = tmp_path / 'accounts.sqlite3'
    if initialized:
        accounts.init_accounts(account_db)
    server = ThreadingHTTPServer(
        ('127.0.0.1', 0),
        handler_factory(tmp_path / 'unused-game.sqlite3', None, None, account_db),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', account_db
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def get(base, path, *, method='GET', data=None, headers=None):
    request = Request(base + path, method=method, data=data, headers=headers or {})
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, dict(response.headers), json.load(response)
    except HTTPError as exc:
        return exc.code, dict(exc.headers), json.loads(exc.read())


def test_anonymous_get_reports_local_preflight_and_blocked_release(tmp_path):
    with local_server(tmp_path) as (base, _):
        code, headers, body = get(base, '/api/beta-readiness')
        assert code == 200
        assert headers['Cache-Control'] == 'no-store'
        assert body['schema'] == 'pfl.beta_readiness.v1'
        assert body['ok'] is True
        assert body['local_runtime']['status'] == 'READY_FOR_LOCAL_PREFLIGHT'
        assert all(body['local_runtime']['checks'].values())
        assert body['local_runtime']['anonymous_readiness_get'] is True
        assert body['local_runtime']['full_user_journey_attested'] is False
        assert body['scientific_admission'] == {
            'r5_status': 'STOP_R5', 'r5_record': 'R22',
            'system20_valid_ab_cycles': 0, 'system20_remaining_ab_cycles': 20,
            'empirical_study_eligible': False,
        }
        release = body['public_release']
        assert release['eligible'] is False
        assert release['gates_with_attestation_records'] == 0
        assert release['gates_total'] == 6
        assert release['progress_release_blockers'] == 6
        assert release['real_person_scoring'] is False
        assert release['public_hosting_authorized'] is False
        serialized = json.dumps(body)
        assert 'username' not in serialized
        assert 'csrf' not in serialized
        assert 'password' not in serialized
        assert '"records":' not in serialized
        assert get(base, '/api/state')[0] == 401


def test_readiness_fail_closed_when_local_account_schema_is_missing(tmp_path):
    with local_server(tmp_path, initialized=False) as (base, _):
        code, headers, body = get(base, '/api/beta-readiness')
        assert code == 503
        assert headers['Cache-Control'] == 'no-store'
        assert body['ok'] is False
        assert body['local_runtime']['checks']['accounts_schema_readable'] is False
        assert body['public_release']['eligible'] is False


def test_readiness_rejects_accounts_tables_without_required_columns(tmp_path):
    with local_server(tmp_path, initialized=False) as (base, account_db):
        with sqlite3.connect(account_db) as db:
            db.execute('CREATE TABLE account (id TEXT)')
            db.execute('CREATE TABLE account_session (id TEXT)')
        code, _, body = get(base, '/api/beta-readiness')
        assert code == 503
        assert body['local_runtime']['checks']['accounts_schema_readable'] is False


def test_readiness_rejects_queries_unknown_routes_and_writes(tmp_path):
    with local_server(tmp_path) as (base, _):
        assert get(base, '/api/beta-readiness?path=private')[0] == 400
        assert get(base, '/api/beta-readiness?as_of=2026-11-03')[0] == 400
        assert get(base, '/api/beta-readiness/')[0] == 404
        assert get(base, '/api/beta-readiness', method='POST', data=b'{}',
                   headers={'Content-Type': 'application/json'})[0] == 404


def test_paper_gates_can_never_unlock_public_release(tmp_path):
    auth = tmp_path / 'accounts.sqlite3'
    accounts.init_accounts(auth)
    release = json.loads(RELEASE_GATES.read_text(encoding='utf-8'))
    for gate in release['gates']:
        gate.update(status='PASSED', attestation='synthetic-test-only',
                    reviewed_by='synthetic-test-only')
    modified = tmp_path / 'paper.json'
    modified.write_text(json.dumps(release), encoding='utf-8')
    payload = beta_readiness(bind_host='127.0.0.1', accounts_path=auth,
                             web_root=WEB, release_path=modified)
    assert payload['local_runtime']['status'] == 'READY_FOR_LOCAL_PREFLIGHT'
    assert payload['public_release']['gates_with_attestation_records'] == 6
    assert payload['public_release']['eligible'] is False
    assert payload['scientific_admission']['empirical_study_eligible'] is False


def test_malformed_authority_fails_without_leaking_paths(tmp_path):
    auth = tmp_path / 'accounts.sqlite3'
    accounts.init_accounts(auth)
    invalid = tmp_path / 'invalid.json'
    invalid.write_text('{broken json', encoding='utf-8')
    with pytest.raises(BetaReadinessUnavailable):
        beta_readiness(bind_host='127.0.0.1', accounts_path=auth,
                       web_root=WEB, release_path=invalid)
