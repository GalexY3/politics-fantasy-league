from datetime import datetime, timezone
import pytest
from politics_fantasy.field_ingest import read_snapshot, summary_one

T=datetime(2026,10,25,tzinfo=timezone.utc)
H='votacion_id,fecha,temas,diputado_id,diputado,grupo,circunscripcion,voto\n'
ROW='s202-v020,2026-09-30,instituciones,001,Actor 1,GR1,Madrid,Sí\n'
A='id,fecha,si,no,abstencion,no_vota\ns202-v020,2026-09-30,1,0,0,0\n'

def file(tmp_path,content):
 p=tmp_path/'t.csv';p.write_bytes(content.encode('utf-8'));return p

def test_b30b_01_schema_and_identity_preserves_leading_zeros(tmp_path):
 obj=read_snapshot(file(tmp_path,H+ROW),kind='individual',acquired_at=T)
 assert obj.rows[0].deputy_id=='001' and obj.rows[0].choice=='YES'
 assert obj.provenance.input_bytes==len((H+ROW).encode())

def test_b30b_02_choice_is_closed_vocabulary(tmp_path):
 with pytest.raises(ValueError,match='Unknown vote choice'):
  read_snapshot(file(tmp_path,H+ROW.replace(',Sí\n',',A favor\n')),kind='individual',acquired_at=T)

def test_b30b_03_duplicates_rejected_even_if_identical(tmp_path):
 with pytest.raises(ValueError,match='Duplicate nominal'):
  read_snapshot(file(tmp_path,H+ROW+ROW),kind='individual',acquired_at=T)

def test_b30b_04_no_guessing_source_publication_or_group_history(tmp_path):
 obj=read_snapshot(file(tmp_path,H+ROW),kind='individual',acquired_at=T)
 assert obj.provenance.provenance_status=='LOCAL_BYTES_NOT_INDEPENDENTLY_CERTIFIED'
 assert obj.group_at_vote_certified is False
 assert not hasattr(obj.rows[0],'first_public_at')

def test_b30b_05_aggregate_schema_counts_checked(tmp_path):
 obj=read_snapshot(file(tmp_path,A),kind='aggregate',acquired_at=T)
 assert obj.rows[0].yes==1
 with pytest.raises(ValueError,match='Counts must be nonnegative integers'):
  read_snapshot(file(tmp_path,A.replace(',1,0,0,0',',1,-1,0,0')),kind='aggregate',acquired_at=T)

def test_b30b_06_byte_hash_and_missing_census_not_fabricated(tmp_path):
 obj=read_snapshot(file(tmp_path,H+ROW),kind='individual',acquired_at=T)
 assert len(obj.provenance.sha256)==64
 assert summary_one(obj)['unknown_rows']=='NOT_ESTIMABLE_WITHOUT_ROSTER'
 assert summary_one(obj)['n_deputy_ids']==1
