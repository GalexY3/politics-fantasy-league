"""Aggregate local official CSVs only; no individual or municipality rows emitted."""
import csv,hashlib,json,pathlib
R=pathlib.Path(__file__).parent; D=R/'private_raw'
numeric=('Censo','Certif Alta','Censo Total','Votos Totais','Votos nulos','Votos brancos','Abstención','Votos Válidos','Votos Candidaturas')
out=[]
for n in (1,3,5,7,9,11,13,15):
 b=(D/f'galicia_csv_{n:03}.csv').read_bytes()
 try: text=b.decode('utf-8-sig'); encoding='utf-8-sig'
 except UnicodeDecodeError: text=b.decode('cp1252');encoding='cp1252'
 rows=list(csv.reader(text.splitlines(),delimiter=';')); header=rows[0]; data=rows[1:]
 if not data or any(len(x)!=len(header) for x in data):raise ValueError(f'bad shape {n}')
 idx={key:header.index(key) for key in numeric}; sums={k:sum(int(x[i] or 0) for x in data) for k,i in idx.items()}
 code=sorted({x[0] for x in data}); out.append({'file':n,'sha256':hashlib.sha256(b).hexdigest(),
  'encoding':encoding,'delimiter':';','columns':len(header),'rows':len(data),'province_codes':code,
  'unit':'municipality' if n%4==1 else 'polling_station','totals':sums})
province_pairs=[{'municipality_file':a['file'],'polling_station_file':b['file'],
 'matching_totals':a['totals']==b['totals'],'matching_province':a['province_codes']==b['province_codes']}
 for a,b in zip(out[::2],out[1::2])]
totals={k:sum(x['totals'][k] for x in out[::2]) for k in numeric}
report={'files':out,'municipality_vs_polling_station':province_pairs,'galicia_sum_municipal_files':totals,
 'scope':'Official open-data files only; compare DOG separately; no causal or denominator assumption',
 'first_public_at':'UNKNOWN'}
(R/'AGGREGATE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'province_pairs':province_pairs,'sum_municipal_files':totals},ensure_ascii=False,indent=2))
