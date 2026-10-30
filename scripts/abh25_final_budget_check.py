"""Check the exhausted ABH25 grant without touching prior balances."""
import json
from pathlib import Path
def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))
g=load('research/ABH25_20261030/AUTHORIZATION.json')
s=load('PROJECT_STATE.json')
old=load('research/CONTINUATION20_20261030/AUTHORIZATION.json')
assert g['new_granted']==25 and g['valid_executed']==25 and g['remaining']==0
assert g['planning_only']==1 and len(g['cycle_register'])==25
assert len({x['cycle'] for x in g['cycle_register']})==25
assert all(x['cycle']!='ABH25-C03' for x in g['cycle_register'])
assert old['substantive_units_remaining']==15
assert s['authorization_snapshot']['executed']==6 and s['authorization_snapshot']['remaining']==4
assert s['additional_authorization_snapshot']['executed']==0
assert s['additional_authorization_snapshot']['remaining']==10
assert s['atlas_snapshot']['batches']==97
assert s['atlas_snapshot']['state_sha256']=='609e93fa0abd03b4b0137bbe7549a745fd0a4f8c7317932cb6fc9057ba573ebc'
assert s['atlas_snapshot']['passed_gates']==0
assert s['scientific_status']['prospective_CT2_ordinal']==20
assert s['abh25_authorization_snapshot']['scientific_discoveries']==0
print('ABH25_FINAL_GRANT_AND_SCIENCE_SEPARATION_PASS')
