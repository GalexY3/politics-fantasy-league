import datetime,hashlib,json,pathlib,ssl,urllib.error,urllib.parse,urllib.request
root=pathlib.Path(__file__).resolve().parent
raw=root/'raw_local_only';raw.mkdir(exist_ok=False)
prior=pathlib.Path.home()/'AppData/Local/Temp/pfl-t020-t023-probe-20261029'
probe=json.loads((prior/'PROBE.json').read_text(encoding='utf8'))
ids=[700143,730194,727309,737105,722903,705383,702844,730605,705384,718406,746363,700824]
attrs=['state','signature_count','opened_at','response_threshold_reached_at','government_response_at','debate_threshold_reached_at','scheduled_debate_date','debate_outcome_at','closed_at','updated_at']
class OnlyUK(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  if urllib.parse.urlparse(newurl).hostname!='petition.parliament.uk':raise ValueError('Unexpected redirect host')
  return super().redirect_request(req,fp,code,msg,headers,newurl)
opener=urllib.request.build_opener(OnlyUK,urllib.request.HTTPSHandler(context=ssl.create_default_context()))
results=[]
for i in ids:
 url=f'https://petition.parliament.uk/petitions/{i}.json';rec={'id':i,'url':url,'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'first_public_at':'UNKNOWN'}
 try:
  if i==700143:
   old=probe['petition_700143'];data=(prior/'petition_700143.bin').read_bytes();rec.update({k:old.get(k) for k in ('status','url_final','size','sha256','content_type','last_modified','etag','start_utc','end_utc')});rec['reused_prior_probe']=True
  else:
   req=urllib.request.Request(url,headers={'User-Agent':'PoliticsFantasy source verification research/1.0'})
   with opener.open(req,timeout=20) as r:
    data=r.read(2_000_001)
    if len(data)>2_000_000:raise ValueError('response >2MB')
    rec.update({'status':r.status,'url_final':r.url,'size':len(data),'sha256':hashlib.sha256(data).hexdigest(),'content_type':r.headers.get('Content-Type'),'last_modified':r.headers.get('Last-Modified'),'etag':r.headers.get('ETag'),'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
  (raw/f'{i}.bin').write_bytes(data)
  if not rec.get('content_type','').startswith('application/json'):raise ValueError('Non-JSON response')
  dups=[]
  def pairs(items):
   d={}
   for k,v in items:
    if k in d:dups.append(k)
    d[k]=v
   return d
  obj=json.loads(data,object_pairs_hook=pairs); assert str(obj['data']['id'])==str(i)
  a=obj['data']['attributes']; panel={k:a.get(k) for k in attrs}; gr=a.get('government_response');panel['response_responded_on']=gr.get('responded_on') if isinstance(gr,dict) else None
  rec.update({'json_parse':'PASS','duplicate_key_count':len(dups),'aggregate':panel})
 except Exception as e:rec.update({'status':getattr(e,'code',rec.get('status')),'error_type':type(e).__name__,'error':str(e),'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 results.append(rec)
out={'scope':'12 previously selected closed top-signature petitions, not representative, no personal information','responses':results,'limitations':['Raw bodies local only and may contain creator names; never commit','No timestamps imply first_public_at','No retries, capture is non-simultaneous']}
(root/'T022_CAPTURE_MANIFEST.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print(json.dumps({'ids':len(ids),'json_pass':sum(r.get('json_parse')=='PASS' for r in results),'status_counts':{str(k):sum(r.get('status')==k for r in results) for k in {r.get('status') for r in results}}},indent=2))
