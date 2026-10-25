import json
import subprocess
import sys
from datetime import datetime,timezone
import pytest
from politics_fantasy.field_cli import make_field_report,write_report_once,main
T=datetime(2026,10,25,tzinfo=timezone.utc)
I='votacion_id,fecha,temas,diputado_id,diputado,grupo,voto\ns202-v020,2026-09-30,x,001,Confidential Display Name,G1,Sí\n'
A='id,fecha,si,no,abstencion,no_vota\ns202-v020,2026-09-30,1,0,0,0\n'

def mk(tmp):
 i=tmp/'i.csv';a=tmp/'a.csv';i.write_text(I);a.write_text(A);return i,a

def test_b30b_19_report_produced_with_field_provenance(tmp_path):
 i,a=mk(tmp_path);r=make_field_report(individual=i,aggregate=a,acquired_at=T)
 assert len(r['report_sha256'])==64 and r['source_snapshots']['individual']['bytes']>0

def test_b30b_20_report_digest_reproducible(tmp_path):
 i,a=mk(tmp_path)
 x=make_field_report(individual=i,aggregate=a,acquired_at=T)
 assert x==make_field_report(individual=i,aggregate=a,acquired_at=T)

def test_b30b_21_write_once_not_silent_overwrite(tmp_path):
 i,a=mk(tmp_path);r=make_field_report(individual=i,aggregate=a,acquired_at=T)
 p=tmp_path/'out/report.json';write_report_once(r,p)
 with pytest.raises(FileExistsError):write_report_once(r,p)
 assert json.loads(p.read_text())==r

def test_b30b_22_report_has_no_deputy_identifiers_or_names(tmp_path):
 i,a=mk(tmp_path);r=make_field_report(individual=i,aggregate=a,acquired_at=T)
 dump=json.dumps(r)
 assert 'Confidential Display Name' not in dump and '001' not in dump
 assert not r['may_score_real_persons'] and r['VSDS']['grade']==1

def test_b30b_23_no_false_source_attestation_on_perfect_match(tmp_path):
 i,a=mk(tmp_path);r=make_field_report(individual=i,aggregate=a,acquired_at=T)
 assert not r['reconciliation']['any_unresolved']
 assert not r['gate']['inference_ready'] and not r['membership_at_vote_certified']

def test_b30b_24_cli_end_to_end_and_reject_naive_timestamp(tmp_path):
 i,a=mk(tmp_path);out=tmp_path/'o.json'
 assert main(['--individual',str(i),'--aggregate',str(a),
              '--acquired-at',T.isoformat(),'--out',str(out)])==0
 assert out.is_file()
 with pytest.raises(SystemExit) as exc:
  main(['--individual',str(i),'--aggregate',str(a),
        '--acquired-at','2026-10-25T09:00:00','--out',str(tmp_path/'bad.json')])
 assert exc.value.code==2
