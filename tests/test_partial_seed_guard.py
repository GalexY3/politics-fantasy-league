"""C13: fail closed on partial synthetic SQLite demo fixture."""
import sqlite3
from datetime import datetime, timezone
import pytest
from politics_fantasy.product import seed_demo, GameError, SCHEMA, NAMES

NOW=datetime(2026,10,28,tzinfo=timezone.utc)

def test_preexisting_partial_figure_cannot_skip_fixture_install(tmp_path):
    path=tmp_path/'partial.sqlite'
    with sqlite3.connect(path) as db:
        db.executescript(SCHEMA)
        db.execute("INSERT INTO figure VALUES(?,?,?,?,?,'SYNTHETIC')",NAMES[0])
    with pytest.raises(GameError,match='Demo local incompleta') as exc:
        seed_demo(path,now=NOW)
    assert exc.value.code=='PARTIAL_SEED'

def test_complete_seed_remains_idempotent(tmp_path):
    path=tmp_path/'good.sqlite'
    seed_demo(path,now=NOW)
    with sqlite3.connect(path) as db:
        before=db.execute('SELECT COUNT(*) FROM demo_event').fetchone()[0]
    seed_demo(path,now=NOW)
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT COUNT(*) FROM demo_event').fetchone()[0]==before

def test_preexisting_event_without_figures_rejected(tmp_path):
    path=tmp_path/'partial.sqlite'
    with sqlite3.connect(path) as db:
        db.executescript(SCHEMA)
        db.execute("INSERT INTO figure VALUES(?,?,?,?,?,'SYNTHETIC')",NAMES[0])
        db.execute('DELETE FROM figure')
        db.execute("INSERT INTO club VALUES('demo','Club ficticio',100)")
    with pytest.raises(GameError) as exc:
        seed_demo(path,now=NOW)
    assert exc.value.code=='PARTIAL_SEED'
