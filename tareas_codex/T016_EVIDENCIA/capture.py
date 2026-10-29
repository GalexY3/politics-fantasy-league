"""Read-only official source capture: personal records remain local and unversioned."""
import datetime, hashlib, json, pathlib, urllib.request
ROOT=pathlib.Path(__file__).parent; RAW=ROOT/'private_raw'; RAW.mkdir(exist_ok=True)
urls={
 'dog_galicia':'https://www.xunta.gal/dog/Publicados/2024/20240306/AnuncioG2453-050324-1_es.html',
 'dog_catalogue':'https://datos.gob.es/es/catalogo/a12002994-elecciones-al-parlamento-de-galicia-resultados-2024',
 'boe_europeas':'https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-13092',
 'euskadi_definitive_notice':'https://www.euskadi.eus/gobierno-vasco/-/noticia/2024/publicados-resultados-definitivos-elecciones-al-parlamento-vasco-del-21-abril/',
}
out=[]
for name,url in urls.items():
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'PFL-research-source-QA/1.0'})
        with urllib.request.urlopen(req,timeout=30) as r:
            body=r.read(); status=r.status; final=r.geturl(); headers=dict(r.headers.items())
        f=RAW/(name+'.html'); f.write_bytes(body)
        out.append({'source':name,'url_requested':url,'url_effective':final,'status':status,
          'started_utc':started,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'sha256':hashlib.sha256(body).hexdigest(),'size_bytes':len(body),
          'content_type':headers.get('Content-Type'),'last_modified':headers.get('Last-Modified'),
          'tls':'verified system trust','first_public_at':'UNKNOWN','local_original':str(f)})
        print(name,status,len(body),final)
    except Exception as exc:
        out.append({'source':name,'url_requested':url,'started_utc':started,
                    'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'error':repr(exc),'first_public_at':'UNKNOWN'})
        print(name,'FAIL',type(exc).__name__,str(exc))
(ROOT/'MANIFEST.json').write_text(json.dumps({'schema':'pfl.t016.capture.v1','sources':out,
 'note':'HTML originals can contain personal names; do not commit originals. Rights, first_public_at and full QA not verified. Euskadi ZIP separately failed TLS and was not retried.'},
 ensure_ascii=False,indent=2)+'\n',encoding='utf8')
