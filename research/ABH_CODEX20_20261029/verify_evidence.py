from pathlib import Path
import json,hashlib
base=Path('proyectos/politics-fantasy-league/tareas_codex');checked=0;errors=[]
for n in range(16,24):
 d=(base/f'T{n:03}_EVIDENCIA').resolve();idx=d/'EVIDENCE_INDEX.json'
 x=json.loads(idx.read_text(encoding='utf8'))
 entries=x.get('files') or x.get('sha256')
 if entries is None:errors.append({'index':str(idx),'error':'unsupported schema'});continue
 for name,entry in entries.items():
  target=(d/name).resolve()
  if not target.is_relative_to(d):errors.append({'file':name,'error':'unsafe path'});continue
  expected=entry if isinstance(entry,str) else entry['sha256']
  if not target.is_file():errors.append({'file':str(target),'error':'missing'});continue
  got=hashlib.sha256(target.read_bytes()).hexdigest();checked+=1
  if got!=expected:errors.append({'file':str(target),'error':'sha256 mismatch','expected':expected,'actual':got})
print(json.dumps({'checked':checked,'errors':errors},indent=2));raise SystemExit(1 if errors else 0)
