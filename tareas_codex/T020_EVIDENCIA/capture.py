import datetime, hashlib, json, pathlib, urllib.request, urllib.error
from urllib.parse import urlparse

base='https://results.elections.europa.eu/'
urls={
 'turnout.csv':base+'data-sheets/csv/turnout/turnout-country.csv',
 'turnout.sig':base+'data-sheets/csv/turnout/turnout-country.sig',
 'gender_2024.csv':base+'data-sheets/csv/2024-2029/election-results/gender-balance/gender-balance-country.csv',
 'gender_2024.sig':base+'data-sheets/csv/2024-2029/election-results/gender-balance/gender-balance-country.sig',
 'gender_2019.csv':base+'data-sheets/csv/2019-2024/election-results/gender-balance/gender-balance-country.csv',
 'gender_2019.sig':base+'data-sheets/csv/2019-2024/election-results/gender-balance/gender-balance-country.sig',
 'certificate.crt':base+'assets/certificate.crt',
 'certchain.crt':'https://elections.europa.eu/ee24/certchain.crt',
}
class Redirects(urllib.request.HTTPRedirectHandler):
 def redirect_request(self, req, fp, code, msg, headers, newurl):
  p=urlparse(newurl)
  if p.scheme!='https' or not p.hostname.endswith('.europa.eu'): raise RuntimeError('Refused redirect')
  return super().redirect_request(req,fp,code,msg,headers,newurl)
out=pathlib.Path(__file__).parent
opener=urllib.request.build_opener(Redirects())
records=[]
for name,url in urls.items():
 record={'name':name,'url':url,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with opener.open(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as response:
   data=response.read(); (out/name).write_bytes(data)
   record.update(status=response.status,effective_url=response.url,content_type=response.headers.get('Content-Type'),etag=response.headers.get('ETag'),last_modified=response.headers.get('Last-Modified'),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),tls_verified=True)
 except Exception as e: record['error']=str(e)
 record['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat(); records.append(record)
(out/'MANIFEST.json').write_text(json.dumps({'portal':'https://results.elections.europa.eu/en/tools/download-datasheets/','note':'Turnout-country contains multiple years; signatures unverified until separate crypto tests.','records':records},indent=2)+'\n')
print(json.dumps([{'name':r['name'],'status':r.get('status'),'bytes':r.get('bytes'),'error':r.get('error')} for r in records]))
