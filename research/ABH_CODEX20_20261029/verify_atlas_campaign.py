from pathlib import Path
import subprocess,sys,json,tempfile
root=Path('proyectos/politics-fantasy-league');base=root/'ab_atlas/seed.json';updates=root/'ab_atlas/updates'
cmd=[sys.executable,'ab_atlas/atlas_delta.py'];r=subprocess.run(cmd+['check','--base',str(base),'--updates',str(updates)],capture_output=True)
print(r.stdout.decode('utf8','replace'));print(r.stderr.decode('utf8','replace'));assert r.returncode==0
with tempfile.TemporaryDirectory() as tmp:
 out=Path(tmp)/'state.json';subprocess.run(cmd+['replay','--base',str(base),'--updates',str(updates),'--out',str(out)],check=True)
 s=json.loads(out.read_text(encoding="utf8"));runs=[r for r in s['runs'] if r['id'].startswith('PFL-CODEX20-C')];assert len(runs)==20
 assert not any(g.get('status')=='passed' for g in s['project_contract']['release_gates'])
 assert len(s['nodes'])==63 and len(s['runs'])==283 and len(s['complaints'])==51
 print(json.dumps({'batch_count':len(list(updates.glob('*.json'))),'campaign_runs':len(runs),'nodes':len(s['nodes']),'runs':len(s['runs']),'complaints':len(s['complaints']),'gates':s['project_contract']['release_gates'], 'gate_promotions_in_new_batch':False},indent=2))
