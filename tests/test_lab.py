import json
import threading
import urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
import pytest
from politics_fantasy.lab import synthetic_rollcalls, local_lab_report, project_value_grade
from politics_fantasy.server import handler_factory
from politics_fantasy.product import seed_demo


def test_br30_25_rollcall_fixture_reproducible_and_fictional():
 a=synthetic_rollcalls();b=synthetic_rollcalls()
 assert a==b and len(a)==11
 assert all(v.person_id.startswith('SYN-') and v.source_sha256=='0'*64 for v in a)

def test_br30_26_lab_participation_shows_unknown_and_true_no_vote():
 r=local_lab_report()
 p={x['actor']:x for x in r['participation']}
 assert p['SYN-P04']['unknown']==1 and p['SYN-P04']['explicit_no_vote']==1
 assert p['SYN-P04']['participation'] is None
 assert p['SYN-P01']['participation']==1

def test_br30_27_lab_comparator_exposes_joint_n_and_marginal_chance():
 p=local_lab_report()['pair_comparison']
 assert p['joint_n']==3 and p['chance']>=0 and p['observed']>=0
 assert p['status']=='DESCRIPTIVE_SYNTHETIC_NOT_INFLUENCE'

def test_br30_28_vsds_never_awards_field_value_to_synthetics():
 assert project_value_grade(artifact_valid=True)['grade']==1
 assert project_value_grade(artifact_valid=False)['grade']==0
 assert project_value_grade(artifact_valid=True,source_certified=True,semantics_audited=True,
                            baseline_competent=True,coverage_certified=True)['grade']==2
 assert project_value_grade(artifact_valid=True,source_certified=True,semantics_audited=True,
                            baseline_competent=True,coverage_certified=True,independently_replicated=True,
                            utility_demonstrated=True)['grade']==3
 assert local_lab_report()['value_grade']['scientific_novelty_grade']==0

def test_br30_29_readonly_api_lab_independent_game(tmp_path):
 db=tmp_path/'lab.db';seed_demo(db)
 srv=ThreadingHTTPServer(('127.0.0.1',0),handler_factory(db,None))
 t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
 try:
  base=f'http://127.0.0.1:{srv.server_port}'
  with urllib.request.urlopen(base+'/api/lab') as resp:r=json.load(resp)
  assert r['mode']=='SYNTHETIC_NOT_SPANISH_PARLIAMENT' and not r['real_politician_scoring']
  assert len(r['report_sha256'])==64
  with urllib.request.urlopen(base+'/api/state') as resp:s=json.load(resp)
  assert s['mode']=='SYNTHETIC_FICTIONAL_DEMO_ONLY'
 finally:
  srv.shutdown();srv.server_close();t.join(timeout=3)

def test_br30_30_frontend_has_explicit_demo_and_unknown_labels():
 root=Path(__file__).resolve().parents[1]/'src/politics_fantasy/web'
 js=(root/'app.js').read_text(encoding='utf-8')
 assert '/api/lab' in js and 'labPanel()' in js
 assert 'SINTÉTICO, NO POLÍTICOS REALES' in js
 assert "?'DESCONOCIDA'" in js
 assert 'No son votos parlamentarios reales' in js
