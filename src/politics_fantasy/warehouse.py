"""Local longitudinal event warehouse for already-normalized, audited JSONL.

This module does NOT parse unknown official JSON formats and does not certify historical
availability, schema semantics, identity resolution, or completeness of institutional data.
It is deliberately bitemporal: a future ingestion cannot silently become past knowledge.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from contextlib import closing
from .events import as_utc

DDL = """
CREATE TABLE IF NOT EXISTS ingestion (
 sha256 TEXT PRIMARY KEY, filename TEXT NOT NULL, source_id TEXT NOT NULL,
 observed_at TEXT NOT NULL, row_count INTEGER NOT NULL,
 status TEXT NOT NULL CHECK(status='NORMALIZED_NOT_SOURCE_CERTIFIED'));
CREATE TABLE IF NOT EXISTS event (
 source_id TEXT NOT NULL, event_id TEXT NOT NULL, source_revision TEXT NOT NULL,
 occurred_at TEXT NOT NULL, first_public_at TEXT NOT NULL,
 recorded_at TEXT NOT NULL, event_kind TEXT NOT NULL, person_ids_json TEXT NOT NULL,
 source_url TEXT NOT NULL, raw_sha256 TEXT NOT NULL,
 ingestion_sha256 TEXT NOT NULL REFERENCES ingestion(sha256),
 PRIMARY KEY(source_id, event_id, source_revision));
