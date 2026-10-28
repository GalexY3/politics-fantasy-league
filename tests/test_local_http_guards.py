"""Local HTTP guard matrix; synthetic callbacks and loopback only."""
import http.client
import json
import threading
from http.server import ThreadingHTTPServer

import pytest

import politics_fantasy.server as app


@pytest.fixture
def service(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(app, "add_club", lambda db, name: calls.append(name) or {"name": name})
    server = ThreadingHTTPServer(("127.0.0.1", 0), app.handler_factory(tmp_path / "unused.db", None))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_port, calls
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def send(port, headers, body=b''):
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=3)
    try:
        conn.putrequest('POST', '/api/clubs', skip_host=True)
        for key, value in headers.items():
            conn.putheader(key, value)
        conn.endheaders(body)
        response = conn.getresponse()
        payload = json.loads(response.read())
        return response.status, payload
    finally:
        conn.close()


@pytest.mark.parametrize('overrides,expected', [
    ({'Host': 'attacker.invalid'}, 403),
    ({'Origin': 'https://attacker.invalid'}, 403),
    ({'Content-Type': 'text/plain'}, 415),
    ({'Content-Length': '0'}, 413),
    ({'Content-Length': '-1'}, 413),
    ({'Content-Length': '16385'}, 413),
    ({'Content-Length': 'invalid'}, 400),
    ({'Content-Length': None}, 413),
])
def test_rejected_request_never_calls_action(service, overrides, expected):
    port, calls = service
    headers = {'Host': f'127.0.0.1:{port}', 'Content-Type': 'application/json',
               'Content-Length': '2'}
    headers.update(overrides)
    headers = {key: value for key, value in headers.items() if value is not None}
    status, payload = send(port, headers)
    assert status == expected
    assert calls == []
    assert 'error' in payload


def test_valid_local_json_reaches_action(service):
    port, calls = service
    body = b'{"name":"Fixture"}'
    status, payload = send(port, {'Host': f'127.0.0.1:{port}',
                                 'Origin': f'http://127.0.0.1:{port}',
                                 'Content-Type': 'application/json',
                                 'Content-Length': str(len(body))}, body)
    assert status == 200
    assert calls == ['Fixture']
    assert payload['ok'] is True
