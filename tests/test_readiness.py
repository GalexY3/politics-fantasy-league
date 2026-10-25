from datetime import datetime,timezone
from pathlib import Path
import pytest
from politics_fantasy.field_cli import make_field_report,main
from politics_fantasy.field_ingest import read_snapshot
from politics_fantasy.readiness import (research_readiness,observed_label_transitions,
    as_of_snapshot_gate,yes_share_bounds)
T=datetime(2026,10,25,tzinfo=timezone.utc)
I='votacion_id,fecha,diputado_id,diputado,grupo,voto\ns202-v01,2026-09-30,001,Private Name,A,Sí\ns202-v01,2026-09-30,002,Private Name B,B,No\n'
A='id,fecha,si,no,abstencion,no_vota\ns202-v01,2026-09-30,1,1,0,0\n'
G='votacion_id,fecha,grupo,si,no,abstencion,no_vota\ns202-v01,2026-09-30,A,1,0,0,0\ns202-v01,2026-09-30,B,0,1,0,0\n'
def inputs(tmp_path):
 for name,body in [('i.csv',I),('a.csv',A),('g.csv',G)]: (tmp_path/name).write_text(body)
 return tmp_path/'i.csv',tmp_path/'a.csv',tmp_path/'g.csv'

def test_br30c_25_consistency_is_not_scientific_ready(tmp_path):
 i,a,g=inputs(tmp_path);r=make_field_report(individual=i,aggregate=a,group=g,acquired_at=T)
 assert not r['reconciliation']['any_unresolved'] and r['group_audit']['aggregate_consistent']
 z=research_readiness(r)
 assert z['status']=='NOT_READY_FOR_EMPIRICAL_CLAIMS'
 assert z['VSDS_upper_bound_without_new_field_validation']==1

def test_br30c_26_group_change_not_defection(tmp_path):
 i,a,g=inputs(tmp_path)
 i.write_text(I+'s203-v01,2026-10-01,001,Private Name,B,Sí\n')
 z=observed_label_transitions(read_snapshot(i,kind='individual',acquired_at=T))
 assert z['deputy_ids_with_different_reported_group_over_time']==1
 assert z['historical_roster_certified'] is False and 'NOT_CAUSAL' in z['interpretation']

def test_br30c_27_historical_asof_never_leaks_new_download(tmp_path):
 i,a,g=inputs(tmp_path);r=make_field_report(individual=i,aggregate=a,group=g,acquired_at=T)
 old=as_of_snapshot_gate(r,datetime(2025,1,1,tzinfo=timezone.utc))
 assert not old['eligible_for_historical_prediction'] and 'AFTER' in old['reason']
 new=as_of_snapshot_gate(r,datetime(2027,1,1,tzinfo=timezone.utc))
 assert not new['eligible_for_historical_prediction'] and new['usable_for_descriptive_audit_as_of']

def test_br30c_28_no_roster_no_eligibility_claim():
 x=yes_share_bounds(yes=2,observed=3,eligible_roster=None)
 assert x['lower'] is None and x['upper'] is None and x['unknown_count'] is None

def test_br30c_29_algebraic_bounds_for_explicit_roster():
 x=yes_share_bounds(yes=2,observed=5,eligible_roster=10)
 assert x['lower']==0.2 and x['upper']==0.7 and x['unknown_count']==5
 assert yes_share_bounds(yes=2,observed=5,eligible_roster=5)['lower']==0.4
 with pytest.raises(ValueError):yes_share_bounds(yes=2,observed=5,eligible_roster=3)

def test_br30c_30_three_source_cli_end_to_end(tmp_path):
 i,a,g=inputs(tmp_path);output=tmp_path/'field.json'
 assert main(['--individual',str(i),'--aggregate',str(a),'--group',str(g),
              '--acquired-at',T.isoformat(),'--out',str(output)])==0
 import json
 z=json.loads(output.read_text())
 assert z['group_audit']['aggregate_consistent'] and 'source_snapshots' in z
 assert research_readiness(z)['VSDS_upper_bound_without_new_field_validation']==1
