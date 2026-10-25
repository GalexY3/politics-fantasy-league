from datetime import datetime,timezone
from pathlib import Path
import json
import pytest
from politics_fantasy.field_cli import make_field_report,main,write_report_once
from politics_fantasy.field_api import local_field_status
T=datetime(2026,10,25,tzinfo=timezone.utc)
I='votacion_id,fecha,diputado_id,diputado,grupo,voto\ns202-v01,2026-09-30,001,Private Name,A,Sí\ns202-v01,2026-09-30,002,Other Private Name,B,No\n'
A='id,fecha,si,no,abstencion,no_vota\ns202-v01,2026-09-30,1,1,0,0\n'
G='votacion_id,fecha,grupo,si,no,abstencion,no_vota\ns202-v01,2026-09-30,A,1,0,0,0\ns202-v01,2026-09-30,B,0,1,0,0\n'
def paths(tmp):
 for name,body in [('i.csv',I),('a.csv',A),('g.csv',G)]: (tmp/name).write_text(body)
 return tmp/'i.csv',tmp/'a.csv',tmp/'g.csv'

def test_br30c_19_optional_third_table_report(tmp_path):
 i,a,g=paths(tmp_path);r=make_field_report(individual=i,aggregate=a,group=g,acquired_at=T)
 assert r['group_audit']['group_rows']==2 and r['group_audit']['aggregate_consistent']
 assert r['group_audit']['nominal_group_complete'] and len(r['source_snapshots']['group']['sha256'])==64

def test_br30c_20_backward_compatible_report_unchanged(tmp_path):
 i,a,g=paths(tmp_path)
 r=make_field_report(individual=i,aggregate=a,acquired_at=T)
 assert 'group_audit' not in r and 'group' not in r['source_snapshots']
 assert r==make_field_report(individual=i,aggregate=a,acquired_at=T)

def test_br30c_21_cli_group_invalid_rejected_atomically(tmp_path):
 i,a,g=paths(tmp_path);g.write_text('invalid\n1\n');out=tmp_path/'report.json'
 with pytest.raises(SystemExit) as err:
  main(['--individual',str(i),'--aggregate',str(a),'--group',str(g),
        '--acquired-at',T.isoformat(),'--out',str(out)])
 assert err.value.code==2 and not out.exists()

def test_br30c_22_signed_report_privacy(tmp_path):
 i,a,g=paths(tmp_path);r=make_field_report(individual=i,aggregate=a,group=g,acquired_at=T)
 text=json.dumps(r);assert 'Private Name' not in text and 'Other Private Name' not in text
 assert not r['may_score_real_persons'] and not r['membership_at_vote_certified']

def test_br30c_23_whitelist_group_api_and_tamper_fail_closed(tmp_path):
 i,a,g=paths(tmp_path);r=make_field_report(individual=i,aggregate=a,group=g,acquired_at=T)
 out=tmp_path/'receipt.json';write_report_once(r,out)
 state=local_field_status(out);assert state['group_audit']['group_rows']==2
 assert 'Private Name' not in json.dumps(state) and 'group' not in state['group_audit']
 r['group_audit']['group_rows']+=1;out.write_text(json.dumps(r))
 assert local_field_status(out)['mode']=='FIELD_REPORT_REJECTED'

def test_br30c_24_ui_group_limits_visible():
 js=(Path(__file__).parents[1]/'src/politics_fantasy/web/app.js').read_text()
 assert 'No mide disciplina partidista.' in js and 'Sin puntos para personas reales.' in js
 assert 'g.aggregate_consistent' in js and 'g.nominal_group_complete' in js
