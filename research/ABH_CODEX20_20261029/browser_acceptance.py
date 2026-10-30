from pathlib import Path
import subprocess,sys,json,os,hashlib
root=Path(__file__).resolve().parents[4];project=root/'proyectos/politics-fantasy-league';out=Path(__file__).parent/'C18_BROWSER';out.mkdir(exist_ok=True)
env={**os.environ,'PYTHONPATH':str(project/'src'),'PF_BROWSER_ARTIFACT':str(out)}
records=[]
for name in ['run_browser_smoke.py','run_playable_smoke.py']:
 r=subprocess.run([sys.executable,str(project/'tests'/name)],cwd=project,env=env,capture_output=True)
 for kind,blob in [('stdout',r.stdout),('stderr',r.stderr)]: (out/(name+'.'+kind)).write_bytes(blob)
 records.append({'test':name,'exit':r.returncode,'stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(r.stderr).hexdigest()})
(out/'RUNS.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records,indent=2));raise SystemExit(1 if any(r['exit'] for r in records) else 0)
