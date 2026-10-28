"""Verifies bibliographic URLs only, not direct original bytes or first-publication time."""
from urllib.parse import urlsplit, unquote
from politics_fantasy.source_event_registry import public_stage_catalog, evaluate_server_claim

def test_published_boccl_doc_links_are_cve_specific():
    docs={x['cve']:x for x in public_stage_catalog()['records'] if x.get('cve')}
    assert set(docs)=={'BOCCL-12-000986','BOCCL-12-001042'}
    for cve, record in docs.items():
        url=record['source_url']
        parsed=urlsplit(url)
        assert parsed.scheme=='https' and parsed.hostname=='www.ccyl.es'
        assert parsed.username is None and parsed.password is None
        assert parsed.port in (None,443)
        assert cve+'.xml' in unquote(url)
        assert '\\12L\\' in unquote(url)
        assert record['legislature']==12

def test_documents_are_distinct_stage_types_not_status_certificates():
    records={r['cve']:r for r in public_stage_catalog()['records'] if r.get('cve')}
    a=records['BOCCL-12-000986']; b=records['BOCCL-12-001042']
    assert a['record_family']=='BOCCL_CANDIDATE_ACCEPTANCE'
    assert b['record_family']=='BOCCL_PLENARY_DESIGNATION'
    assert (a['act_day'],a['bulletin_day'])==('2026-09-03','2026-09-10')
    assert (b['act_day'],b['bulletin_day'])==('2026-09-10','2026-09-16')

def test_document_url_is_not_timestamp_attestation():
    status=public_stage_catalog()
    assert status['original_publication_timestamps_verified']==0
    assert not status['full_senator_status_certified']
    assert not status['release_ready'] and not status['real_person_scoring']
    assert all(x['first_public_at'] is None for x in status['records'])

def test_cve_lookup_still_quarantined():
    for cve,claim in [('BOCCL-12-000986','NOMINATED_AND_ACCEPTED_CANDIDATES'),('BOCCL-12-001042','DESIGNATED_SENATORS')]:
        value=evaluate_server_claim(evidence_ref='CCYL:'+cve,desired_claim=claim,as_of='2026-12-01T00:00:00Z')
        assert value['reason']=='FIRST_PUBLIC_AT_UNVERIFIED'
        assert not value['eligible'] and not value['release_grade']
