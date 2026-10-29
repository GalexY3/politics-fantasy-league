"""Sequential, Git-frozen AB-P campaign receipts. No scientific promotion."""
import sys,json,subprocess,datetime,hashlib
from pathlib import Path
sys.stdout.reconfigure(errors='backslashreplace')
sys.stderr.reconfigure(errors='backslashreplace')
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def write(path,x):path.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
mode,cid,*args=sys.argv[1:]
if mode=='plan':
 question,method,acceptance,trigger=args
 x={'id':cid,'type':'AB-P','status':'PREREGISTERED','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':git('rev-parse','HEAD'),'A':question,'B':['Contract holds under the stated control','A concrete counterexample violates it','Evidence insufficient or environment blocked'],'C':{'method':method,'acceptance':acceptance,'baseline':'Existing documented project contract; no claim of scientific novelty'},'D':'Preserve stdout, stderr, command, exit and hashes. Freeze this file on GitHub before execution.','F':'Try ordinary and hostile/negative conditions; preserve failures and distinguish runtime limitations.','G':'Internal software/document audit only. No external causal confirmation.','selection_exposure':trigger,'DRIFT':0,'CT2_before':22,'CT2_after':22,'grade_0_3':0}
 write(HERE/(cid+'_PREREG.json'),x);git('add',str(HERE/(cid+'_PREREG.json')));git('commit','-m',f'PFL CODEX20 {cid} freeze contract [skip ci]');git('push');print(cid,'frozen',git('rev-parse','HEAD'))
elif mode=='run':
 command=args
 if command and command[0]=='--':command=command[1:]
 pre=git('rev-parse','HEAD');out=subprocess.run(command,cwd=ROOT,capture_output=True)
 for name,blob in [('stdout',out.stdout),('stderr',out.stderr)]: (HERE/(cid+'.'+name)).write_bytes(blob)
 rec={'command':command,'cwd':str(ROOT),'code_commit':pre,'exit':out.returncode,'stdout_sha256':hashlib.sha256(out.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(out.stderr).hexdigest()};write(HERE/(cid+'_RUN.json'),rec)
 print(json.dumps(rec));print(out.stdout.decode('utf8',errors='replace')[-1600:]);print(out.stderr.decode('utf8',errors='replace')[-500:])
elif mode=='close':
 finding,decision,next_question=args
 x=json.loads((HERE/(cid+'_PREREG.json')).read_text(encoding='utf8'));x.update({'status':'EXECUTED','prereg_commit':git('log','-1','--format=%H','--',str(HERE/(cid+'_PREREG.json'))),'E':json.loads((HERE/(cid+'_RUN.json')).read_text(encoding='utf8')),'H':{'finding':finding,'hypothesis_update':'Restricted to tested software or documented sources','new_question':next_question},'I':{'scientific_validity':'NOT_ESTABLISHED','novelty':'NOT_CLAIMED','external_replication':'NOT_RUN','CT2_reason':'No new identified external scientific evidence'},'J':decision});write(HERE/(cid+'_RESULT.json'),x)
 c=json.loads((HERE/'CAMPAIGN.json').read_text(encoding='utf8'));c['cycles'].append({'id':cid,'type':'AB-P','result':cid+'_RESULT.json','status':'EXECUTED'});c['executed_valid']=len(c['cycles']);c['remaining_authorized']=20-len(c['cycles']);write(HERE/'CAMPAIGN.json',c)
 git('add',str(HERE));git('commit','-m',f'PFL CODEX20 {cid} record observed outcome [skip ci]');git('push');print(cid,'closed; remaining',c['remaining_authorized'])
