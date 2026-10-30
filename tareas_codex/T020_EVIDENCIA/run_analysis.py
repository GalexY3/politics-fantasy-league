import hashlib,json,os,pathlib,platform,subprocess,sys
import numpy,pandas,scipy,sklearn
root=pathlib.Path(__file__).parent
project=pathlib.Path(r'C:\Github\Politics-Fantasy-Codex\proyectos\politics-fantasy-league\research\ABH_EU27_20261028')
script=project/'analyze_eu27.py'; panel=project/'EU27_OFFICIAL_HTML_TRANSCRIPTION.csv'
p=subprocess.run([sys.executable,str(script)],cwd=project,capture_output=True)
(root/'ANALYSIS.stdout').write_bytes(p.stdout); (root/'ANALYSIS.stderr').write_bytes(p.stderr)
result={'command':[sys.executable,str(script)],'cwd':str(project),'exit_code':p.returncode,'python':platform.python_version(),
 'numpy':numpy.__version__,'pandas':pandas.__version__,'scipy':scipy.__version__,'scikit_learn':sklearn.__version__,
 'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'panel_sha256':hashlib.sha256(panel.read_bytes()).hexdigest(),
 'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()}
if p.returncode==0:
 result['metrics']=json.loads(p.stdout); result['matches_approximate_targets']=all([result['metrics']['n']==27,abs(result['metrics']['c02']['pearson']-(-0.0244))<0.0001,abs(result['metrics']['c02']['spearman']-0.0599)<0.0001,abs(result['metrics']['c04']['spearman']-0.1911)<0.0001,abs(result['metrics']['c05']['M1_2019_women']['mae']-10.09)<0.01,abs(result['metrics']['c05']['M2_2024_turnout']['mae']-11.55)<0.01])
(root/'ANALYSIS_META.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'exit_code':p.returncode,'targets_pass':result.get('matches_approximate_targets'),'stdout_sha256':result['stdout_sha256']}))
if p.returncode or not result.get('matches_approximate_targets'):sys.exit(1)
