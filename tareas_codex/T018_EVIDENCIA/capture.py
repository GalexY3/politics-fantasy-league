import datetime,hashlib,json,pathlib,urllib.request
from urllib.parse import urlparse
root=pathlib.Path(__file__).parent; raw=root/'raw';raw.mkdir(exist_ok=True)
project=pathlib.Path(r'C:\Github\Politics-Fantasy-Codex\proyectos\politics-fantasy-league\research\ABH_DIVISIONS5_20261028')
class Redirects(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  p=urlparse(newurl)
  if p.scheme!='https' or not p.hostname.endswith('.parliament.uk'):raise RuntimeError('unsafe redirect')
  return super().redirect_request(req,fp,code,msg,headers,newurl)
opener=urllib.request.build_opener(Redirects()); records=[]
def capture(name,url):
 rec={'name':name,'url':url,'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'first_public_at':None}
 try:
  with opener.open(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as res:
   data=res.read();(raw/name).write_bytes(data); obj=json.loads(data)
   rec.update(status=res.status,effective_url=res.url,content_type=res.headers.get('Content-Type'),etag=res.headers.get('ETag'),last_modified=res.headers.get('Last-Modified'),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),tls_verified=True)
 except Exception as ex: rec['error']=str(ex);obj=None
 rec['end_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();records.append(rec);return obj
base='https://commonsvotes-api.parliament.uk/'
searched={}
for date in ['2026-10-20','2026-10-21','2026-07-15']:
 searched[date]=capture('commons_search_'+date+'.json',base+'data/divisions.json/search?startDate='+date+'&endDate='+date+'&take=100')
commons=[]
for date,seq in searched.items():
 for entry in seq or []:
  if (date=='2026-10-20' and entry['Number'] in range(96,101)) or (date=='2026-10-21' and entry['Number'] in [101,102,103,104]) or (date=='2026-07-15' and entry['DivisionId']==2411):
   d=capture('commons_'+str(entry['DivisionId'])+'.json',base+'data/division/'+str(entry['DivisionId'])+'.json')
   if d:commons.append({'id':d['DivisionId'],'number':d['Number'],'date':d['Date'],'title':d['Title'],'aye':d['AyeCount'],'no':d['NoCount'],'publication_updated':d['PublicationUpdated'],'deferred':d['IsDeferred']})
lords=[]
for id in [3729,3730,3731]:
 d=capture('lords_'+str(id)+'.json','https://lordsvotes-api.parliament.uk/data/Divisions/'+str(id))
 if d:lords.append({'id':d['divisionId'],'number':d['number'],'date':d['date'],'title':d['title'],'content':d['authoritativeContentCount'],'not_content':d['authoritativeNotContentCount'],'teller_content_count':d['tellerContentCount'],'teller_not_content_count':d['tellerNotContentCount'],'member_content_count':d['memberContentCount'],'member_not_content_count':d['memberNotContentCount'],'first_public_at':None})
f2=json.loads((project/'C02_UK_DISTINCT_DIVISIONS_COLLISION.json').read_text());f3=json.loads((project/'C03_UK_BILL_STAGES_20261020.json').read_text());f4=json.loads((project/'C04_UK_LORDS_SAME_BILL_AGGREGATES.json').read_text())
checks=[]
for date,fixture,ak,nk in [('2026-10-21',f2['records'],'aye','no'),('2026-10-20',f3['votes'],'ayes','noes')]:
 for row in fixture:
  matches=[d for d in commons if d['date'].startswith(date) and d['number']==row['division_number']]
  checks.append({'chamber':'Commons','number':row['division_number'],'one_match':len(matches)==1,'counts_match':len(matches)==1 and matches[0]['aye']==row[ak] and matches[0]['no']==row[nk]})
for row in f4['records']:
 matches=[d for d in lords if d['id']==row['id']]
 checks.append({'chamber':'Lords','id':row['id'],'one_match':len(matches)==1,'counts_match':len(matches)==1 and matches[0]['content']==row['content'] and matches[0]['not_content']==row['not_content']})
out={'commons':commons,'lords':lords,'comparisons':checks,'warning':'Counts are separate events, not unique voters or physical attendance; original JSON includes people and remains outside Git. first_public_at unknown.'}
(root/'MANIFEST.json').write_text(json.dumps({'scope':'T018_PARTIAL_CAPTURE','records':records},indent=2)+'\n')
(root/'AGGREGATES.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'captures_ok':sum(r.get('status')==200 for r in records),'captures_total':len(records),'commons':len(commons),'lords':len(lords),'comparisons_ok':sum(c['one_match'] and c['counts_match'] for c in checks),'comparisons_total':len(checks),'errors':[r['error'] for r in records if 'error' in r]}))
