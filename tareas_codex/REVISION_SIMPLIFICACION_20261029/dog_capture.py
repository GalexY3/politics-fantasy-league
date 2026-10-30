import datetime, hashlib, json, pathlib, re, subprocess, urllib.request
from html.parser import HTMLParser

root = pathlib.Path(__file__).resolve().parent
urls = {
    'rectification.html': 'https://www.xunta.gal/dog/Publicados/2024/20240308/AnuncioG2453-070324-1_es.html',
    'rectification.pdf': 'https://www.xunta.gal/dog/Publicados/2024/20240308/AnuncioG2453-070324-1_es.pdf',
}
class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]
    def handle_data(self,s): self.parts.append(s)
records=[]
for name,url in urls.items():
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'PFL-Research/1.0 (public institutional documents)'}), timeout=30) as r:
        data=r.read(); status=r.status; final=r.url; headers=dict(r.headers.items())
    (root/name).write_bytes(data)
    records.append({'name':name,'requested_url':url,'effective_url':final,'status':status,'started_utc':start,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tls':'system trust verified','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'content_type':headers.get('Content-Type'),'last_modified':headers.get('Last-Modified'),'etag':headers.get('ETag')})
    if status != 200: raise RuntimeError('not HTTP 200')
assert (root/'rectification.pdf').read_bytes().startswith(b'%PDF-')
parser=Text();parser.feed((root/'rectification.html').read_text(encoding='utf-8'))
html=' '.join(parser.parts);html=' '.join(html.split())
pdftotext=r'C:\Users\Nitropc\AppData\Local\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin\pdftotext.exe'
extract=subprocess.run([pdftotext,'-layout',str(root/'rectification.pdf'),str(root/'rectification.txt')],capture_output=True,text=True,timeout=30)
if extract.returncode: raise RuntimeError('pdf text extraction failed: '+extract.stderr)
pdf=(root/'rectification.txt').read_text(encoding='utf-8')
normal=lambda s: ' '.join(s.split())
patterns={'candidaturas':r'1\.488\.805[^0-9]+1\.488\.705','validos':r'1\.501\.857[^0-9]+1\.501\.757'}
checks={k:{'html':bool(re.search(p,html)),'pdf':bool(re.search(p,normal(pdf)))} for k,p in patterns.items()}
aggregate=json.loads(pathlib.Path(r'C:\Users\Nitropc\AppData\Local\Temp\pfl-t016-originals-20261029\AGGREGATE.json').read_text(encoding='utf-8'))['galicia_sum_municipal_files']
reconciled={'validos':aggregate['Votos Válidos']==1501757,'candidaturas':aggregate['Votos Candidaturas']==1488705,'votantes_minus_nulos':aggregate['Votos Totais']-aggregate['Votos nulos']==1501757}
out={'status':'PASS_OFFICIAL_CORRECTION_RECONCILES_CSV','document_date':'2024-03-08','issue':'DOG 49','first_public_at_not_inferred':True,'records':records,'pdf_extraction':{'tool':pdftotext,'exit':extract.returncode,'text_sha256':hashlib.sha256((root/'rectification.txt').read_bytes()).hexdigest()},'document_patterns':checks,'aggregate_checks':reconciled,'scope':'correction applies to general tally only; other T016 criteria remain pending'}
(root/'MANIFEST.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
if not all(v for pair in checks.values() for v in pair.values()) or not all(reconciled.values()): raise SystemExit(1)
