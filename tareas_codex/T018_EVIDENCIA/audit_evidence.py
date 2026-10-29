import hashlib,json,pathlib
root=pathlib.Path(__file__).parent
data=json.loads((root/'AGGREGATES.json').read_text())
allowed={'commons':{'id','number','date','title','aye','no','publication_updated','deferred'},
         'lords':{'id','number','date','title','content','not_content','teller_content_count','teller_not_content_count','member_content_count','member_not_content_count','first_public_at'},
         'comparisons':{'chamber','number','id','one_match','counts_match'}}
for kind,keys in allowed.items():
 for row in data[kind]:
  assert set(row)<=keys and all(v is None or isinstance(v,(str,int,float,bool)) for v in row.values())
assert len(data['commons'])==10 and len(data['lords'])==3
assert all(r['one_match'] and r['counts_match'] for r in data['comparisons'])
manifest=json.loads((root/'MANIFEST.json').read_text())
assert len(manifest['records'])==16 and all(r.get('status')==200 and r.get('tls_verified') for r in manifest['records'])
files=['MANIFEST.json','AGGREGATES.json','capture.py','NODE.stdout','NODE.stderr','NODE_META.json','test_ontology.py','audit_evidence.py']
result={'scope':'AGGREGATE_FIELDS_ONLY_NO_MEMBER_ROWS','checks':{'whitelist_scalar_fields':True,'commons_count':10,'lords_count':3,'comparisons_pass':12,'requests_pass':16},
 'sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in files}}
(root/'EVIDENCE_INDEX.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['checks']))
