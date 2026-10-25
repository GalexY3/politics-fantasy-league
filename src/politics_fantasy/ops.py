"""Read-only, local operational checks for the fantasy demo and normalized warehouse.

This is not a political-data certification or a security audit. Exit nonzero on an
invariant violation so the operator can catch corruption before a release.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


def _db(path: Path):
    return sqlite3.connect(f'file:{path.resolve()}?mode=ro', uri=True)


def audit(path: Path, *, kind: str = 'product', now: datetime | None = None) -> dict:
    """Read-only quick-check, FK checks and application-level invariants."""
    if kind not in ('product', 'warehouse'):
        raise ValueError('kind must be product or warehouse')
    if not path.is_file():
        raise FileNotFoundError(str(path))
    errors = []
    checks = {}
    with closing(_db(path)) as con:
        con.execute('PRAGMA foreign_keys=ON')
        row=con.execute('PRAGMA quick_check').fetchone()
        checks['sqlite_quick_check'] = row[0]
        if row[0] != 'ok':
            errors.append('SQLITE_QUICK_CHECK_FAILED')
        fk = con.execute('PRAGMA foreign_key_check').fetchall()
        checks['foreign_key_violations'] = len(fk)
        if fk:
            errors.append('FOREIGN_KEYS_INVALID')
        if kind == 'product':
            checks['clubs'] = con.execute('SELECT count(*) FROM club').fetchone()[0]
            checks['figures'] = con.execute('SELECT count(*) FROM figure').fetchone()[0]
            checks['ownership'] = con.execute('SELECT count(*) FROM ownership').fetchone()[0]
            checks['synthetic_only'] = con.execute("SELECT count(*) FROM figure WHERE evidence_state!='SYNTHETIC'").fetchone()[0] == 0
            if not checks['synthetic_only']:
                errors.append('DEMO_HAS_NON_SYNTHETIC_FIGURES')
            invalid = con.execute('''SELECT count(*) FROM demo_event WHERE
                                   source_url NOT LIKE 'synthetic://%' OR raw_sha256 IS NULL''').fetchone()[0]
            checks['non_synthetic_demo_events'] = invalid
            if invalid:
                errors.append('NON_SYNTHETIC_DEMO_EVENTS')
            negative=con.execute('SELECT count(*) FROM club WHERE credits<0').fetchone()[0]
            checks['negative_credits'] = negative
            if negative:
                errors.append('NEGATIVE_CREDITS')
            cur=(now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat(timespec='seconds')
            invalid_future=con.execute('''SELECT count(*) FROM lineup l JOIN fantasy_round r ON r.id=l.round_id
                LEFT JOIN ownership o ON o.figure_id=l.figure_id AND o.club_id=l.club_id
                WHERE r.lock_at>? AND o.figure_id IS NULL''',(cur,)).fetchone()[0]
            checks['unowned_in_open_lineups'] = invalid_future
            if invalid_future:
                errors.append('OPEN_LINEUP_CONTAINS_UNOWNED_FIGURE')
            excessive=con.execute('''SELECT count(*) FROM (
                SELECT club_id, count(*) n FROM ownership GROUP BY club_id HAVING n>5)''').fetchone()[0]
            checks['oversized_clubs'] = excessive
            if excessive:
                errors.append('OVERSIZED_ROSTER')
        else:
            checks['ingestions'] = con.execute('SELECT count(*) FROM ingestion').fetchone()[0]
            checks['events_all_revisions'] = con.execute('SELECT count(*) FROM event').fetchone()[0]
            errors_in_counts=con.execute('''SELECT count(*) FROM ingestion i WHERE row_count!=
                      (SELECT count(*) FROM event e WHERE e.ingestion_sha256=i.sha256)''').fetchone()[0]
            checks['row_count_disagreements'] = errors_in_counts
            if errors_in_counts:
                errors.append('INGESTION_COUNTS_MISMATCH')
            checks['certification'] = 'NOT_SOURCE_CERTIFIED'
    return {'kind':kind,'status':'PASS' if not errors else 'FAIL', 'errors':errors, 'checks':checks,
            'scope':'LOCAL_INTEGRITY_ONLY_NOT_OFFICIAL_VALIDATION'}


def main():
    p=argparse.ArgumentParser(description='Read-only integrity check; never validates official political datasets')
    p.add_argument('--db',required=True,type=Path)
    p.add_argument('--kind',choices=['product','warehouse'],default='product')
    a=p.parse_args()
    try:
        result=audit(a.db,kind=a.kind)
    except (OSError,sqlite3.DatabaseError,ValueError) as e:
        result={'kind':a.kind,'status':'FAIL','errors':[str(e)],'checks':{}}
    print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True))
    raise SystemExit(0 if result['status']=='PASS' else 1)

if __name__=='__main__':
    main()
