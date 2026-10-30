from pathlib import Path
import subprocess,json,hashlib
root=Path('proyectos/politics-fantasy-league');names=['product/progress_scope_v4_20261027.json','ab_atlas/ACHIEVEMENTS_REGISTRY.json'];records=[]
for name in names:
 path=root/name;original=subprocess.check_output(['git','show','a95b7e5c:'+path.as_posix()]);current=subprocess.check_output(['git','show','HEAD:'+path.as_posix()])
 assert original==current,name
 records.append({'file':name,'git_bytes_unchanged_from_baseline':True,'sha256':hashlib.sha256(current).hexdigest()})
r=subprocess.run([__import__('sys').executable,str(root/'ab_atlas/validate_achievements.py')],capture_output=True)
print(json.dumps({'scope_and_badges':records,'validator_exit':r.returncode,'validator_stdout':r.stdout.decode('utf8','replace'),'validator_stderr':r.stderr.decode('utf8','replace'),'scientific_progress_promoted':False},indent=2));raise SystemExit(r.returncode)
