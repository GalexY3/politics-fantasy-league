from datetime import datetime,timezone
from pathlib import Path
import pytest
from politics_fantasy.field_ingest import read_snapshot
from politics_fantasy.groupvotes import read_group_snapshot,majority,reconcile_groups

T=datetime(2026,10,25,tzinfo=timezone.utc)
G='votacion_id,fecha,grupo,si,no,abstencion,no_vota\ns202-v01,2026-09-30,A,1,0,0,0\ns202-v01,2026-09-30,B,0,1,0,0\n'
A='id,fecha,si,no,abstencion,no_vota\ns202-v01,2026-09-30,1,1,0,0\n'
I='votacion_id,fecha,diputado_id,grupo,voto\ns202-v01,2026-09-30,001,A,Sí\ns202-v01,2026-09-30,002,B,No\n'
def fixture(tmp_path,content,name='x.csv'):
 p=tmp_path/name;p.write_text(content,encoding='utf-8');return p

def test_br30c_01_group_csv_field_id_and_label(tmp_path):
 g=read_group_snapshot(fixture(tmp_path,G),acquired_at=T)
 assert g.rows[0].group=='A' and g.rows[0].vote_id=='s202-v01' and not g.certified

def test_br30c_02_group_nonnegative_capacity(tmp_path):
 for bad in ('-1','351','1.2'):
  with pytest.raises(ValueError):read_group_snapshot(fixture(tmp_path,G.replace('A,1,0,0,0',f'A,{bad},0,0,0')),acquired_at=T)

def test_br30c_03_group_duplicate_rejected(tmp_path):
 with pytest.raises(ValueError,match='Duplicate'):
  read_group_snapshot(fixture(tmp_path,G+G.splitlines(True)[1]),acquired_at=T)

def test_br30c_04_majority_ties_and_no_vote(tmp_path):
 g=read_group_snapshot(fixture(tmp_path,G.replace('A,1,0,0,0','A,1,1,0,14')),acquired_at=T)
 assert majority(g.rows[0])=='TIE'
 g=read_group_snapshot(fixture(tmp_path,G.replace('A,1,0,0,0','A,0,0,0,14')),acquired_at=T)
 assert majority(g.rows[0])=='NO_EXPRESSED_CHOICE'

def test_br30c_05_group_aggregate_reconciliation(tmp_path):
 g=read_group_snapshot(fixture(tmp_path,G),acquired_at=T)
 a=read_snapshot(fixture(tmp_path,A,'a.csv'),kind='aggregate',acquired_at=T)
 assert reconcile_groups(g,a)['aggregate_consistent']
 g2=read_group_snapshot(fixture(tmp_path,G.replace('B,0,1,0,0','B,0,0,0,0')),acquired_at=T)
 assert not reconcile_groups(g2,a)['aggregate_consistent']

def test_br30c_06_group_nominal_does_not_infer_missing(tmp_path):
 g=read_group_snapshot(fixture(tmp_path,G),acquired_at=T)
 a=read_snapshot(fixture(tmp_path,A,'a.csv'),kind='aggregate',acquired_at=T)
 i=read_snapshot(fixture(tmp_path,I.splitlines(True)[0]+I.splitlines(True)[1],'i.csv'),kind='individual',acquired_at=T)
 out=reconcile_groups(g,a,i)
 assert out['aggregate_consistent'] and out['nominal_group_overages']==0
 assert out['nominal_unmatched_group_rows']==0
 i2=read_snapshot(fixture(tmp_path,I.replace(',B,No',',X,No'),'i.csv'),kind='individual',acquired_at=T)
 assert reconcile_groups(g,a,i2)['nominal_unmatched_group_rows']==1
