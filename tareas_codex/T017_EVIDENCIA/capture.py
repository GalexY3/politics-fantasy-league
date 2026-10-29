"""Download T017 originals for local-only provenance; no individual rows exported."""
import datetime,hashlib,json,pathlib,urllib.parse,urllib.request
R=pathlib.Path(__file__).parent;D=R/'private_raw';D.mkdir(exist_ok=True)
items=[('navarra_csv','https://datosabiertos.navarra.es/dataset/fa95fdf0-4aa1-4194-84b3-2779c9bc8e5e/resource/f555f0ff-a6f1-420b-bd25-caf979f26d86/download/escrutinio_parlamento_2023.csv'),
 ('navarra_parliament','https://parlamentodenavarra.es/en/node/167978'),
 ('asturias_pdf','https://www.jgpa.es/documents/11156/18491/Resultados%2Belectorales%2B2023%2B%28XII%2BLegislatura%29/79394093-f262-4829-845a-faf8cc85fe30'),
 ('rioja_pdf','https://www.juntaelectoralcentral.es/cs/jec/documentos/Escrutinio%20General.pdf')]
records=[]
for name,url in items:
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'PFL-research-source-QA/1.0'}),timeout=30) as r:
   b=r.read();code=r.status;final=r.geturl(); h=dict(r.headers.items())
  suffix='.csv' if name.endswith('_csv') else '.pdf' if name.endswith('_pdf') else '.html'
  if suffix=='.pdf' and not b.startswith(b'%PDF-'):raise ValueError('response is not PDF')
  if urllib.parse.urlparse(url).hostname != urllib.parse.urlparse(final).hostname:raise ValueError('unexpected redirect host '+final)
  dest=D/(name+suffix);dest.write_bytes(b)
  records.append({'name':name,'url_requested':url,'url_effective':final,'status':code,'size_bytes':len(b),
   'sha256':hashlib.sha256(b).hexdigest(),'content_type':h.get('Content-Type'),'last_modified':h.get('Last-Modified'),
   'started_utc':start,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'tls':'verified system trust','first_public_at':'UNKNOWN','local_original':str(dest)})
  print(name,code,len(b),h.get('Content-Type'))
 except Exception as ex:
  records.append({'name':name,'url_requested':url,'started_utc':start,'error':repr(ex)});print(name,'FAIL',repr(ex))
(R/'MANIFEST.json').write_text(json.dumps({'sources':records,'note':'Originals local only; rights and first-publication require verification'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
