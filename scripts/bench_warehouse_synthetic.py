"""Non-empirical SQLite throughput smoke for warehouse; NO INSTITUTIONAL DATA."""
from __future__ import annotations
import argparse
import json
import resource
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'src'))
from politics_fantasy.warehouse import hash_file,load_jsonl


def benchmark(rows:int=100_000)->dict:
    if rows<1 or rows>1_000_000:
        raise ValueError('1..1,000,000 rows allowed in local synthetic benchmark')
    with tempfile.TemporaryDirectory() as t:
        root=Path(t)
        data=root/'NORMALIZED_SYNTHETIC.jsonl'
        with data.open('w',encoding='utf-8') as f:
            for i in range(rows):
                row={
                    'source_id':'synthetic_benchmark',
                    'event_id':f'synthetic:{i:08}',
                    'source_revision':'r1','event_kind':'speech_recorded',
                    'occurred_at':'2026-01-01T08:00:00+00:00',
                    'first_public_at':'2026-01-01T10:00:00+00:00',
                    'source_url':'synthetic://warehouse-throughput',
                    'raw_sha256':f'{i+1:064x}',
                    'person_ids':[f'person-{i%5000}']}
                f.write(json.dumps(row,separators=(',',':'))+'\n')
        size=data.stat().st_size
        digest=hash_file(data)
        begin=time.monotonic()
        result=load_jsonl(root/'bench.sqlite3',data,source_id='synthetic_benchmark',
                          expected_sha256=digest,acquired_at=datetime(2026,10,24,tzinfo=timezone.utc))
        duration=time.monotonic()-begin
        return {'task':'SYNTHETIC_ENGINEERING_BENCHMARK_NOT_POLITICAL_RESEARCH',
                'rows':rows,'input_bytes':size,'elapsed_seconds':round(duration,3),
                'rows_per_second':round(rows/duration,1),'peak_rss_kb_process':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                'ingestion_status':result['status'],
                'method':'single SQLite connection with one atomic transaction; same computer; non-distributed'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rows',type=int,default=100_000);a=p.parse_args()
    print(json.dumps(benchmark(a.rows),indent=2))
