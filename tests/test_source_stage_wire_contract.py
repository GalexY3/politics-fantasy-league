"""Synthetic read-only JSON response boundary; NOT a live HTTP handler test."""
import json
import pytest
from politics_fantasy.source_event_registry import public_stage_catalog,evaluate_server_claim

@pytest.fixture
def wire():
    return json.loads(json.dumps(public_stage_catalog(),ensure_ascii=False))

def test_wire_contains_three_distinct_sources(wire):
    assert len(wire['records'])==3
    ids=[r['evidence_ref'] for r in wire['records']]
    assert len(set(ids))==3

def test_wire_identifies_official_cves(wire):
    m={r['evidence_ref']:r for r in wire['records']}
    assert m['CCYL:BOCCL-12-000986']['cve']=='BOCCL-12-000986'
    assert m['CCYL:BOCCL-12-001042']['cve']=='BOCCL-12-001042'
    assert all(m[k]['legislature']==12 for k in m if k.startswith('CCYL:'))

def test_short_ref_is_data_not_authority(wire):
    assert 'ESE/000002-01' not in {r['evidence_ref'] for r in wire['records']}
    for alias in ['ESE/000002-01','ESE/000002-02']:
        res=evaluate_server_claim(evidence_ref=alias,desired_claim='DESIGNATED_SENATORS',as_of='2026-09-30T12:00:00+02:00')
        assert res=={'eligible':False,'release_grade':False,'reason':'AMBIGUOUS_UNQUALIFIED_ESE_REF'}

def test_no_attested_timestamp(wire):
    assert wire['original_publication_timestamps_verified']==0
    assert all(r['first_public_at'] is None for r in wire['records'])

def test_no_scoring_flags(wire):
    assert not wire['real_person_scoring'] and not wire['release_ready']

def test_serialized_response_mutation_cannot_authorize(wire):
    for row in wire['records']: row['first_public_at']='1990-01-01T00:00:00Z'
    real=public_stage_catalog()
    assert all(x['first_public_at'] is None for x in real['records'])

def test_current_cve_does_not_clear_full_status(wire):
    for r in wire['records']:
        result=evaluate_server_claim(evidence_ref=r['evidence_ref'],desired_claim='FULL_SENATOR_STATUS',as_of='2030-01-01T00:00:00Z')
        assert not result['eligible'] and not result['release_grade']
