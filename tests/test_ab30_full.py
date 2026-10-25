import json
import subprocess
import sys
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/upstream_curated_7/derived_anonymous_counts.json'
OUT=ROOT/'research/AB30_FULL_20261025'

def test_anonymous_curated_provenance():
    d=json.loads(DATA.read_text(encoding='utf-8'))
    assert d['source_git_blob_sha1']=='ecaf3b02b9a453265d6bcb588a9121ddaae9ed78'
    assert len(d['records'])==7
    for row in d['records']:
        assert sum(row['totals'])==350
        assert [sum(g[j+1] for g in row['groups']) for j in range(4)]==row['totals']

def test_missing_and_nonvote_separated():
    d=json.loads(DATA.read_text(encoding='utf-8'))
    gap=[sum(row['totals'])-sum(row['nominal']) for row in d['records']]
    assert gap==[4,0,4,4,4,8,18]
    assert sum(gap)==42
    assert sum(row['totals'][3] for row in d['records'])==26

def test_complete_aj_for_all_cycles():
    for i in range(1,31):
        p=OUT/f'C{i:02}.json'
        assert p.is_file(),p
        c=json.loads(p.read_text(encoding='utf-8'))
        assert all(k in c for k in 'ABCDEFGHIJ')
        assert c['I']['VSDS_grade_project']==1
        assert not c['G']['independent_confirmation']

def test_cycle_05_errata_retained():
    original=json.loads((OUT/'C05.json').read_text(encoding='utf-8'))
    corr=json.loads((OUT/'C05_ERRATA.json').read_text(encoding='utf-8'))
    assert original['E']['result']['spearman_approx_corr']==round(corr['old_value'],6)
    assert corr['old_value']!=corr['correct_value']
    assert corr['original_result_mutated'] is False

def test_monte_carlo_negative_controls():
    read=lambda i:json.loads((OUT/f'C{i:02}.json').read_text(encoding='utf-8'))['E']['result']
    assert read(19)['mean_paired_delta']==0
    assert read(20)['mean_paired_delta']==0
    assert read(28)['mean_paired_delta']<0
    assert read(29)['mean_paired_delta']<0
    assert abs(read(30)['bonferroni_FWER']-.05)<.03
