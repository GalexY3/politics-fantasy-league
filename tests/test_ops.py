from datetime import datetime, timezone
import sqlite3
from politics_fantasy.ops import audit
from politics_fantasy.product import seed_demo, connect, set_lineup
from politics_fantasy.warehouse import hash_file, load_jsonl
import json


def test_audit_demo_only_synthetic(tmp_path):
    db=tmp_path/'demo.sqlite';seed_demo(db)
    result=audit(db,kind='product')
    assert result['status']=='PASS'
    assert result['checks']['synthetic_only']
    assert result['checks']['non_synthetic_demo_events']==0


def test_audit_catches_future_lineup_corruption(tmp_path):
    db=tmp_path/'demo.sqlite';seed_demo(db)
    set_lineup(db,club_id='demo',round_id='next',figures=['F01','F02','F03'])
    with connect(db) as con:
        con.execute("DELETE FROM ownership WHERE figure_id='F01'")
    result=audit(db,kind='product')
    assert result['status']=='FAIL'
    assert 'OPEN_LINEUP_CONTAINS_UNOWNED_FIGURE' in result['errors']


def test_audit_warehouse_counts(tmp_path):
    db=tmp_path/'warehouse.sqlite';p=tmp_path/'events.jsonl'
    row=dict(source_id='test',event_id='1',source_revision='r1',
             occurred_at='2026-01-01T00:00:00+00:00',first_public_at='2026-01-02T00:00:00+00:00',
             event_kind='speech_recorded',person_ids=['p1'],source_url='synthetic://test',raw_sha256='a'*64)
    p.write_text(json.dumps(row)+'\n');cut=datetime(2026,10,25,tzinfo=timezone.utc)
    load_jsonl(db,p,source_id='test',expected_sha256=hash_file(p),acquired_at=cut)
    assert audit(db,kind='warehouse')['status']=='PASS'
    with sqlite3.connect(db) as con:
        con.execute('UPDATE ingestion SET row_count=99')
    out=audit(db,kind='warehouse')
    assert out['status']=='FAIL'
    assert 'INGESTION_COUNTS_MISMATCH' in out['errors']