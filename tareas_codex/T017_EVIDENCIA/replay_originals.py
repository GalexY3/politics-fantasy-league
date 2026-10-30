"""Exact D'Hondt based on captured aggregate votes; compare previously transcribed seats."""
import fractions,json,pathlib,subprocess
R=pathlib.Path(__file__).parent;HEAD='7a6876f71b6cbc286f86ff4bf1393889e4f22851';BASE='proyectos/politics-fantasy-league/research/ABH_HOLDOUT5_20261028/'
def fixture(name):return json.loads(subprocess.check_output(['git','show',f'{HEAD}:{BASE+name}'],cwd=r'C:\Github\Politics-Fantasy-Codex'))
def calc(votes,valid,threshold,seats):
 q=[(fractions.Fraction(v,d),p,d) for p,v in votes.items() if v*100>=valid*threshold for d in range(1,seats+1)]
 q.sort(reverse=True); result={p:0 for p in votes}
 if len(q)<=seats or q[seats-1][0]==q[seats][0]:raise ValueError('boundary tie needs legal tie-break rule')
 for _,p,_ in q[:seats]:result[p]+=1
 return result
nav=json.loads((R/'NAVARRA_AGGREGATE.json').read_text(encoding='utf8'));rio=json.loads((R/'RIOJA_AGGREGATE.json').read_text(encoding='utf8'))
nf=fixture('C01_NAVARRA_OFFICIAL_AGGREGATE.json');rf=fixture('C03_RIOJA_FINAL_VERSION_COMPARISON.json')
votes_r={r['id']:rio['observed_candidate_values_by_published_order'][['PSOE','VINEA','E_BLANCO','Cs','PACMA','PLRi','PP','PODEMOS-IU','PR+E','VOX'].index(r['id'])] for r in rf['party_rows']}
navseats=calc(nav['party_vote_aggregates'],nav['summary']['valid'],3,50);rioseats=calc(votes_r,rio['source_totals']['valid'],5,33)
checks={'navarra_50_seats_match_fixture':navseats==nf['published_seats'],
        'rioja_33_seats_match_fixture':rioseats=={x['id']:x['seats'] for x in rf['party_rows']}}
report={'source_scope':'83 seats computed directly from two freshly captured original aggregates; 45 Asturias seats remain fixture-based',
        'navarra_seats':navseats,'rioja_seats':rioseats,'checks':checks,'head':HEAD}
(R/'DIRECT_83_SEATS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2))
if not all(checks.values()):raise SystemExit(1)
