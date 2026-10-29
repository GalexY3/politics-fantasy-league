import collections,hashlib,json,pathlib
root=pathlib.Path(__file__).resolve().parent
archive=pathlib.Path.home()/'AppData/Local/Temp/pfl-t025-mechanism-qa-20261029/proyectos/politics-fantasy-league/research/ABH_PETITIONCOHORT5_20261028'
m=json.loads((root/'T023_COHORT_MANIFEST.json').read_text(encoding='utf8'))
rows=json.loads((archive/'ARCHIVE_COHORT40_PANEL.json').read_text(encoding='utf8'))['rows']
for i in range(1,5):rows += json.loads((archive/f'ARCHIVE_140_PART{i}.json').read_text(encoding='utf8'))['out']
assert len(rows)==66 and len({x['id'] for x in rows})==66
rs={r['id']:r for r in m['responses']}; parsed={i for i,r in rs.items() if r.get('json_parse')=='PASS'}
ar={r['id']:r for r in rows}; assert len(rs)==180
fields={'state':'state','signatures':'signature_count','created_at':'created_at','opened_at':'opened_at','closed_at':'closed_at','updated_at':'updated_at','response_threshold_reached_at':'response_threshold_reached_at','government_response_at':'government_response_at','debate_threshold_reached_at':'debate_threshold_reached_at','scheduled_debate_date':'scheduled_debate_date','debate_outcome_at':'debate_outcome_at','rejected_at':'rejected_at'}
diff={k:[] for k in [*fields,'government_response_responded_on']}; hashes={'matches':[],'differs':[]}; no_public_payload=[]
for i in sorted(parsed & ar.keys()):
 a=ar[i];b=rs[i]['aggregate']
 for x,y in fields.items():
  if a.get(x)!=b.get(y):diff[x].append({'id':i,'archive':a.get(x),'official':b.get(y)})
 old_response=a.get('government_response_responded_on',a.get('response_responded_on'))
 if old_response!=b.get('government_response_responded_on'): diff['government_response_responded_on'].append({'id':i,'archive':old_response,'official':b.get('government_response_responded_on')})
 payload=(root/'t023_raw_local_only'/f'{i}.json').read_bytes()
 sha=hashlib.sha1(f'blob {len(payload)}\0'.encode()+payload).hexdigest()
 hashes['matches' if sha==a['source_blob'] else 'differs'].append(i)
timing={}
for i in [700189,700262,700143]:
 b=rs[i].get('aggregate',{})
 timing[str(i)]={k:b.get(k) for k in ['state','signature_count','government_response_at','government_response_responded_on','updated_at']}
summary={'scope':'T023 180 IDs fixed before source access; metadata/aggregate only, raw data excluded from Git', 'response_classification':{'valid_json':len(parsed),'html_redirected_gathering_support':sum(r.get('status')==200 and '/gathering-support' in r.get('url_final','') for r in rs.values()),'http_404':sum(r.get('status')==404 for r in rs.values())},'archive_rows':len(ar),'overlap_archived_and_official':len(parsed & ar.keys()),'official_only_json_ids':sorted(parsed-ar.keys()),'archive_missing_from_official_json_ids':sorted(ar.keys()-parsed),'git_blob_match_count':len(hashes['matches']),'git_blob_differ_count':len(hashes['differs']),'field_discrepancy_counts':{k:len(v) for k,v in diff.items()},'field_discrepancies':{k:v for k,v in diff.items() if v},'audit_ids':timing,'limits':['HTTP 404 is not proof of nonexistence','HTTP 200 HTML redirect is not a JSON or definitive state','88 redirected HTML bodies were not retained due to capture script ordering; their metadata and SHA remain recorded','current source capture does not establish first publication time','original archived source uses Git blob hashes; mismatch does not prove cause or chronology','response timestamps and public response dates are different fields','no person, creator, action text, party or individual signature in this report']}
(root/'T023_RECONCILIATION.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in summary.items() if k not in ('field_discrepancies','limits')},indent=2))
