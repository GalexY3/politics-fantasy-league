"""End-to-end product core tests with fictional figures and injected wall time."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import sqlite3

import pytest

from politics_fantasy.product import (
    GameError, add_club, connect, seed_demo, set_lineup, simulate_round, state, transfer,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def db(tmp_path: Path):
    path = tmp_path / 'demo.sqlite'
    seed_demo(path, now=NOW)
    return path


def test_complete_round_is_frozen_and_next_is_playable(db):
    empty = add_club(db, 'Club sin titulares')['id']
    transfer(db, club_id='demo', figure_id='F04', action='buy', when=NOW)
    set_lineup(db, club_id='demo', round_id='next', figures=['F01', 'F02', 'F04'], when=NOW)
    result = simulate_round(db, round_id='next', when=NOW)
    assert result['already_settled'] is False
    snapshot = state(db, when=NOW)
    finished = next(r for r in snapshot['rounds'] if r['id'] == 'next')
    following = next(r for r in snapshot['rounds'] if r['id'] == result['next_round_id'])
    assert snapshot['demo_clock']['simulated'] is True
    assert finished['is_locked'] is True
    assert finished['scores']['demo'] == pytest.approx(5.5)
    assert finished['scores'][empty] is None
    assert following['is_locked'] is False and following['scores']['demo'] is None
    set_lineup(db, club_id='demo', round_id=following['id'], figures=['F01', 'F02', 'F04'], when=NOW)
    with pytest.raises(GameError, match='bloqueado'):
        set_lineup(db, club_id='demo', round_id='next', figures=['F01', 'F02', 'F04'], when=NOW)
    assert simulate_round(db, round_id='next', when=NOW)['already_settled'] is True
    assert len(state(db, when=NOW)['rounds']) == 3
    # A new late event cannot rewrite the frozen result.
    with connect(db) as con:
        con.execute('INSERT INTO demo_event VALUES(?,?,?,?,?,?,?,?)',
                    ('late', 'F01', 'initiative_registered', finished['starts_at'], result['settled_at'],
                     'a' * 64, 'synthetic://late', 'synthetic-round-1'))
    assert next(r for r in state(db, when=NOW)['rounds'] if r['id']=='next')['scores']['demo'] == pytest.approx(5.5)
    # Reopening the DB keeps the synthetic clock, settlement and next round.
    seed_demo(db, now=NOW)
    assert state(db, when=NOW)['demo_clock']['simulated'] is True
    assert simulate_round(db, round_id='next', when=NOW)['next_round_id'] == result['next_round_id']


def test_concurrent_retries_close_once(db):
    set_lineup(db, club_id='demo', round_id='next', figures=['F01', 'F02', 'F03'], when=NOW)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: simulate_round(db, round_id='next', when=NOW), range(2)))
    assert sum(r['already_settled'] for r in results) == 1
    assert results[0]['next_round_id'] == results[1]['next_round_id']
    with connect(db) as con:
        assert con.execute('SELECT COUNT(*) FROM round_settlement').fetchone()[0] == 1
        assert con.execute("SELECT COUNT(*) FROM demo_event WHERE event_id LIKE 'SIM:next:%'").fetchone()[0] == 10
        assert con.execute('SELECT COUNT(*) FROM fantasy_round').fetchone()[0] == 3


def test_unpublished_future_event_does_not_score_early(db):
    before = state(db, when=NOW)
    past = next(r for r in before['rounds'] if r['id'] == 'past')
    end = datetime.fromisoformat(past['ends_at'])
    with connect(db) as con:
        con.execute('INSERT INTO demo_event VALUES(?,?,?,?,?,?,?,?)',
                    ('future', 'F01', 'speech_recorded', past['starts_at'],
                     (end + timedelta(hours=12)).isoformat(), hashlib.sha256(b'future').hexdigest(),
                     'synthetic://test', 'synthetic-test'))
    early = state(db, when=end + timedelta(hours=1))
    late = state(db, when=end + timedelta(hours=13))
    assert next(r for r in early['rounds'] if r['id']=='past')['scores']['demo'] == pytest.approx(15)
    assert next(r for r in late['rounds'] if r['id']=='past')['scores']['demo'] == pytest.approx(17)


def test_failure_rolls_back_clock_and_journey(db):
    with connect(db) as con:
        con.execute('INSERT INTO demo_event VALUES(?,?,?,?,?,?,?,?)',
                    ('SIM:next:F01', 'F01', 'speech_recorded', NOW.isoformat(), NOW.isoformat(),
                     'b' * 64, 'synthetic://collision', 'synthetic-test'))
    before = state(db, when=NOW)
    with pytest.raises(sqlite3.IntegrityError):
        simulate_round(db, round_id='next', when=NOW)
    after = state(db, when=NOW)
    assert after['demo_clock'] == before['demo_clock']
    assert after['rounds'] == before['rounds']
    with connect(db) as con:
        assert con.execute('SELECT COUNT(*) FROM round_settlement').fetchone()[0] == 0


def test_existing_database_gets_additive_schema_on_seed(db):
    with connect(db) as con:
        con.execute('DROP TABLE round_settlement_score')
        con.execute('DROP TABLE round_settlement')
        con.execute('DROP TABLE demo_clock')
    seed_demo(db, now=NOW)
    assert len(state(db, when=NOW)['figures']) == 10
    assert state(db, when=NOW)['demo_clock']['offset_seconds'] == 0
    set_lineup(db, club_id='demo', round_id='next', figures=['F01','F02','F03'], when=NOW)
    assert simulate_round(db, round_id='next', when=NOW)['already_settled'] is False


def test_non_synthetic_event_blocks_simulation_without_mutation(db):
    upcoming = next(r for r in state(db, when=NOW)['rounds'] if r['id'] == 'next')
    with connect(db) as con:
        con.execute('INSERT INTO demo_event VALUES(?,?,?,?,?,?,?,?)',
                    ('external', 'F01', 'speech_recorded', upcoming['starts_at'], upcoming['starts_at'],
                     'c' * 64, 'https://example.org/real-data', 'test'))
    with pytest.raises(GameError) as exc:
        simulate_round(db, round_id='next', when=NOW)
    assert exc.value.code == 'NON_SYNTHETIC_EVENT'
    after = state(db, when=NOW)
    assert len(after['rounds']) == 2 and after['demo_clock']['offset_seconds'] == 0
