import concurrent.futures, datetime, hashlib, json, pathlib, ssl, threading, urllib.error, urllib.parse, urllib.request
root=pathlib.Path(__file__).resolve().parent
raw=root/'t023_raw_local_only'; raw.mkdir(exist_ok=False)
probe=json.loads((root/'PROBE.json').read_text(encoding='utf-8'))
names=['state','signature_count','created_at','opened_at','closed_at','rejected_at','updated_at','response_threshold_reached_at','government_response_at','debate_threshold_reached_at','scheduled_debate_date','debate_scheduled_on','debate_outcome_at']
class Restrict(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  if urllib.parse.urlparse(newurl).hostname!='petition.parliament.uk': raise ValueError('Unexpected redirect host')
  return super().redirect_request(req,fp,code,msg,headers,newurl)
opener=urllib.request.build_opener(Restrict,urllib.request.HTTPSHandler(context=ssl.create_default_context()))
def parse(data):
 duplicates=[]
 def pairs(items):
  d={}
  for k,v in items:
   if k in d: duplicates.append(k)
   d[k]=v
  return d
 obj=json.loads(data,object_pairs_hook=pairs)
 attrs=obj['data']['attributes'];panel={k:attrs.get(k) for k in names}
 gr=attrs.get('government_response');panel['government_response_responded_on']=gr.get('responded_on') if isinstance(gr,dict) else None
 return str(obj['data']['id']),panel,duplicates
def one(i):
 key='petition_'+str(i);url=f'https://petition.parliament.uk/petitions/{i}.json'
 rec={'id':i,'url':url,'first_public_at':'UNKNOWN'}; start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  if key in probe and probe[key].get('status')==200:
   old=probe[key];data=(root/(key+'.bin')).read_bytes()
   rec.update({k:old.get(k) for k in ('status','url_final','size','sha256','content_type','last_modified','etag','start_utc','end_utc')});rec['reused_probe']=True
  else:
   req=urllib.request.Request(url,headers={'User-Agent':'PoliticsFantasy source verification research/1.0'})
   with opener.open(req,timeout=20) as r:
    data=r.read(2_000_001)
    if len(data)>2_000_000: raise ValueError('response >2MB')
    rec.update({'status':r.status,'url_final':r.url,'size':len(data),'sha256':hashlib.sha256(data).hexdigest(),'content_type':r.headers.get('Content-Type'),'last_modified':r.headers.get('Last-Modified'),'etag':r.headers.get('ETag'),'start_utc':start,'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
  parsed_id,panel,dups=parse(data)
  if parsed_id!=str(i): raise ValueError('unexpected id')
  (raw/(str(i)+'.json')).write_bytes(data)
  rec.update({'json_parse':'PASS','duplicate_key_count':len(dups),'id_matches':True,'aggregate':panel})
 except Exception as e:
  rec.update({'status':getattr(e,'code',rec.get('status')),'error_type':type(e).__name__,'error':str(e),'start_utc':start,'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 results=sorted(pool.map(one,range(700120,700300)),key=lambda x:x['id'])
report={'preselected_ids':{'start':700120,'end':700299,'count':180},'capture_conditions':'fixed ID cohort; 4 concurrent HTTP requests; no retries; TLS verified; no first-publication time inferred; 404 is not proof of nonexistence','originals':'t023_raw_local_only (must not be committed)','responses':results}
(root/'T023_COHORT_MANIFEST.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
counts={}
for r in results: counts[str(r.get('status'))]=counts.get(str(r.get('status')),0)+1
print(json.dumps({'statuses':counts,'parsed':sum(r.get('json_parse')=='PASS' for r in results),'duplicate_keys':sum(r.get('duplicate_key_count',0) for r in results),'total':len(results)},indent=2))
