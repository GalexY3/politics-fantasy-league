from pathlib import Path
import sys, json
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from inspect_official_json import profile_json


def test_profiler_reports_structure_without_values(tmp_path):
    path=tmp_path/'one.json'
    path.write_text(json.dumps({'nominalList':[{'firstName':'TEST_NAME_PRIVATE', 'decision':'yes'}], 'session':193}),encoding='utf-8')
    obj=profile_json(path)
    text=json.dumps(obj)
    assert 'TEST_NAME_PRIVATE' not in text
    assert 'nominalList' in text
    assert obj['root_type']=='dict'


def test_profiler_handles_bad_json(tmp_path):
    path=tmp_path/'bad.json';path.write_text('{bad}',encoding='utf-8')
    with pytest.raises(json.JSONDecodeError):profile_json(path)
