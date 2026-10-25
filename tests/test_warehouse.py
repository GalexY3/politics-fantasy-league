import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import pytest
from politics_fantasy.warehouse import hash_file,load_jsonl,events_as_of,WarehouseError

NOW=datetime(2026,10,24,tzinfo=timezone.utc)
D1=datetime(2026,10,1,tzinfo=timezone.utc)

def record(**changes):
    row={'source_id':'demo','event_id':'one','source_revision':'r1','event_kind':'speech_recorded',
         'occurred_at':D1.isoformat(),'first_public_at':(D1+timedelta(days=1)).isoformat(),
         'source_url':'synthetic://warehouse-fixture','raw_sha256':'a'*64,'person_ids':['person-1']}
    row.update(changes)
    return row

def write(path,rows):
    path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    return hash_file(path)

def test_import_and_asof_cutoff(tmp_path):
    db=tmp_path/'warehouse.db';p=tmp_path/'events.jsonl';digest=write(p,[record()])
    result=load_jsonl(db,p,source_id='demo',expected_sha256=digest,acquired_at=NOW)
    assert result['rows']==1
    assert events_as_of(db,as_of=NOW-timedelta(seconds=1))==[]
    out=events_as_of(db,as_of=NOW)
    assert len(out)==1 and out[0]['person_ids']==['person-1']
    assert result['status']=='NORMALIZED_NOT_SOURCE_CERTIFIED'

def test_hash_mismatch_fails(tmp_path):
    db=tmp_path/'warehouse.db';p=tmp_path/'events.jsonl';write(p,[record()])
    with pytest.raises(WarehouseError,match='SHA256 mismatch'):
        load_jsonl(db,p,source_id='demo',expected_sha256='0'*64,acquired_at=NOW)

def test_idempotent_identical_file(tmp_path):
    db=tmp_path/'warehouse.db';p=tmp_path/'events.jsonl';digest=write(p,[record()]);kw=dict(source_id='demo',expected_sha256=digest,acquired_at=NOW)
    load_jsonl(db,p,**kw)
    assert load_jsonl(db,p,**kw)['status']=='ALREADY_INGESTED'
    assert len(events_as_of(db,as_of=NOW))==1

def test_atomic_rejection_of_bad_row(tmp_path):
    db=tmp_path/'warehouse.db';p=tmp_path/'events.jsonl';digest=write(p,[record(),record(event_id='two',raw_sha256='bad')])
    with pytest.raises(WarehouseError,match='Row 2'):
        load_jsonl(db,p,source_id='demo',expected_sha256=digest,acquired_at=NOW)
    with sqlite3.connect(db) as con:
        assert con.execute('SELECT count(*) FROM event').fetchone()[0]==0
        assert con.execute('SELECT count(*) FROM ingestion').fetchone()[0]==0

def test_conflict_same_identity_and_revision_fails_atomically(tmp_path):
    db=tmp_path/'warehouse.db';a=tmp_path/'a.jsonl';digest=write(a,[record()]);load_jsonl(db,a,source_id='demo',expected_sha256=digest,acquired_at=NOW)
    b=tmp_path/'b.jsonl';digest_b=write(b,[record(person_ids=['other-person'])])
    with pytest.raises(WarehouseError,match='Row 1'):
        load_jsonl(db,b,source_id='demo',expected_sha256=digest_b,acquired_at=NOW)
    assert events_as_of(db,as_of=NOW)[0]['person_ids']==['person-1']

def test_reject_mixed_sources(tmp_path):
    db=tmp_path/'warehouse.db';p=tmp_path/'a.jsonl';digest=write(p,[record(source_id='elsewhere')])
    with pytest.raises(WarehouseError,match='Row 1'):
        load_jsonl(db,p,source_id='demo',expected_sha256=digest,acquired_at=NOW)

def test_revision_is_immutable_and_bitemporal(tmp_path):
    db=tmp_path/'warehouse.db';a=tmp_path/'a.jsonl';digest=write(a,[record()]);load_jsonl(db,a,source_id='demo',expected_sha256=digest,acquired_at=NOW)
    b=tmp_path/'b.jsonl';digest_b=write(b,[record(source_revision='r2',person_ids=['new'])]);load_jsonl(db,b,source_id='demo',expected_sha256=digest_b,acquired_at=NOW+timedelta(days=1))
    assert len(events_as_of(db,as_of=NOW))==1
    assert [x['source_revision'] for x in events_as_of(db,as_of=NOW+timedelta(days=1))]==['r2']

def test_time_range_filter(tmp_path):
    db=tmp_path/'warehouse.db';a=tmp_path/'events.jsonl';digest=write(a,[record()]);load_jsonl(db,a,source_id='demo',expected_sha256=digest,acquired_at=NOW)
    assert events_as_of(db,as_of=NOW,start=D1+timedelta(days=1))==[]
    assert len(events_as_of(db,as_of=NOW,start=D1,end=D1+timedelta(hours=1)))==1
    with pytest.raises(WarehouseError):events_as_of(db,as_of=NOW,start=D1,end=D1)

def test_fails_closed_on_invalid_persons(tmp_path):
    db=tmp_path/'warehouse.db';a=tmp_path/'a.jsonl';digest=write(a,[record(person_ids=['person-1','person-1'])])
    with pytest.raises(WarehouseError,match='duplicate person'):
        load_jsonl(db,a,source_id='demo',expected_sha256=digest,acquired_at=NOW)


def test_revision_replaced_before_time_window_filter(tmp_path):
    db=tmp_path/'warehouse.db';a=tmp_path/'a.jsonl';digest=write(a,[record()])
    load_jsonl(db,a,source_id='demo',expected_sha256=digest,acquired_at=NOW)
    b=tmp_path/'b.jsonl';digest=write(b,[record(source_revision='r2',occurred_at=(D1+timedelta(days=5)).isoformat(),first_public_at=(D1+timedelta(days=6)).isoformat())])
    load_jsonl(db,b,source_id='demo',expected_sha256=digest,acquired_at=NOW+timedelta(days=1))
    assert len(events_as_of(db,as_of=NOW,start=D1,end=D1+timedelta(days=2)))==1
    assert events_as_of(db,as_of=NOW+timedelta(days=2),start=D1,end=D1+timedelta(days=2))==[]


def test_import_detects_intervening_file_change(tmp_path,monkeypatch):
    import politics_fantasy.warehouse as mod
    db=tmp_path/'warehouse.db';p=tmp_path/'events.jsonl';digest=write(p,[record()])
    actual_hash=mod.hash_file
    def changed_between_check_and_read(path):
        result=actual_hash(path)
        write(path,[record(event_id='surprise')])
        return result
    monkeypatch.setattr(mod,'hash_file',changed_between_check_and_read)
    with pytest.raises(WarehouseError,match='File changed during import'):
        load_jsonl(db,p,source_id='demo',expected_sha256=digest,acquired_at=NOW)
    with sqlite3.connect(db) as con:
        assert con.execute('SELECT count(*) FROM ingestion').fetchone()[0]==0


def test_import_rejects_invalid_utf8_atomically(tmp_path):
    db=tmp_path/'warehouse.db';p=tmp_path/'data.jsonl'
    p.write_bytes((json.dumps(record())+'\n').encode('utf-8')+b'\xff\xfe\n')
    with pytest.raises(WarehouseError,match='invalid UTF-8'):
        load_jsonl(db,p,source_id='demo',expected_sha256=hash_file(p),acquired_at=NOW)
    with sqlite3.connect(db) as con:
        assert con.execute('SELECT count(*) FROM ingestion').fetchone()[0]==0