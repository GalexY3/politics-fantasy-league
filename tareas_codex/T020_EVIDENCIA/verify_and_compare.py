import csv, hashlib, json, pathlib, subprocess
root=pathlib.Path(__file__).parent
project=pathlib.Path(r'C:\Github\Politics-Fantasy-Codex\proyectos\politics-fantasy-league')
openssl=r'C:\msys64\ucrt64\bin\openssl.exe'
def run(args):
 p=subprocess.run([openssl]+args,cwd=root,capture_output=True,text=True)
 return {'args':args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
checks={'version':run(['version']), 'certificate':run(['x509','-in','certificate.crt','-noout','-subject','-issuer','-dates','-fingerprint','-sha256']), 'chain':run(['verify','-CAfile','certchain.crt','certificate.crt']), 'public_key':run(['x509','-in','certificate.crt','-pubkey','-noout','-out','public_key.pem'])}
for name in ['turnout','gender_2019','gender_2024']:
 checks[name]=run(['dgst','-sha256','-verify','public_key.pem','-signature',name+'.sig',name+'.csv'])
# Verify the same signature rejects tampered bytes, preserving the original file.
tampered=root/'tampered_control.tmp'; tampered.write_bytes((root/'turnout.csv').read_bytes()+b'\n')
checks['negative_control']=run(['dgst','-sha256','-verify','public_key.pem','-signature','turnout.sig',tampered.name]); tampered.unlink()
def read(name,delimiter):
 with (root/name).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f,delimiter=delimiter))
turnout=read('turnout.csv',';'); gender19=read('gender_2019.csv',';'); gender24=read('gender_2024.csv',';')
with (project/'research/ABH_EU27_20261028/EU27_OFFICIAL_HTML_TRANSCRIPTION.csv').open(encoding='utf-8-sig',newline='') as f: panel=list(csv.DictReader(f))
index_t={(r['COUNTRY_ID'],r['YEAR']):r for r in turnout}
g19={r['COUNTRY_ID']:r for r in gender19};g24={r['COUNTRY_ID']:r for r in gender24}
differences=[]; missing=[]
for row in panel:
 iso=row['iso']
 for field,src in [('turnout2019',index_t.get((iso,'2019'))),('turnout2024',index_t.get((iso,'2024'))),('women2019',g19.get(iso)),('women2024',g24.get(iso))]:
  if src is None:missing.append({'iso':iso,'field':field});continue
  official=float(src['RATE' if field.startswith('turnout') else 'WOMEN']); recorded=float(row[field])
  if abs(official-recorded)>1e-9:differences.append({'iso':iso,'field':field,'official':official,'transcription':recorded})
output={'scope':'OFFICIAL_SIGNED_CURRENT_FILES_VS_PREVIOUS_TRANSCRIPTION_NO_INDEPENDENT_CAUSAL_CONFIRMATION', 'commands':checks,
 'panel_rows':len(panel),'missing':missing,'differences':differences,'fields_compared':4*len(panel),
 'trust_limit':'Certificate and chain downloaded via TLS from official links, openssl verify uses supplied chain as trust anchor; no separate independent root trust validation claimed.'}
(root/'VERIFICATION.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({'crypto_exit_codes':{k:v['exit_code'] for k,v in checks.items()},'rows':len(panel),'missing_count':len(missing),'difference_count':len(differences),'differences':differences}))
if any(checks[k]['exit_code']!=0 for k in ['chain','public_key','turnout','gender_2019','gender_2024']) or checks['negative_control']['exit_code']==0 or missing or differences: raise SystemExit(1)
