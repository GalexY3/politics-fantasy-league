"""Compare page 1's aggregated tally, not local officials or person records."""
import hashlib,json,pathlib,re,subprocess
R=pathlib.Path(__file__).parent; p=R/'private_raw/rioja_pdf.pdf';HEAD='7a6876f71b6cbc286f86ff4bf1393889e4f22851'
f='proyectos/politics-fantasy-league/research/ABH_HOLDOUT5_20261028/C03_RIOJA_FINAL_VERSION_COMPARISON.json'
fixture=json.loads(subprocess.check_output(['git','show',f'{HEAD}:{f}'],cwd=r'C:\Github\Politics-Fantasy-Codex'))
cmd=['pdftotext','-f','1','-l','1','-layout',str(p),'-']
run=subprocess.run(cmd,capture_output=True,check=True);text=run.stdout.decode('utf8','replace')
expected_order=['PSOE','VINEA','E_BLANCO','Cs','PACMA','PLRi','PP','PODEMOS-IU','PR+E','VOX']
expected={r['id']:r['final_votes'] for r in fixture['party_rows']}
matches={}
for line in text.splitlines():
 m=re.match(r'^\s*(10|[1-9])\s+\S.*?([\d.]+)\s*$',line)
 if m:
  idx=int(m.group(1));matches[idx]=int(m.group(2).replace('.',''))
checks={'all_ten_party_counts_match':len(matches)==10 and all(matches.get(i+1)==expected[name] for i,name in enumerate(expected_order)),
 'all_four_summary_fields_present':all(format(fixture['official'][k],',').replace(',','.') in text for k in ('electorate','voters','null','blank')),
 'valid_derived':fixture['official']['voters']-fixture['official']['null']==fixture['official']['valid'],
 'candidacy_derived':fixture['official']['valid']-fixture['official']['blank']==fixture['official']['candidacy'],
 'ten_candidates_sum':sum(expected.values())==fixture['official']['candidacy']}
result={'head':HEAD,'original_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_pages':60,'inspected_page':1,
 'reproduction':'pdftotext -f 1 -l 1 -layout; page image visually inspected',
 'source_totals':{k:fixture['official'][k] for k in ('electorate','voters','null','blank','valid','candidacy')},
 'observed_candidate_values_by_published_order':[matches.get(i) for i in range(1,11)],'checks':checks,
 'limitations':['PDF and page image contain personal names: local only','Not a full 60-page municipal reconciliation','First publication timing UNKNOWN']}
(R/'RIOJA_AGGREGATE.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,ensure_ascii=False,indent=2))
if not all(checks.values()):raise SystemExit(1)
