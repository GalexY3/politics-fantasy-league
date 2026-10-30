import json, sys, subprocess, hashlib, os
from pathlib import Path

root = Path(r'C:\Programación\PFL-status-20261030')
project = root / 'proyectos/politics-fantasy-league'
out = project / 'tareas_codex/REVISION_20261030'
out.mkdir(exist_ok=True)
os.chdir(root)
sys.path.insert(0, str(root / 'ab_atlas'))
import atlas_delta as delta

base_head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
results = {}
for name, args in {
    'atlas91': ['ab_atlas/atlas_delta.py', 'check', '--base', str(project/'ab_atlas/seed.json'), '--updates', str(project/'ab_atlas/updates')],
    'atlas_tests': ['-m', 'unittest', 'discover', '-s', 'ab_atlas/tests', '-v'],
}.items():
    r = subprocess.run([sys.executable, *args], capture_output=True, env=env)
    for suffix, content in [('stdout', r.stdout), ('stderr', r.stderr)]:
        (out/f'{name}.{suffix}.txt').write_bytes(content)
    results[name] = {'exit': r.returncode, 'command': [sys.executable, *args]}
    assert r.returncode == 0, name
doc, batches = delta.replay(project/'ab_atlas/seed.json', project/'ab_atlas/updates')
snapshot = {
    'source_commit': base_head, 'platform': sys.platform, 'python': sys.version,
    'batches': len(batches), 'state_sha256': delta.digest(doc),
    **{k: len(doc[k]) for k in ['nodes', 'edges', 'runs', 'complaints', 'events']},
    'operations': sum(len(json.loads(p.read_text(encoding='utf-8'))['ops']) for p in (project/'ab_atlas/updates').glob('*.json')),
    'gates': doc['project_contract']['release_gates'],
    'blocked': [n for n in doc['nodes'] if n['status'] == 'blocked'],
    'open_complaints': [c for c in doc['complaints'] if c['status'] in ['open','triaged']],
    'results': results,
    'scope': 'Canonical replay and Atlas tests; not complete product QA or source attestation',
}
(out/'ATLAS91.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

graph_path = project/'research/ABH5B_INCENTIVE_FORMAL_20261029/O7_CAUSAL_GRAPH.json'
add_path = project/'research/ABH30_NEW_20261029/C20_C30_O7_ADDENDUM_PENDING.json'
graph = json.loads(graph_path.read_text(encoding='utf-8'))
add = json.loads(add_path.read_text(encoding='utf-8'))
ids = {n['id'] for n in graph['nodes']}
added=[]
for n in add['nodes']:
    if n['id'] in ids: continue
    item=dict(n, state='answered', summary='Bounded synthetic product QA; no independent human evidence.')
    item['source']='../ABH30_NEW_20261029/'+n['source']
    graph['nodes'].append(item); ids.add(n['id']); added.append(n['id'])
n=add['late_reconciliation']
if n['id'] not in ids:
    graph['nodes'].append(dict(id=n['id'], type='source_feasibility_negative',mode='AB-R',state='blocked',summary='Human forecast source remains unavailable for the stated analysis; no participant data processed.',source='../ABH30_NEW_20261029/'+n['source']))
    ids.add(n['id']); added.append(n['id'])
edge_key = lambda e: (e['from'],e['to'],e['relation'])
keys={edge_key(e) for e in graph['edges']}
original_duplicate_edges = len(graph['edges']) - len(keys)
unique_edges = {}
for edge in graph['edges']:
    unique_edges.setdefault(edge_key(edge), edge)
graph['edges'] = list(unique_edges.values())
for e in add['links']:
    assert e['from'] in ids and e['to'] in ids, e
    if edge_key(e) not in keys:
        graph['edges'].append(e); keys.add(edge_key(e))
assert len(ids)==len(graph['nodes'])
assert all(e['from'] in ids and e['to'] in ids for e in graph['edges'])
assert len(keys)==len(graph['edges'])
campaign=graph['metadata']['latest_campaign'] if 'metadata' in graph else None
if campaign is None:
    for val in graph.values():
        if isinstance(val,dict) and 'latest_campaign' in val:
            campaign=val['latest_campaign'];break
assert campaign is not None
campaign.update(new_valid=30,new_unused=0,latest_valid_cycle='ABH30-C30',invalid_attempts=10,last_source_pr=73,branch='research/pfl-abh30-c20-c30-multiaxis-20261029')
graph['reconciliation_20261030']={'source_commit':base_head,'added_nodes':added,'added_edges':len(add['links']),'removed_exact_duplicate_edges':original_duplicate_edges,'scope':'Applied pending documentary addendum in review branch; no AB cycle, no new causal evidence or main merge.'}
graph_path.write_text(json.dumps(graph,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'O7_RECONCILIATION.json').write_text(json.dumps({'nodes':len(ids),'edges':len(keys),'added_nodes':added,'dangling_edges':0,'duplicate_nodes':0,'duplicate_edges':0},indent=2)+'\n')
print(json.dumps({k:snapshot[k] for k in ['source_commit','batches','state_sha256','nodes','edges','runs','complaints','operations']}))
print('O7',len(ids),'nodes',len(keys),'edges')
