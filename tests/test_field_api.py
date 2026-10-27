import json, threading,urllib.request,urllib.error
from http.server import ThreadingHTTPServer
from pathlib import Path
from datetime import datetime,timezone
from politics_fantasy.field_api import local_field_status
from politics_fantasy.field_cli import make_field_report,write_report_once
from politics_fantasy.server import handler_factory
from politics_fantasy.product import seed_demo

T=datetime(2026,10,25,tzinfo=timezone.utc)

def receipt(tmp):
 i=tmp/'i.csv';a=tmp/'a.csv'
 i.write_text('votacion_id,fecha,diputado_id,diputado,grupo,voto\ns202-v020,2026-09-30,001,NotPublicName,G1,Sí\n', encoding="utf-8")
 a.write_text('id,fecha,si,no,abstencion,no_vota\ns202-v020,2026-09-30,1,0,0,0\n', encoding="utf-8")
 r=make_field_report(individual=i,aggregate=a,acquired_at=T)
 out=tmp/'out.json';write_report_once(r,out)
 return out

def test_b30b_25_missing_receipt_cannot_implicate_real_mps(tmp_path):
 x=local_field_status(tmp_path/'missing.json')
 assert x['mode']=='FIELD_CSV_NOT_IMPORTED' and x['VSDS']==1 and not x['real_person_scoring']

def test_b30b_26_valid_report_digest_check_and_sanitized_counts(tmp_path):
 x=local_field_status(receipt(tmp_path))
 assert x['mode']=='USER_SUPPLIED_CSV_UNCERTIFIED' and x['n_nominal_rows']==1
 assert x['reconciliation_complete']

def test_b30b_27_tampering_report_returns_rejected(tmp_path):
 file=receipt(tmp_path);r=json.loads(file.read_text(encoding="utf-8"));r['coverage']['individual']['n_rows']=999
 file.write_text(json.dumps(r), encoding="utf-8");x=local_field_status(file)
 assert x['mode']=='FIELD_REPORT_REJECTED' and not x['certified']

def test_b30b_28_client_never_receives_personal_rows(tmp_path):
 x=local_field_status(receipt(tmp_path));payload=json.dumps(x)
 assert 'NotPublicName' not in payload and '001' not in payload
 assert 'n_deputy_ids' in x and 'deputy_id' not in x

def test_b30b_29_frontend_visible_limits_and_offline_documentation():
 root=Path(__file__).resolve().parents[1]/'src/politics_fantasy/web'
 js=(root/'app.js').read_text(encoding="utf-8")
 assert '/api/field' in js and 'fieldPanel()' in js
 assert 'SIN CSV NOMINALES IMPORTADOS' in js and 'Esto NO certifica autenticidad' in js
 assert 'No se atribuyen puntos' not in js or 'Sin puntos para personas reales' in js

def test_b30b_30_local_get_read_only_and_synthetic_game_isolation(tmp_path):
 db=tmp_path/'game.db';seed_demo(db);rc=receipt(tmp_path)
 server=ThreadingHTTPServer(('127.0.0.1',0),handler_factory(db,None,rc))
 t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
 try:
  base=f'http://127.0.0.1:{server.server_port}'
  with urllib.request.urlopen(base+'/api/field') as r: f=json.load(r)
  assert f['mode']=='USER_SUPPLIED_CSV_UNCERTIFIED' and not f['real_person_scoring']
  with urllib.request.urlopen(base+'/api/state') as r: s=json.load(r)
  assert s['mode']=='SYNTHETIC_FICTIONAL_DEMO_ONLY'
  request=urllib.request.Request(base+'/api/field',data=b'{}',headers={'Content-Type':'application/json'},method='POST')
  try:urllib.request.urlopen(request)
  except urllib.error.HTTPError as e:assert e.code==404
  else:assert False,'No field write route allowed'
 finally:server.shutdown();server.server_close();t.join(timeout=3)
