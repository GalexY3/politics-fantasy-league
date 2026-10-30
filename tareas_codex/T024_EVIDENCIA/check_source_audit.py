"""Check original CSVs against recorded C01 source metadata and arithmetic."""
import csv, hashlib, json, sys
from collections import Counter
from pathlib import Path

raw, audit_path, output = map(Path, sys.argv[1:])
audit = json.loads(audit_path.read_text(encoding='utf-8'))
tables, file_checks = {}, []
for reference in audit['sourceFiles']:
    data = (raw / reference['name']).read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    with (raw / reference['name']).open(encoding='utf-8-sig', newline='') as f:
        header_line = next(f).rstrip('\r\n')
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = list(reader)
    keyed = {int(r.get('DivisionID', r.get('DivisionId'))):r for r in rows}
    check = {'name':reference['name'], 'size_ok':len(data)==reference['bytes_utf8'],
             'git_blob_ok':blob==reference['git_blob_sha'], 'header_ok':header_line==reference['header_line'],
             'columns_ok':columns==reference['columns'], 'rows_ok':len(rows)==reference['rows'],
             'unique_ids_ok':len(keyed)==len(rows)}
    file_checks.append(check)
    tables[reference['name'].split('Download')[0]] = keyed
n,e,i,t=(tables[k] for k in ('HouseNominationsByDivision','GeneralEnrolmentByDivision','HouseInformalByDivision','HouseTurnoutByDivision'))
ids = set(n)
assert all(set(table)==ids for table in (e,i,t))
informal_errors, turnout_errors, sum_errors, too_many = [], [], 0, 0
for id in ids:
    ir, tr, er=i[id],t[id],e[id]
    informal_errors.append(abs(float(ir['InformalPercent'])-100*int(ir['InformalVotes'])/int(ir['TotalVotes'])))
    turnout_errors.append(abs(float(tr['TurnoutPercentage'])-100*int(tr['Turnout'])/int(er['Enrolment'])))
    sum_errors += int(int(ir['FormalVotes'])+int(ir['InformalVotes'])!=int(ir['TotalVotes']))
    too_many += int(int(ir['TotalVotes'])>int(tr['Turnout']))
states = dict(Counter(r['StateAb'] for r in n.values()))
demographics = dict(Counter(r['Demographic'] for r in n.values()))
checks = {'states_equal':states==audit['states'], 'demographics_equal':demographics==audit['demographic'],
          'informal_rounding_under_0_012_pp':max(informal_errors)<0.012,
          'turnout_rounding_under_0_012_pp':max(turnout_errors)<0.012,
          'formal_plus_informal_equal_total':sum_errors==0, 'total_not_more_than_turnout':too_many==0}
result={'scope':'COMPARISON_WITH_RECORDED_C01_FACTS_NOT_A_REPLACEMENT_OF_HISTORICAL_MANIFEST',
        'rows':len(ids),'file_checks':file_checks,'checks':checks,
        'max_informal_rounding_error_pp':max(informal_errors),'max_turnout_rounding_error_pp':max(turnout_errors),
        'formal_plus_informal_mismatches':sum_errors,'total_greater_than_turnout':too_many}
output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
ok=all(checks.values()) and all(all(v for k,v in row.items() if k!='name') for row in file_checks)
print(json.dumps({'ok':ok,'rows':len(ids),'checks':checks}))
sys.exit(0 if ok else 1)
