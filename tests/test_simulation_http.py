"""The simulation action is confined to the existing local HTTP contract."""
import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from politics_fantasy.product import seed_demo, set_lineup, state
from politics_fantasy.server import handler_factory


@pytest.fixture
def service(tmp_path):
    db = tmp_path / 'game.db'
    seed_demo(db)
    set_lineup(db, club_id='demo', round_id='next', figures=['F01','F02','F03'])
    srv = ThreadingHTTPServer(('127.0.0.1', 0), handler_factory(db, None))
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    try:
        yield db, f'http://127.0.0.1:{srv.server_port}'
    finally:
        srv.shutdown()
        srv.server_close()
        thread.join(timeout=3)


def post(base, payload, headers=None):
    req = urllib.request.Request(base+'/api/simulate-round', data=json.dumps(payload).encode('utf8'),
        headers={'Content-Type':'application/json', **(headers or {})}, method='POST')
    with urllib.request.urlopen(req) as response:
        return json.load(response)


def test_http_simulation_is_idempotent_and_creates_next_round(service):
    db, base = service
    first = post(base, {'round_id':'next'})['result']
    second = post(base, {'round_id':'next'})['result']
    assert not first['already_settled'] and second['already_settled']
    assert first['next_round_id'] == second['next_round_id']
    result = state(db)
    assert len(result['rounds']) == 3
    assert next(r for r in result['rounds'] if r['id']=='next')['scores']['demo'] == pytest.approx(6.5)


@pytest.mark.parametrize('payload,headers,code', [
    ({'round_id':[]}, {}, 400),
    ({'round_id':'missing'}, {}, 404),
    ({'round_id':'next'}, {'Origin':'https://foreign.example'}, 403),
    ({'round_id':'next'}, {'Host':'foreign.example'}, 403),
])
def test_invalid_http_requests_do_not_change_demo(service, payload, headers, code):
    db, base = service
    before = state(db)
    with pytest.raises(urllib.error.HTTPError) as exc:
        post(base, payload, headers)
    assert exc.value.code == code
    after = state(db)
    assert after['rounds'] == before['rounds']
    assert after['demo_clock']['offset_seconds'] == before['demo_clock']['offset_seconds']
