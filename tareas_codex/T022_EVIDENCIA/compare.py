import datetime,json,pathlib,statistics
root=pathlib.Path(__file__).resolve().parent
proj=pathlib.Path.home()/'AppData/Local/Temp/pfl-t025-mechanism-qa-20261029/proyectos/politics-fantasy-league'
old=json.loads((proj/'research/ABH_PETITIONS5_20261028/PETITIONS12_EVENT_PANEL.json').read_text(encoding='utf8'))['data'];old={r['id']:r for r in old}
new=json.loads((root/'T022_CAPTURE_MANIFEST.json').read_text(encoding='utf8'))['responses'];assert len(new)==12 and all(r.get('json_parse')=='PASS' for r in new)
mapping={'signatures':'signature_count','opened_at':'opened_at','response_threshold_reached_at':'response_threshold_reached_at','government_response_at':'government_response_at','debate_threshold_reached_at':'debate_threshold_reached_at','scheduled_debate_date':'scheduled_debate_date','debate_outcome_at':'debate_outcome_at','closed_at':'closed_at','updated_at':'updated_at','response_responded_on':'response_responded_on'}
differences={k:[] for k in mapping}
for row in new:
 i=row['id'];a=old[i];b=row['aggregate']
 for x,y in mapping.items():
  if a.get(x)!=b.get(y):differences[x].append({'id':i,'prior':a.get(x),'captured':b.get(y)})
def parse(x):return datetime.datetime.fromisoformat(x.replace('Z','+00:00'))
waits=[];public_waits=[];dates=[]
for row in new:
 a=row['aggregate']; threshold=parse(a['response_threshold_reached_at']); response=parse(a['government_response_at']); day=a['response_responded_on']; public=datetime.datetime.fromisoformat(day).replace(tzinfo=datetime.timezone.utc)
 waits.append((response-threshold).total_seconds()/86400);public_waits.append((public-threshold).total_seconds()/86400)
 if response.date().isoformat()!=day:dates.append({'id':row['id'],'timestamp_date':response.date().isoformat(),'publication_date':day})
out={'sample':'12 previously top-closed by signatures, deliberately outcome-selected; not representative','original_jsons_captured':len(new),'field_discrepancy_counts':{k:len(v) for k,v in differences.items()},'differences':{k:v for k,v in differences.items() if v},'response_date_disagreements':dates,'median_response_threshold_to_technical_timestamp_days':statistics.median(waits),'median_response_threshold_to_published_date_midnight_utc_days':statistics.median(public_waits),'limits':['No verified first public timestamp; published date treated as UTC midnight only for comparability','No causal inference or representativeness','Differences are two snapshots, not evidence of cause','Raw originals may contain creator names and are local only','T023 covers a separate 180-ID cohort; one overlap does not replace all 12 originals']}
(root/'T022_COMPARISON.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k not in ['differences','limits']},indent=2))
