from datetime import datetime,timezone
import pytest
import politics_fantasy.groupvotes as mod
from politics_fantasy.groupvotes import read_group_snapshot,reconcile_groups,group_release_difference
from politics_fantasy.field_ingest import read_snapshot
T=datetime(2026,10,25,tzinfo=timezone.utc)
HEADER='votacion_id,fecha,grupo,si,no,abstencion,no_vota\n'
L1='s202-v01,2026-09-30,A,1,0,0,0\n'
L2='s202-v01,2026-09-30,B,0,1,0,0\n'
A='id,fecha,si,no,abstencion,no_vota\ns202-v01,2026-09-30,1,1,0,0\n'
I='votacion_id,fecha,diputado_id,grupo,voto\ns202-v01,2026-09-30,001,A,Sí\n'
def file(tmp_path,s,name='x.csv'):
 p=tmp_path/name;p.write_text(s,encoding='utf-8');return p
def parse(tmp_path,s,when=T):return read_group_snapshot(file(tmp_path,s),acquired_at=when)
def agg(tmp_path):return read_snapshot(file(tmp_path,A,'a.csv'),kind='aggregate',acquired_at=T)

def test_br30c_13_bounded_input_bytes(tmp_path,monkeypatch):
 monkeypatch.setattr(mod,'MAX_CSV_BYTES',30)
 with pytest.raises(ValueError,match='large'):
  parse(tmp_path,HEADER+L1)

def test_br30c_14_duplicate_header_fail_closed(tmp_path):
 with pytest.raises(ValueError,match='header'):
  parse(tmp_path,HEADER.replace('grupo,si','grupo,grupo,si')+L1.replace(',A,1',',A,A,1'))

def test_br30c_15_conflicting_group_vote_dates(tmp_path):
 src=HEADER+L1+L2.replace('2026-09-30','2026-09-29')
 r=reconcile_groups(parse(tmp_path,src),agg(tmp_path))
 assert r['group_votes_with_conflicting_dates']==1
 assert r['summary']['GROUP_INTERNAL_DATE_CONFLICT']==1

def test_br30c_16_missing_nominal_is_not_no_vote(tmp_path):
 g=parse(tmp_path,HEADER+L1+L2)
 i=read_snapshot(file(tmp_path,I,'i.csv'),kind='individual',acquired_at=T)
 r=reconcile_groups(g,agg(tmp_path),i)
 assert r['nominal_group_undercounts']==1 and r['nominal_group_complete'] is False
 assert r['nominal_group_overages']==0

def test_br30c_17_release_diff_ignores_row_position(tmp_path):
 x=parse(tmp_path,HEADER+L1+L2)
 y=parse(tmp_path,HEADER+L2+L1)
 assert group_release_difference(x,y)['modified']==0
 z=parse(tmp_path,HEADER+L1+L2.replace(',0,1,0,0',',0,2,0,0'))
 assert group_release_difference(x,z)['modified']==1

def test_br30c_18_snapshot_not_publication_history(tmp_path):
 x=parse(tmp_path,HEADER+L1)
 y=parse(tmp_path,HEADER+L1,datetime(2026,10,26,tzinfo=timezone.utc))
 d=group_release_difference(x,y)
 assert d['old_sha256']==d['new_sha256']
 assert d['old_observed_at']!=d['new_observed_at']
 assert 'NOT_FIRST_PUBLICATION' in d['meaning']
