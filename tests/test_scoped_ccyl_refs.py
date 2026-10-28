from politics_fantasy.source_event_registry import evaluate_server_claim, public_stage_catalog

def check(ref, claim):
    return evaluate_server_claim(evidence_ref=ref,desired_claim=claim,as_of='2026-09-30T12:00:00+02:00')

def test_unqualified_2022_2026_ref_is_rejected():
    for ref in ('ESE/000002-01','ESE/000002-02'):
        r=check(ref,'NOMINATED_AND_ACCEPTED_CANDIDATES')
        assert r['reason']=='AMBIGUOUS_UNQUALIFIED_ESE_REF'
        assert r['eligible'] is False and r['release_grade'] is False

def test_qualified_cve_record_still_requires_first_publication():
    assert check('CCYL:BOCCL-12-000986','NOMINATED_AND_ACCEPTED_CANDIDATES')['reason']=='FIRST_PUBLIC_AT_UNVERIFIED'
    assert check('CCYL:BOCCL-12-001042','DESIGNATED_SENATORS')['reason']=='FIRST_PUBLIC_AT_UNVERIFIED'

def test_cross_assertion_does_not_certify():
    r=check('CCYL:BOCCL-12-000986','DESIGNATED_SENATORS')
    assert r['reason']=='ASSERTION_TYPE_MISMATCH'

def test_records_explicitly_cve_scoped_and_no_original_dates():
    rows=public_stage_catalog()['records']
    assert len(rows)==3
    assert rows[0]['legislature']==12 and rows[1]['legislature']==12
    assert rows[0]['cve']=='BOCCL-12-000986' and rows[1]['cve']=='BOCCL-12-001042'
    assert all(r['first_public_at'] is None for r in rows)
    assert all('/' not in r['evidence_ref'] for r in rows[:2])
