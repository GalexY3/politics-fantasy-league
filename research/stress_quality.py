"""Deterministic 100k-row SYNTHETIC streaming audit (software stress, never politics data)."""
from pathlib import Path
import sys, json, time, tempfile
from hashlib import sha256
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from politics_fantasy.quality import audit_jsonl


def main(n=100_000):
    # Strict deterministic typed records; content has no politicians.
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp)/'synthetic.jsonl'
        digest=sha256(b'SYNTHETIC_TEST_FIXTURE').hexdigest()
        with p.open('w') as f:
            for i in range(n):
                row={"source_id":"synthetic", "event_id":f"E{i:06d}",
                     "event_kind":"speech_recorded", "occurred_at":"2026-01-02T00:00:00+00:00",
                     "first_public_at":"2026-01-03T00:00:00+00:00",
                     "source_url":"https://example.invalid/FAKE", "raw_sha256":digest,
                     "person_ids":[f"P{i%1000}"]}
                f.write(json.dumps(row,separators=(',',':'))+'\n')
        size=p.stat().st_size
        start=time.perf_counter()
        a=audit_jsonl(p)
        elapsed=time.perf_counter()-start
    assert a['counts']['rows']==n and a['counts']['parseable']==n
    assert a['counts'].get('duplicate_same_revision',0)==0
    return {'kind':'SYNTHETIC_SOFTWARE_STRESS', 'rows':n, 'bytes':size,
            'elapsed_seconds':round(elapsed,4), 'rows_per_second':round(n/elapsed),
            'audit':a, 'warning':'Not real political data; no source/API throughput measured.'}


if __name__=='__main__':
    r=main()
    print(json.dumps(r,indent=2))
    out=Path(__file__).resolve().parent/'stress_result_SYNTHETIC.json'
    out.write_text(json.dumps(r,indent=2))
