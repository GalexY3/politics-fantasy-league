"""Production-engine tests use ONLY fictional entities, timestamps and events."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import tempfile
import json
import urllib.request
import urllib.error
import threading

import pytest

from politics_fantasy.product import (seed_demo, state, transfer, set_lineup, add_club,
                                     connect, GameError, LINEUP_SIZE)
from politics_fantasy.server import handler_factory, PILOT
from http.server import ThreadingHTTPServer

@pytest.fixture
def db(tmp_path):
    p=tmp_path/'app.db'
    seed_demo(p)
    return p

def check_error(code,fn,*args,**kwargs):
    with pytest.raises(GameError) as err: fn(*args,**kwargs)
    assert err.value.code==code

def test_seed_idempotent(db):
    seed_demo(db)
    s=state(db)
    assert len(s['figures'])==10 and len(s['clubs'])==1
    assert sum(f['owner_id']=='demo' for f in s['figures'])==3
    assert s['clubs'][0]['credits']==32
    assert len(s['rounds'])==2
    assert s['mode']=='SYNTHETIC_FICTIONAL_DEMO_ONLY'
    assert s['rounds'][0]['scores']['demo']==pytest.approx(15.0)
    assert s['rounds'][1]['scores']['demo'] is None

def test_real_aggregate_is_separated(db):
    s=state(db,pilot_csv=PILOT)
    assert len(s['observatory']['votes'])==20
    assert s['observatory']['status']=='EXPLORATORY_MANUAL_AGGREGATE_NOT_VALIDATED'
    assert all(f['evidence_state']=='SYNTHETIC' for f in s['figures'])
    assert not any('politico' in f['id'].lower() for f in s['figures'])

def test_buy_sell_consistency(db):
    b=transfer(db,club_id='demo',figure_id='F04',action='buy')
    assert b['credits']==20 and b['credits_delta']==-12
    check_error('OWNED',transfer,db,club_id='demo',figure_id='F04',action='buy')
    s=transfer(db,club_id='demo',figure_id='F04',action='sell')
    assert s['credits']==32 and s['credits_delta']==12
    assert [e['action'] for e in state(db)['trades']]==['sell','buy']

def test_other_club_cannot_buy_owned_or_sell(db):
    club=add_club(db,'Club Doble')
    check_error('OWNED',transfer,db,club_id=club['id'],figure_id='F01',action='buy')
    check_error('NOT_OWNED',transfer,db,club_id=club['id'],figure_id='F01',action='sell')

def test_roster_cap(db):
    transfer(db,club_id='demo',figure_id='F04',action='buy')
    transfer(db,club_id='demo',figure_id='F09',action='buy')
    check_error('ROSTER_FULL',transfer,db,club_id='demo',figure_id='F06',action='buy')

def test_low_credits(db):
    with connect(db) as con:
        con.execute("UPDATE club SET credits=0 WHERE id='demo'")
    check_error('LOW_CREDITS',transfer,db,club_id='demo',figure_id='F06',action='buy')
    assert not any(x['id']=='F06' and x['owner_id'] for x in state(db)['figures'])

def test_bad_entities_and_actions(db):
    check_error('UNKNOWN_ENTITY',transfer,db,club_id='nothere',figure_id='F05',action='buy')
    check_error('UNKNOWN_ENTITY',transfer,db,club_id='demo',figure_id='notreal',action='buy')
    check_error('INVALID_ACTION',transfer,db,club_id='demo',figure_id='F05',action='a')

def test_lineup_rejects_duplicates(db):
    check_error('BAD_LINEUP',set_lineup,db,club_id='demo',round_id='next',figures=['F01','F01','F02'])
    check_error('BAD_LINEUP',set_lineup,db,club_id='demo',round_id='next',figures=['F01','F02'])

def test_lineup_rejects_non_owned(db):
    check_error('NOT_OWNED',set_lineup,db,club_id='demo',round_id='next',figures=['F01','F02','F04'])

def test_future_lineup_can_be_saved_and_replaced(db):
    a=set_lineup(db,club_id='demo',round_id='next',figures=['F01','F02','F03'])
    assert a['figures']==['F01','F02','F03']
    transfer(db,club_id='demo',figure_id='F04',action='buy')
    b=set_lineup(db,club_id='demo',round_id='next',figures=['F01','F02','F04'])
    assert b['figures']==['F01','F02','F04']
    assert state(db)['rounds'][1]['lineups']['demo']==['F01','F02','F04']

def test_locked_round_never_change(db):
    check_error('LINEUP_LOCKED',set_lineup,db,club_id='demo',round_id='past',figures=['F01','F02','F03'])

def test_lock_boundary_exact_instant(db):
    lock=state(db)['rounds'][1]['lock_at']
    check_error('LINEUP_LOCKED',set_lineup,db,club_id='demo',round_id='next',figures=['F01','F02','F03'],when=datetime.fromisoformat(lock))
    a=set_lineup(db,club_id='demo',round_id='next',figures=['F01','F02','F03'],when=datetime.fromisoformat(lock)-timedelta(microseconds=1))
    assert a['locked'] is False

def test_historical_lineups_are_frozen_when_sold(db):
    transfer(db,club_id='demo',figure_id='F01',action='sell')
    s=state(db)
    assert 'F01' in s['rounds'][0]['lineups']['demo']
    assert s['rounds'][0]['scores']['demo']==pytest.approx(15.0)

def test_club_validation(db):
    check_error('INVALID_CLUB_NAME',add_club,db,'X')
    check_error('INVALID_CLUB_NAME',add_club,db,'<script>')
    check_error('INVALID_CLUB_NAME',add_club,db,'\nBad')
    assert add_club(db,'Grupo X')['credits']==100
    check_error('DUPLICATE_NAME',add_club,db,'Grupo X')

def test_atomic_buy_concurrency(db):
    a=add_club(db,'Equipo A')['id']
    b=add_club(db,'Equipo B')['id']
    def try_buy(cid):
        try: return transfer(db,club_id=cid,figure_id='F08',action='buy')
        except GameError as ex: return ex.code
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(try_buy,[a,b]))
    assert sum(isinstance(x,dict) for x in results)==1
    assert results.count('OWNED')==1
    with connect(db) as con:
        assert con.execute("SELECT COUNT(*) FROM ownership WHERE figure_id='F08'").fetchone()[0]==1

@pytest.fixture
def http_server(db):
    serv=ThreadingHTTPServer(('127.0.0.1',0),handler_factory(db,PILOT))
    t=threading.Thread(target=serv.serve_forever,daemon=True);t.start()
    try:
        yield f'http://127.0.0.1:{serv.server_port}'
    finally:
        serv.shutdown();serv.server_close();t.join(timeout=3)

def test_http_health(http_server):
    with urllib.request.urlopen(http_server+'/api/health') as resp:
        data=json.load(resp)
        assert data['ok'] and not data['real_player_scoring']
        assert resp.headers['X-Frame-Options']=='DENY'

def test_http_frontend_served(http_server):
    with urllib.request.urlopen(http_server+'/') as resp:
        assert b'POL' in resp.read()
    for f in ('app.js','style.css'):
        with urllib.request.urlopen(http_server+'/'+f) as resp:
            assert len(resp.read())>500

def test_http_api_buy_and_state(http_server):
    req=urllib.request.Request(http_server+'/api/buy',data=b'{"club_id":"demo","figure_id":"F04"}',headers={'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req) as resp:
        assert json.load(resp)['result']['credits']==20
    with urllib.request.urlopen(http_server+'/api/state') as resp:
        assert any(f['id']=='F04' and f['owner_id']=='demo' for f in json.load(resp)['figures'])

def test_http_rejects_bad_media_and_cross_origin(http_server):
    req=urllib.request.Request(http_server+'/api/buy',data=b'{}',headers={'Content-Type':'text/plain'},method='POST')
    with pytest.raises(urllib.error.HTTPError) as e: urllib.request.urlopen(req)
    assert e.value.code==415
    req=urllib.request.Request(http_server+'/api/buy',data=b'{}',headers={'Content-Type':'application/json','Origin':'https://evil.example'},method='POST')
    with pytest.raises(urllib.error.HTTPError) as e: urllib.request.urlopen(req)
    assert e.value.code==403

def test_http_not_found(http_server):
    with pytest.raises(urllib.error.HTTPError) as e: urllib.request.urlopen(http_server+'/../../../etc/passwd')
    assert e.value.code==404


def test_cannot_sell_an_active_future_lineup(db):
    set_lineup(db,club_id='demo',round_id='next',figures=['F01','F02','F03'])
    check_error('ACTIVE_LINEUP',transfer,db,club_id='demo',figure_id='F01',action='sell')
    assert next(f for f in state(db)['figures'] if f['id']=='F01')['owner_id']=='demo'
    transfer(db,club_id='demo',figure_id='F04',action='buy')
    set_lineup(db,club_id='demo',round_id='next',figures=['F02','F03','F04'])
    transfer(db,club_id='demo',figure_id='F01',action='sell')


def test_http_rejects_untrusted_host_even_if_origin_matches(http_server):
    with pytest.raises(urllib.error.HTTPError) as err:
        urllib.request.urlopen(urllib.request.Request(http_server+'/api/state',
                                   headers={'Host':'evil.example:8787'}))
    assert err.value.code==403
    req=urllib.request.Request(http_server+'/api/buy',data=b'{}',method='POST',
          headers={'Host':'evil.example:8787','Origin':'http://evil.example:8787',
                   'Content-Type':'application/json'})
    with pytest.raises(urllib.error.HTTPError) as err:
        urllib.request.urlopen(req)
    assert err.value.code==403