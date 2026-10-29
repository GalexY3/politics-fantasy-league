from pathlib import Path
import json,hashlib,re
known=set()
def collect(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if isinstance(v,str) and re.fullmatch('[0-9a-fA-F]{64}',v):known.add(v.lower())
   else:collect(v)
 elif isinstance(x,list):
  for v in x:collect(v)
for base in [Path('proyectos/politics-fantasy-league/tareas_codex'),Path('C:/Github/Politics-Fantasy-Release-QA/proyectos/politics-fantasy-league/tareas_codex')]:
 for f in base.rglob('*.json'):
  try:collect(json.loads(f.read_text(encoding='utf8')))
  except (UnicodeError,json.JSONDecodeError):pass
base=Path('C:/Github/Metodologia-AB/proyectos/politics-fantasy-league/data/raw');summary=[]
for folder in sorted(base.glob('t0*_20261029')):
 files=[f for f in folder.iterdir() if f.is_file()];matches=sum(hashlib.sha256(f.read_bytes()).hexdigest() in known for f in files)
 summary.append({'folder':folder.name,'files':len(files),'hash_matches':matches,'unmatched':len(files)-matches})
print(json.dumps({'raw_contents_exported':False,'folders':summary},indent=2))
