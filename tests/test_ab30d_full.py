"""AB30D independent regression checks of the published computational ledger."""
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DR=ROOT/'research'/'AB30_COMPLETOS_20261025'

def _load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def test_registered_30_distinct_estimands_with_disjoint_seeds():
    experiment=_load('ab30d_full')
    assert experiment.check_invariants()==30
    prereg=json.loads((DR/'PREREG.json').read_text(encoding="utf-8"))
    assert len({(x['A']['claim'],x['A']['estimand']) for x in prereg['cases']})==30

def test_results_record_all_A_through_J_without_field_claims():
    d=json.loads((DR/'RESULTS_AUDITED.json').read_text(encoding="utf-8"))
    assert d['n_cycles_A_to_J_completed_computational']==30
    assert d['n_empirical_field_cycles']==0
    assert d['n_independent_external_replications']==0
    assert d['VSDS']=='1/3' and d['CT2_prediction']==24
    assert d['scientific_novelties_N1_N2_N3']==[0,0,0]
    assert all(set('ABCDEFGHIJ').issubset(x) for x in d['cycles'])
    assert all(x['G']['independent_external_replication'] is False for x in d['cycles'])
    assert all(x['E']['run_stress_holdout']['n']==80 for x in d['cycles'])

def test_adversarial_audit_rejects_leakage_and_mismatched_units():
    d=json.loads((DR/'RESULTS_AUDITED.json').read_text(encoding="utf-8"))
    by={c['id']:c for c in d['cycles']}
    for cid in ['T13','T17','M05','R19','R22','F29']:
        assert by[cid]['J']['scientific_verdict'].startswith('INVALID')
    assert by['C09']['J']['scientific_verdict']=='STRESS_REVERSAL'
    assert by['M03']['J']['scientific_verdict']=='IDENTIFICATION_FAILURE'
    assert by['M01']['J']['scientific_verdict']=='NEGATIVE_CONTROL'
    assert sum(d['audit_grade_counts'].values())==30

def test_independent_seed_streams_are_deterministic():
    f=_load('ab30d_full')
    for code in ('M03','C09','T15','R21','F28'):
        for mode in ('main','holdout','ablation'):
            assert f.simulate(code,123456,mode)==f.simulate(code,123456,mode)

def test_known_negative_controls_and_ablations():
    f=_load('ab30d_full')
    for code in ('M04','M06','C11','C12','T16','R24','F25','F27','F30'):
        a,b,_=f.simulate(code,32142,'ablation')
        assert a >=0 and b>=0
        assert abs(a-b)<1e-10,(code,a,b)

def test_audit_source_hash_unchanged():
    import hashlib
    p=json.loads((DR/'RESULTS_AUDITED.json').read_text(encoding="utf-8"))
    assert p['source_raw_result_sha256']==hashlib.sha256((DR/'RESULTS.json').read_bytes()).hexdigest()
    assert p['source_prereg_sha256']==hashlib.sha256((DR/'PREREG.json').read_bytes()).hexdigest()
