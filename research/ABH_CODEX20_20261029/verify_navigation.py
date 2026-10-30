from pathlib import Path
import re,json
root=Path('proyectos/politics-fantasy-league');checked=[]
for relative in ['README.md','tareas_codex/README.md']:
 p=root/relative
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf8')):
  if '://' in link or link.startswith('#'):continue
  target=p.parent/link.split('#')[0]
  assert target.exists(),str(target)
  checked.append(str(target))
x=json.loads((root/'docs/SOURCE_CAPTURE_INDEX_20261029.json').read_text(encoding='utf8'))
for record in x['records']:
 assert (root/record['report']).exists() and (root/record['evidence_directory']).is_dir()
print(json.dumps({'local_links':len(checked),'indexed_sources':len(x['records']),'raw_files_copied':0}))
