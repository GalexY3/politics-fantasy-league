import datetime,hashlib,json,pathlib,re,ssl,urllib.parse,urllib.request
root=pathlib.Path(__file__).resolve().parent
ids=[705383,702844,730605,705384,718406,746363,700824]
sources={};out=[]
for i in ids:
 obj=json.loads((root/'raw_local_only'/f'{i}.bin').read_bytes());a=obj['data']['attributes'];d=a['debate'];url=d['transcript_url'];parts=urllib.parse.urlsplit(url)
 rec={'id':i,'transcript_url':url,'debated_on':d['debated_on'],'scheduled_debate_date':a['scheduled_debate_date'],'dates_match':d['debated_on']==a['scheduled_debate_date'],'url_date_match':d['debated_on'] in parts.path}
 if parts.hostname!='hansard.parliament.uk':rec['error']='unexpected transcript host';out.append(rec);continue
 canonical=urllib.parse.urlunsplit((parts.scheme,parts.netloc,parts.path,parts.query,''))
 if canonical not in sources:
  source={'url':canonical,'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  try:
   with urllib.request.urlopen(urllib.request.Request(canonical,headers={'User-Agent':'PoliticsFantasy source verification research/1.0'}),context=ssl.create_default_context(),timeout=20) as r:
    data=r.read(5_000_001)
    if len(data)>5_000_000:raise ValueError('response >5MB')
    source.update({'status':r.status,'url_final':r.url,'size':len(data),'sha256':hashlib.sha256(data).hexdigest(),'content_type':r.headers.get('Content-Type'),'last_modified':r.headers.get('Last-Modified'),'etag':r.headers.get('ETag')})
    sources[canonical]=(source,data)
  except Exception as e:
   source.update({'status':getattr(e,'code',None),'error_type':type(e).__name__,'error':str(e)});sources[canonical]=(source,None)
  source['end_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 source,data=sources[canonical];rec['capture']=source
 if data is not None:
  text=data.decode('utf8',errors='replace'); rec['id_found_in_html']=str(i) in text
  rec['petition_and_id_nearby']=bool(re.search(r'(petition.{0,200}'+str(i)+r'|'+str(i)+r'.{0,200}petition)',text,re.I|re.S))
 out.append(rec)
result={'scope':'Seven transcript links in the official petition JSON; HTTP date and ID checks, not proof of policy change or full debate content','rows':out,'distinct_transcripts':len(sources),'limits':['No transcript body retained, only hash and metadata','Date in URL plus petition JSON is not an independent publication timestamp','No complete textual audit or independent institution: both services are UK Parliament','No first_public_at inferred']}
(root/'T022_HANSARD.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps([{'id':r['id'],'status':r.get('capture',{}).get('status'),'dates_match':r['dates_match'],'id_found':r.get('id_found_in_html'),'petition_nearby':r.get('petition_and_id_nearby')} for r in out],indent=2))
