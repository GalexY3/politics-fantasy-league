import json
import sys
from pathlib import Path
from hashlib import sha256
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from politics_fantasy.quality import audit_jsonl


def test_audit_duplicate_and_absent_attribution(tmp_path):
    d={'event_id':'x', 'source_id':'congreso', 'event_kind':'speech_recorded',
       'occurred_at':'2026-01-02T11:00:00+01:00',
       'first_public_at':'2026-01-03T11:00:00+01:00',
       'source_url':'https://www.congreso.es/fake',
       'raw_sha256':sha256(b'example').hexdigest(),
       'person_ids':[]}
    p=tmp_path/'events.jsonl'
    p.write_text('\n'.join([json.dumps(d),json.dumps(d),'INVALID_JSON','{}']))
    r=audit_jsonl(p)
    assert r['counts']['rows']==4
    assert r['counts']['duplicate_same_revision']==1
    assert r['counts']['unattributed_events']==2
    assert r['counts']['bad_json_or_type']==1
    assert r['counts']['missing_required']==1
    assert r['coverage_status']=='NOT_INFERABLE_WITHOUT_SOURCE_CENSUS'
