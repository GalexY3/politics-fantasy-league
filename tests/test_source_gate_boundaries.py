"""Negative controls for candidate origins and malformed claim types."""
import pytest

from politics_fantasy.source_eligibility import assess_evidence
from politics_fantasy.provenance_claim_gate import AUTHORITY, evaluate_claim_as_of
from politics_fantasy.source_event_registry import evaluate_server_claim


@pytest.mark.parametrize('url', [
    'https://www.senado.es/legis15/votaciones/ses_60.xml',
    'https://descargas.interior.gob.es/datasets/resultados_electorales/Elecciones-Congreso.xlsx',
])
def test_catalogued_official_host_remains_quarantined(url):
    result = assess_evidence({'scope':'AGGREGATE', 'official_url':url})
    assert 'UNVERIFIED_SOURCE_URL' not in result['reasons']
    assert result['status'] == 'QUARANTINED'
    assert not result['real_person_scoring'] and not result['release_ready']


@pytest.mark.parametrize('url', [
    'http://www.senado.es/file.xml',
    'https://www.senado.es.evil.example/file.xml',
    'https://www.senado.es@evil.example/file.xml',
    'https://user@www.senado.es/file.xml',
    'https://www.senado.es:444/file.xml',
    'https://descargas.interior.gob.es.evil.example/file.xlsx',
])
def test_spoofed_or_insecure_url_is_rejected(url):
    assert 'UNVERIFIED_SOURCE_URL' in assess_evidence({'scope':'AGGREGATE','official_url':url})['reasons']


@pytest.mark.parametrize('value', [[], {}, None])
def test_nonstring_claim_and_family_fail_closed(value):
    base={'authority':AUTHORITY,'record_family':'BOCCL_CANDIDATE_ACCEPTANCE',
          'evidence_ref':'ESE/000002-01','desired_claim':'NOMINATED_AND_ACCEPTED_CANDIDATES',
          'as_of':'2026-09-30T12:00:00+02:00','trusted_registry':{}}
    result=evaluate_claim_as_of(**{**base,'desired_claim':value})
    assert result['reason']=='UNSUPPORTED_CLAIM' and not result['eligible']
    result=evaluate_claim_as_of(**{**base,'record_family':value})
    assert result['reason']=='UNSUPPORTED_RECORD_FAMILY' and not result['eligible']
    result=evaluate_server_claim(evidence_ref='ESE/000002-01',desired_claim=value,as_of=base['as_of'])
    assert result['reason']=='UNSUPPORTED_CLAIM' and not result['eligible']
