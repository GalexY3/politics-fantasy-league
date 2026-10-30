"""Compare official Navarra aggregate; output no municipality or personal records."""
import csv,hashlib,json,pathlib,subprocess
R=pathlib.Path(__file__).parent;P=R/'private_raw/navarra_csv.csv'
blob=P.read_bytes();data=list(csv.DictReader(blob.decode('utf-8-sig').splitlines()));
HEAD='7a6876f71b6cbc286f86ff4bf1393889e4f22851'
f='proyectos/politics-fantasy-league/research/ABH_HOLDOUT5_20261028/C01_NAVARRA_OFFICIAL_AGGREGATE.json'
expected=json.loads(subprocess.check_output(['git','show',f'{HEAD}:{f}'],cwd=r'C:\Github\Politics-Fantasy-Codex'))
total_rows=[r for r in data if r['Codmun'].strip()=='0'];ordinary=[r for r in data if r['Codmun'].strip()!='0']
keys=[(r['Codcir'],r['Codmun']) for r in ordinary]
if len(keys)!=len(set(keys)):raise ValueError('duplicate territory codes')
summary_mapping={'registered':'Censo_Total','voters':'Votos_Totales','abstention':'Abstención','null':'Votos_Nulos','blank':'Votos_Blancos','valid':'Votos_Validos','candidacy_sum':'Votos_Candidaturas'}
party_mapping={'UPN':'UPN','PSN-PSOE':'PSN-PSOE','EH Bildu':'EH_BILDU','Geroa Bai':'GEROA_BAI','PPN':'PPN','Contigo Zurekin':'CONTIGO_ZUREKIN','Vox':'VOX','Por un mundo más justo':'PUM_MAS_J','Ciudadanos':'CIUDADANOS','Eguzkilore':'EGUZKILORE','Voluntad Foral':'VOLUNTAD_FORAL'}
sums=lambda mapping:{name:sum(int(r[col] or 0) for r in ordinary) for name,col in mapping.items()}
summary=sums(summary_mapping);parties=sums(party_mapping)
checks={'summary_fields_match':all(summary[k]==v for k,v in expected['summary'].items()),
 'all_11_party_totals_match':all(parties[k]==v for k,v in expected['list_votes'].items()),
 'party_sum_to_candidates':sum(parties.values())==summary['candidacy_sum'],
 'valid_plus_null_voters':summary['valid']+summary['null']==summary['voters'],
 'valid_minus_blank_candidates':summary['valid']-summary['blank']==summary['candidacy_sum']}
report={'source_sha256':hashlib.sha256(blob).hexdigest(),'head':HEAD,'encoding':'utf-8-sig','row_count':len(data),
 'municipio_zero_total_rows':len(total_rows),'ordinary_rows':len(ordinary),'territory_keys_unique':True,
 'has_absent_resident_code_990':any(r['Codmun']=='990' for r in ordinary),
 'summary':summary,'party_vote_aggregates':parties,'checks':checks,
 'limitations':['No inference of first_public_at','No direct legal rights verification','No seat data extracted from CSV']}
(R/'NAVARRA_AGGREGATE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2))
if not all(checks.values()):raise SystemExit(1)
