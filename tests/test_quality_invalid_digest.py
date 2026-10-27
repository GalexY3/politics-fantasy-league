import json
from copy import deepcopy
from politics_fantasy.quality import audit_jsonl
D={'event_id':'synthetic-1','source_id':'test','event_kind':'speech_recorded','occurred_at':'2026-01-02T10:00:00+00:00', 'first_public_at':'2026-01-03T10:00:00+00:00','source_url':'https://example.invalid', 'raw_sha256':'a'*64, 'person_ids':['synthetic-ID']}

def test_good_and_empty_attribution(tmp_path):
 p=tmp_path/'data.jsonl';q=deepcopy(D);q['person_ids']=[];p.write_text(json.dumps(q)+'\n')
 assert audit_jsonl(p)['counts']['parseable']==1

def test_malformed_digest_and_person_ids_not_parseable(tmp_path):
 rows=[]
 for k,v in [('raw_sha256','z'*64),('person_ids',[123]),('person_ids',['x','x'])]:
  x=deepcopy(D);x[k]=v;rows.append(x)
 p=tmp_path/'data.jsonl';p.write_text('\n'.join(json.dumps(x) for x in rows)+'\n')
 result=audit_jsonl(p)['counts']
 assert result.get('parseable',0)==0
 assert result['bad_identity_or_hash']==3
