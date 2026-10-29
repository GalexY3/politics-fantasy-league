"""Capture resources directly linked by the two already obtained official source pages."""
import datetime,hashlib,json,pathlib,urllib.parse,urllib.request
R=pathlib.Path(__file__).parent; D=R/'private_raw'; D.mkdir(exist_ok=True)
items=[('dog_pdf','https://www.xunta.gal/dog/Publicados/2024/20240306/AnuncioG2453-050324-1_es.pdf'),
       ('boe_xml','https://www.boe.es/diario_boe/xml.php?id=BOE-A-2024-13092')]
items += [(f'galicia_csv_{n:03}',f'https://abertos.xunta.gal/catalogo/administracion-publica/-/dataset/0656/eleccions-parlamento-galicia-resultados-2024/{n:03}/descarga-directa-ficheiro.csv') for n in (1,3,5,7,9,11,13,15)]
records=[]
for name,url in items:
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'PFL-research-source-QA/1.0'}),timeout=30) as r:
   b=r.read(); code=r.status; final=r.geturl(); h=dict(r.headers.items())
  host=urllib.parse.urlparse(final).hostname or ''
  if not(host=='boe.es' or host.endswith('.boe.es') or host=='xunta.gal' or host.endswith('.xunta.gal')):raise ValueError('unexpected final source domain')
  file=D/(name+('.pdf' if name=='dog_pdf' else '.xml' if name=='boe_xml' else '.csv'));file.write_bytes(b)
  records.append({'name':name,'url':url,'effective_url':final,'status':code,'size':len(b),'sha256':hashlib.sha256(b).hexdigest(),
   'mime':h.get('Content-Type'),'last_modified':h.get('Last-Modified'),'started_utc':start,
   'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'local':str(file),'first_public_at':'UNKNOWN'})
  print(name,code,len(b),final)
 except Exception as ex:
  records.append({'name':name,'url':url,'started_utc':start,'error':repr(ex)});print(name,'FAIL',repr(ex))
(R/'LINKED_MANIFEST.json').write_text(json.dumps({'sources':records,'note':'TLS verification enabled; originals local only, rights not yet checked.'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
