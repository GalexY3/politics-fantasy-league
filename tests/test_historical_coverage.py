from pathlib import Path
import json
import pytest
from politics_fantasy.historical_coverage import load_jsonl, summary, git_blob_hash

def record(day='2023-09-19', id='s2-v001', groups=True):
    return {'id':id,'fecha':day,'sesion':2,'totales':{'si':2,'no':1,'abstencion':0,'noVota':1},
            'votos':{'S':'1','N':'2','X':'3'},
            'grupos':{'GP':[2,1,0,1]} if groups else {}}

def source(tmp_path,records):
    p=tmp_path/'votos.jsonl';p.write_text('\n'.join(json.dumps(x) for x in records)+'\n',encoding='utf8');return p

def test_git_hash(tmp_path):
    p=source(tmp_path,[record()]); rows,pv=load_jsonl(p,expected_blob_sha1=git_blob_hash(p.read_bytes()))
    assert pv['git_blob_sha1']==git_blob_hash(p.read_bytes())
    assert summary(rows,pv)['nominal_rows']==3

def test_wrong_sha(tmp_path):
    with pytest.raises(ValueError,match='SHA-1'):load_jsonl(source(tmp_path,[record()]),expected_blob_sha1='0'*40)

def test_duplicate_critical(tmp_path):
    with pytest.raises(ValueError,match='duplicate'):load_jsonl(source(tmp_path,[record(),record()]))

def test_cross_choice_duplicate(tmp_path):
    x=record();x['votos']['N']='1'
    with pytest.raises(ValueError,match='duplicated'):load_jsonl(source(tmp_path,[x]))

def test_over_total(tmp_path):
    x=record();x['totales']['si']=0
    with pytest.raises(ValueError,match='exceeds'):load_jsonl(source(tmp_path,[x]))

def test_group_conflict(tmp_path):
    x=record();x['grupos']['GP'][0]=1
    with pytest.raises(ValueError,match='contradicts'):load_jsonl(source(tmp_path,[x]))

def test_empty_nominal_is_not_absent(tmp_path):
    x=record();x['votos']={};x['grupos']={}
    rows,pv=load_jsonl(source(tmp_path,[x]));s=summary(rows,pv)
    assert s['without_nominal']==1 and s['nominal_rows']==0 and s['total_positions']==4
    assert s['inference_gate']!='CERTIFIED'

def test_no_vote_is_not_missing(tmp_path):
    rows,pv=load_jsonl(source(tmp_path,[record()]));s=summary(rows,pv)
    assert s['missing_by_choice_on_votes_with_nominal']=={'S':1,'N':0,'A':0,'X':0}
    assert s['explicit_no_votes_total']==1

def test_bootstrap_determinism(tmp_path):
    x=record();y=record(day='2026-02-19',id='s10-v001');y['sesion']=10
    rows,pv=load_jsonl(source(tmp_path,[x,y]));a=summary(rows,pv);b=summary(rows,pv)
    assert a['cluster_bootstrap_2023_2026']==b['cluster_bootstrap_2023_2026']

def test_rejects_unknown_vote_code(tmp_path):
    x=record();x['votos']['Q']='4'
    with pytest.raises(ValueError,match='compact'):load_jsonl(source(tmp_path,[x]))