CREATE INDEX IF NOT EXISTS idx_warehouse_asof ON event(first_public_at, recorded_at, occurred_at);
"""

class WarehouseError(ValueError):
    pass


def hash_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def _utc(v) -> str:
    return as_utc(v).isoformat()


def load_jsonl(db_path: Path, input_file: Path, *, source_id: str, expected_sha256: str,
               acquired_at: datetime, max_rows: int=10_000_000) -> dict:
    """Atomic streaming, source-schema-neutral import; no silent correction of rows.

    This ingestion timestamp is a local *observed at* (not original publication time).
    Re-running same file/source is idempotent; same identity/revision cannot be overwritten.
    Required first_public_at must be externally validated before prospective analysis.
    """
    if not source_id or not isinstance(source_id,str) or len(source_id)>100:
        raise WarehouseError('Invalid source ID')
    if len(expected_sha256)!=64 or not all(c in '0123456789abcdef' for c in expected_sha256):
        raise WarehouseError('Invalid expected SHA256')
    acquired_at=_utc(acquired_at)
    observed_hash=hash_file(input_file)
    if observed_hash!=expected_sha256:
        raise WarehouseError('File has changed: SHA256 mismatch')
    if max_rows<1:
        raise WarehouseError('max_rows must be positive')
    db_path.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(db_path)) as db:
        db.execute('PRAGMA foreign_keys=ON')
        db.executescript(DDL)
        existing=db.execute('SELECT * FROM ingestion WHERE sha256=?',(observed_hash,)).fetchone()
        if existing:
            if existing[2]!=source_id:
                raise WarehouseError('Exact file cannot be reassigned to another source ID')
            return {'status':'ALREADY_INGESTED','rows':existing[4], 'sha256':observed_hash}
        rows=0
        try:
            db.execute('BEGIN IMMEDIATE')
            # Deferred key prevents partial imports if row N fails.
            db.execute('INSERT INTO ingestion VALUES(?,?,?,?,?,?)',(observed_hash,input_file.name,source_id,acquired_at,0,'NORMALIZED_NOT_SOURCE_CERTIFIED'))
            imported_hash=hashlib.sha256()
            with input_file.open('rb') as stream:
                for line_number,raw_line in enumerate(stream,1):
                    imported_hash.update(raw_line)
                    try:
                        line=raw_line.decode('utf-8')
                    except UnicodeDecodeError as e:
                        raise WarehouseError(f'Row {line_number}: invalid UTF-8') from e
                    if not line.strip():continue
                    rows+=1
                    if rows>max_rows:raise WarehouseError('Row limit exceeded')
                    try:
                        record=json.loads(line)
                        if not isinstance(record,dict):raise TypeError('not object')
                        if record['source_id']!=source_id:raise ValueError('mixed source')
                        if not isinstance(record['person_ids'],list) or not all(isinstance(x,str) and x for x in record['person_ids']):
                            raise ValueError('bad person ID list')
                        if len(set(record['person_ids']))!=len(record['person_ids']):
                            raise ValueError('duplicate person ID')
                        for key in ('event_id','event_kind','source_url','raw_sha256','source_revision'):
                            if not isinstance(record[key],str) or not record[key]:raise ValueError('empty key: '+key)
                        if len(record['raw_sha256'])!=64 or not all(ch in '0123456789abcdef' for ch in record['raw_sha256']):
                            raise ValueError('bad raw sha')
                        occured=_utc(record['occurred_at'])
                        published=_utc(record['first_public_at'])
                        if published<occured and not record['event_kind'].startswith('scheduled_'):
                            raise ValueError('published before occurred for observed event')
                        item=(source_id,record['event_id'],record['source_revision'],occured,published,acquired_at,
                              record['event_kind'],json.dumps(record['person_ids'],ensure_ascii=False),
                              record['source_url'],record['raw_sha256'],observed_hash)
                        db.execute('INSERT INTO event VALUES(?,?,?,?,?,?,?,?,?,?,?)',item)
                    except (ValueError,TypeError,KeyError,sqlite3.IntegrityError,json.JSONDecodeError) as e:
                        raise WarehouseError(f'Row {line_number}: invalid or conflicting: {e}') from e
            # Detect modifications between the initial SHA-256 check and the
            # actual import. A successful import must bind to exactly the bytes
            # that were processed, not an earlier version of the same pathname.
            if imported_hash.hexdigest()!=observed_hash:
                raise WarehouseError('File changed during import: SHA256 mismatch')
            db.execute('UPDATE ingestion SET row_count=? WHERE sha256=?',(rows,observed_hash))
            db.commit()
        except Exception:
            db.rollback()
            raise
    return {'status':'NORMALIZED_NOT_SOURCE_CERTIFIED','rows':rows,'sha256':observed_hash,
            'warning':'Not an independently verified official-source or completeness certificate'}


def events_as_of(db_path: Path, *, as_of: datetime, start: datetime | None=None,
                 end: datetime | None=None) -> list[dict]:
    """Historic-safe query only if recorded_at and known_public_at are <= as_of.

    This is conservatively EMPTY for events ingested later, even if first publication
    claimed to be earlier. No retroactive inference from the late archive.
    """
    known=_utc(as_of)
    if start and end and as_utc(end)<=as_utc(start):
        raise WarehouseError('Invalid target date range')
    # First resolve the newest available revision per identity at the cut,
    # THEN filter the target event-time window. Filtering first could wrongly
    # resurrect an obsolete revision after an event-time correction.
    query='''WITH ranked AS (
      SELECT source_id,event_id,source_revision,occurred_at,first_public_at,
             recorded_at,event_kind,person_ids_json,source_url,raw_sha256,
             ROW_NUMBER() OVER (PARTITION BY source_id,event_id
                                ORDER BY recorded_at DESC,source_revision DESC) AS rn
        FROM event WHERE first_public_at<=? AND recorded_at<=?
    ) SELECT source_id,event_id,source_revision,occurred_at,first_public_at,
             recorded_at,event_kind,person_ids_json,source_url,raw_sha256
        FROM ranked WHERE rn=1'''
    params=[known,known]
    if start:query+=' AND occurred_at>=?';params.append(_utc(start))
    if end:query+=' AND occurred_at<?';params.append(_utc(end))
    query+=' ORDER BY occurred_at, source_id, event_id, source_revision'
    with closing(sqlite3.connect(db_path)) as db:
        db.row_factory=sqlite3.Row
        results=[]
        for r in db.execute(query,params):
            item=dict(r)
            item['person_ids']=json.loads(item.pop('person_ids_json'))
            results.append(item)
        return results
