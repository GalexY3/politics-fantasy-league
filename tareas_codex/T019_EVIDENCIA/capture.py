"""T019: capture official XML and compare aggregate fixture; never publish raw files."""
import datetime, hashlib, json, pathlib, re, subprocess, urllib.parse, urllib.request, xml.etree.ElementTree as ET

ROOT=pathlib.Path(__file__).resolve().parent
HEAD='7a6876f71b6cbc286f86ff4bf1393889e4f22851'
REPO=pathlib.Path(r'C:\Github\Politics-Fantasy-Codex')
RAW=ROOT/'private_raw'; RAW.mkdir(exist_ok=True)
records=[]; comparisons=[]

def capture(url):
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    req=urllib.request.Request(url,headers={'User-Agent':'PFL-research-source-QA/1.0'})
    with urllib.request.urlopen(req,timeout=30) as r:
        body=r.read(); final=r.geturl(); headers=dict(r.headers.items()); status=r.status
    ended=datetime.datetime.now(datetime.timezone.utc).isoformat()
    if urllib.parse.urlparse(final).hostname != 'clerk.house.gov': raise RuntimeError('unexpected redirect host')
    return body,{'url_requested':url,'url_effective':final,'status':status,'started_utc':started,'ended_utc':ended,
        'size_bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'content_type':headers.get('Content-Type'),
        'last_modified':headers.get('Last-Modified'),'etag':headers.get('ETag'),'tls':'verified system trust',
        'redirected':url!=final,'first_public_at':'UNKNOWN'}

try:
    for year in (2025,2026):
        path=f'proyectos/politics-fantasy-league/research/ABH_USHOUSE5_20261028/C0{1 if year==2025 else 2}_{year}_OFFICIAL_AGGREGATES.json'
        raw=subprocess.check_output(['git','show',f'{HEAD}:{path}'],cwd=REPO)
        fixture=json.loads(raw)
        for expected in fixture['rows']:
            roll=expected['roll']; page=f'https://clerk.house.gov/Votes/{year}{roll}'
            body,page_meta=capture(page)
            links=re.findall(rb'href=["\']([^"\']+)["\'][^>]*>\s*XML View',body,re.I)
            if len(links)!=1: raise RuntimeError(f'{year}/{roll}: XML View link count {len(links)}')
            xml_url=urllib.parse.urljoin(page,links[0].decode('ascii'))
            if urllib.parse.urlparse(xml_url).hostname!='clerk.house.gov': raise RuntimeError('untrusted XML host')
            xml_body,meta=capture(xml_url)
            (RAW/f'{year}-{roll}.xml').write_bytes(xml_body)
            root=ET.fromstring(xml_body)
            if root.tag!='rollcall-vote': raise RuntimeError('unexpected root')
            m=root.find('vote-metadata'); party_tags=('yea','nay','present','not_voting')
            def counts(element): return {k:int(element.findtext(k.replace('_','-')+'-total')) for k in party_tags}
            totals=counts(m.find('./vote-totals/totals-by-vote'))
            parties={e.findtext('party'):counts(e) for e in m.findall('./vote-totals/totals-by-party')}
            test={
               'roll':int(m.findtext('rollcall-num'))==roll,
               'date':datetime.datetime.strptime(m.findtext('action-date'),'%d-%b-%Y').date().isoformat()==expected['date'],
               'question':m.findtext('vote-question').strip().casefold()==expected['question'].strip().casefold(),
               'vote_type':m.findtext('vote-type').strip().casefold()==expected['vote_type'].strip().casefold(),
               'totals':totals==expected['totals'],
               'party_fixture_fields':all(parties.get(p,{}).get(k)==v for p,values in expected['parties'].items() for k,v in values.items()),
               'party_sum_all_categories':all(sum(v[k] for v in parties.values())==totals[k] for k in party_tags),
            }
            meta.update({'year':year,'roll':roll,'xml_view_link_verified':True,'official_page':page_meta,
                         'xml_root':root.tag,'local_original':str(RAW/f'{year}-{roll}.xml')})
            records.append(meta); comparisons.append({'year':year,'roll':roll,'checks':test,
                'totals':totals,'party_aggregate':parties,'mismatches':[k for k,v in test.items() if not v]})
finally:
    (ROOT/'MANIFEST.json').write_text(json.dumps({'schema':'pfl.t019.capture.v1','source_commit':HEAD,
       'note':'Raw XML nominative; local only. Capture time is not first-publication time; rights review and full QA pending.',
       'records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'COMPARE.json').write_text(json.dumps({'source_commit':HEAD,'scope':'aggregate cross-check; no personal rows',
       'rows':comparisons,'counts':{'files':len(comparisons),'mismatches':sum(bool(c['mismatches']) for c in comparisons)}},
       ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

print('files',len(comparisons),'mismatching_files',sum(bool(c['mismatches']) for c in comparisons))
for c in comparisons:
    if c['mismatches']: print(c['year'],c['roll'],c['mismatches'])
