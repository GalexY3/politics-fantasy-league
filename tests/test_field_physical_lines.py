"""C10: physical source positions for quoted multiline CSV rows, synthetic data."""
from datetime import datetime, timezone
from politics_fantasy.field_ingest import read_snapshot
import pytest

T=datetime(2026,10,28,tzinfo=timezone.utc)
H='votacion_id,fecha,temas,diputado_id,grupo,voto\n'
R1='s202-v1,2026-09-30,"asunto\notro",001,GR1,Sí\n'
R2='s202-v2,2026-09-30,normal,002,GR1,No\n'

def test_source_line_is_physical_record_end_not_logical_ordinal(tmp_path):
    p=tmp_path/'fixture.csv'
    p.write_text(H+R1+R2,encoding='utf8')
    rows=read_snapshot(p,kind='individual',acquired_at=T).rows
    assert [r.source_line for r in rows]==[3,4]

def test_duplicate_error_identifies_end_of_physical_record(tmp_path):
    p=tmp_path/'fixture.csv'
    p.write_text(H+R1+R1,encoding='utf8')
    with pytest.raises(ValueError,match='physical line 5'):
        read_snapshot(p,kind='individual',acquired_at=T)
