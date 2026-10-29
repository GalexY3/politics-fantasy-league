import hashlib,json,pathlib,subprocess
root=pathlib.Path(__file__).parent
repo=pathlib.Path(r'C:\Github\Politics-Fantasy-Codex')
test='proyectos/politics-fantasy-league/research/ABH_DIVISIONS5_20261028/test_division_ontology_research.mjs'
cmd=['node','--test',test]
run=subprocess.run(cmd,cwd=repo,capture_output=True)
(root/'NODE.stdout').write_bytes(run.stdout);(root/'NODE.stderr').write_bytes(run.stderr)
def call(args): return subprocess.check_output(args,cwd=repo,text=True).strip()
metadata={'cmd':cmd,'exit_code':run.returncode,'node_version':call(['node','--version']),'commit':call(['git','rev-parse','HEAD']),
 'test_blob':call(['git','hash-object',test]),'module_blob':call(['git','hash-object',test.replace('test_division','division')]),
 'stdout_sha256':hashlib.sha256(run.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(run.stderr).hexdigest()}
(root/'NODE_META.json').write_text(json.dumps(metadata,indent=2)+'\n')
print(json.dumps(metadata))
raise SystemExit(run.returncode)
