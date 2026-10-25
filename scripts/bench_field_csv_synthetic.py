"""Explicitly synthetic importer stress check, never parliamentary source evidence."""
import json, tempfile, time
from datetime import datetime, timezone
from pathlib import Path
from politics_fantasy.field_ingest import read_snapshot, summary_one

def run(votes=200, figures=350):
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'SYNTHETIC_NOT_SPAIN.csv'
        with p.open('w',encoding='utf-8',newline='') as f:
            f.write('votacion_id,fecha,diputado_id,grupo,voto\n')
            for v in range(votes):
                for i in range(figures):
                    f.write(f's{v+1}-v001,2026-09-30,SYN-{i:04d},SYN-G{i%5},Sí\n')
        size=p.stat().st_size
        start=time.perf_counter()
        r=read_snapshot(p,kind='individual',acquired_at=datetime.now(timezone.utc))
        elapsed=time.perf_counter()-start
        return {'status':'SYNTHETIC_ONLY','rows':len(r.rows),'bytes':size,'seconds':round(elapsed,4),
                'rows_per_second':round(len(r.rows)/elapsed),'synthetic_sessions':votes,
                'source_verified':False,'grade_vdss':1}

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
