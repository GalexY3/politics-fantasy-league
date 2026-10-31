"""R7 catalogue evidence is documentary only; no GET, permission or case admission."""
import json
from pathlib import Path
import pytest

from politics_fantasy.procedural_discovery_r7 import (
    PINNED_SHA, MANIFEST, SAFE_BY, status
)
from politics_fantasy.procedural_population_readiness import report


def test_manifest_is_pinned_and_documentary_without_raw_case():
    import hashlib
    assert hashlib.sha256(MANIFEST.read_bytes()).hexdigest() == PINNED_SHA
    s=status()
    assert s['status']=='DOCUMENTARY_CANDIDATES_BLOCKED_FROM_SOURCE_ADMISSION'
    assert s['documentary_sources_count']==4
    assert s['new_case_records_admitted'] is None
    assert s['all_registered_congress_denominator'] is None
    assert s['direct_bulk_download_authorized_by_this_inventory'] is False
    assert s['first_public_at'] is None and s['ABH_cycles']==0
    assert s['local_audit_safe_by']==SAFE_BY.isoformat()
    by_id={r['source_id']:r for r in s['candidate_sources']}
    assert set(by_id)=={
        'ASAMBLEA_MADRID_OPENDATA','CEPC_INICPAR',
        'SENADO_BIBLIOTECA_APCA','PARLAMENTO_NAVARRA_INICIATIVAS'}
    assert by_id['ASAMBLEA_MADRID_OPENDATA']['access_gate'].startswith('TERMS_ACCEPTED_BY_USE')
    assert by_id['CEPC_INICPAR']['evidence_grade']=='OFFICIAL_INDEX_DESCRIPTION_ONLY'
    assert all(r['source_population_denominator'] is None
               and not r['original_downloaded'] and not r['outcomes_or_events_admitted']
               for r in by_id.values())


def test_before_safe_day_source_names_and_legal_status_not_disclosed():
    old=status(as_of='2026-10-31T23:59:59.999999Z')
    assert old['status']=='DISCOVERY_NOT_KNOWN_AT_CUT'
    assert old['candidate_sources']==[]
    assert old['documentary_sources_count'] is None
    assert old['manifest_sha256'] is None
    assert 'ASAMBLEA_MADRID' not in json.dumps(old)
    present=status(as_of='2026-11-01T00:00:00Z')
    assert present['documentary_sources_count']==4
    current=report(as_of='2026-10-31T06:02:49Z')
    assert current['institutional_sources'][0]['observed_metadata_rows']==1754
    assert current['documentary_candidate_sources']==[]
    assert current['documentary_candidate_sources_count'] is None
    later=report(as_of='2026-11-01T00:00:00Z')
    assert len(later['documentary_candidate_sources'])==4
    assert later['risk_set_denominator'] is None
    assert later['source_groups']==3


def test_quarantine_if_bytes_or_rights_are_changed(tmp_path:Path):
    p=tmp_path/'m.json'
    p.write_bytes(MANIFEST.read_bytes()+b' ')
    broken=status(path=p)
    assert broken['status']=='DISCOVERY_MANIFEST_QUARANTINED'
    assert broken['candidate_sources']==[]
    assert broken['documentary_sources_count'] is None
    assert broken['all_registered_congress_denominator'] is None
    obj=json.loads(MANIFEST.read_text(encoding='utf8'))
    obj['sources'][0]['rights_status']='CC_BY_UNCONDITIONAL'
    p.write_text(json.dumps(obj),encoding='utf8')
    assert status(path=p)['status']=='DISCOVERY_MANIFEST_QUARANTINED'
    obj['sources'][0]['rights_status']='TERMS_ACCEPTED_BY_USE_NOT_AUTHORIZED_FOR_AUTOMATED_ORIGINAL_GET'
    obj['sources'][0]['eligible_scientific_source']=True
    p.write_text(json.dumps(obj),encoding='utf8')
    assert status(path=p)['status']=='DISCOVERY_MANIFEST_QUARANTINED'


def test_quarantine_if_original_is_missing(tmp_path:Path):
    assert status(path=tmp_path/'missing.json')['status']=='DISCOVERY_MANIFEST_QUARANTINED'


@pytest.mark.parametrize('value',['','2026-10-31','wrong','2026-10-31T07:00:00'])
def test_asof_must_be_timezone_aware(value):
    with pytest.raises(ValueError):
        status(as_of=value)
