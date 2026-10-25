from datetime import datetime,timezone
import pytest
from politics_fantasy.field_ingest import read_snapshot
from politics_fantasy.reconcile import reconcile,group_snapshot,snapshot_difference
T=datetime(2026,10,25,tzinfo=timezone.utc)
I='votacion_id,fecha,diputado_id,grupo,voto\n'
A='id,fecha,si,no,abstencion,no_vota\n'
V='s202-v020,2026-09-30'

def mk(tmp,prefix,body,kind):
 p=tmp/f'{kind}{len(list(tmp.iterdir()))}.csv';p.write_text(prefix+body,encoding='utf-8')
 return read_snapshot(p,kind=kind,acquired_at=T)

def test_b30b_07_equal_sources_only_consistent(tmp_path):
 i=mk(tmp_path,I,V+',001,GR1,Sí\n', 'individual')
 a=mk(tmp_path,A,V+',1,0,0,0\n', 'aggregate')
 r=reconcile(i,a)
 assert r['summary']=={'COUNTS_MATCH_NOT_CERTIFIED':1} and not r['any_unresolved']
 assert r['status']=='SOURCE_CONSISTENCY_ONLY_NOT_VALIDATION'

def test_b30b_08_partial_filter_not_spurious_absence(tmp_path):
 i=mk(tmp_path,I,V+',001,GR1,Sí\n','individual')
 a=mk(tmp_path,A,V+',2,0,0,0\n','aggregate')
 assert reconcile(i,a)['votes'][0]['status']=='PARTIAL_NOMINAL_OR_FILTERED'

def test_b30b_09_excess_nominal_is_discrepancy(tmp_path):
 i=mk(tmp_path,I,V+',001,GR1,Sí\n'+V+',002,GR1,Sí\n','individual')
 a=mk(tmp_path,A,V+',1,0,0,0\n','aggregate')
 assert reconcile(i,a)['votes'][0]['status']=='NOMINAL_EXCEEDS_AGGREGATE_CONFLICT'

def test_b30b_10_missing_table_events_not_zero_filled(tmp_path):
 i=mk(tmp_path,I,V+',001,GR1,Sí\n','individual')
 a=mk(tmp_path,A,'s202-v021,2026-09-30,1,0,0,0\n','aggregate')
 x=reconcile(i,a)
 assert set(x['summary'])=={'NOMINAL_ONLY_MISSING_AGGREGATE','AGGREGATE_ONLY_MISSING_NOMINAL'}

def test_b30b_11_group_counts_no_unobserved_members(tmp_path):
 i=mk(tmp_path,I,V+',001,GR1,No vota\n','individual')
 g=group_snapshot(i)
 assert g['GR1']['NO_VOTE']==1 and g['GR1']['coverage']=='OBSERVED_ROWS_ONLY'
 assert g['GR1']['group_history']=='LABEL_AS_REPORTED_UNVERIFIED'

def test_b30b_12_snapshot_delta_not_false_revision_from_order(tmp_path):
 one=mk(tmp_path,I,V+',001,GR1,Sí\n'+V+',002,GR1,No\n','individual')
 two=mk(tmp_path,I,V+',002,GR1,No\n'+V+',001,GR1,Sí\n','individual')
 three=mk(tmp_path,I,V+',001,GR1,No\n'+V+',002,GR1,No\n','individual')
 assert snapshot_difference(one,two)['modified']==0
 assert snapshot_difference(one,three)['modified']==1
