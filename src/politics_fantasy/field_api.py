"""Read-only, allowlisted adapter for local CSV audit receipts.

Never serve uploaded/raw nominal votes or trust an edited receipt. Even a valid
receipt is not proof of independent source certification, and cannot feed the game.
"""
from __future__ import annotations
import hashlib
import hmac
import json
from pathlib import Path

MAX_RECEIPT_BYTES = 512 * 1024


def local_field_status(path: Path | None) -> dict:
    absent={'mode':'FIELD_CSV_NOT_IMPORTED', 'real_person_scoring':False,
            'certified':False,'VSDS':1,
            'message':'Importe manualmente dos CSV con python -m politics_fantasy.field_cli; jamás se descargan automáticamente.'}
    if path is None or not Path(path).exists():return absent
    try:
        p=Path(path)
        with p.open('rb') as f:
            content=f.read(MAX_RECEIPT_BYTES+1)
        if len(content)>MAX_RECEIPT_BYTES:raise ValueError('Receipt too large')
        loaded=json.loads(content.decode('utf-8'))
        if not isinstance(loaded,dict) or loaded.get('schema_version')!='1.0' or loaded.get('mode')!='USER_SUPPLIED_CSV_UNCERTIFIED':
            raise ValueError('Unexpected report schema')
        signature=loaded.get('report_sha256','')
        if not isinstance(signature,str) or len(signature)!=64:raise ValueError('Missing report signature')
        clean={k:v for k,v in loaded.items() if k!='report_sha256'}
        binary=json.dumps(clean,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
        if not hmac.compare_digest(hashlib.sha256(binary).hexdigest(),signature):
            raise ValueError('Modified local report')
        if loaded.get('empirical_findings_validated') is not False or loaded.get('may_score_real_persons') is not False:
            raise ValueError('Unsafe claims')
        overview=loaded.get('coverage',{})
        if not isinstance(overview,dict) or not all(isinstance(overview.get(k),dict) for k in ('individual','aggregate')):
            raise ValueError('Bad summary structure')
        # Whitelist only aggregated fields; no arbitrary source-provided strings.
        votes=overview['individual']; sums=overview['aggregate']
        fields=('n_rows','n_votations','n_deputy_ids','explicit_no_vote','expressed')
        if any(not isinstance(votes.get(k),int) or isinstance(votes[k],bool) or votes[k]<0 for k in fields):
            raise ValueError('Bad count')
        if any(not isinstance(sums.get(k),int) or isinstance(sums[k],bool) or sums[k]<0 for k in ('n_rows','sum_yes','sum_no','sum_abstain','sum_no_vote')):
            raise ValueError('Bad aggregate')
        group=loaded.get('group_audit')
        if group is not None:
            if not isinstance(group,dict):raise ValueError('Bad group audit')
            group_keys=('group_rows','group_labels','votations','years','total_expressed','total_explicit_nonvote',
                        'nominal_group_undercounts','nominal_group_overages','group_date_conflicts')
            if any(type(group.get(k)) is not int or group[k]<0 for k in group_keys):
                raise ValueError('Group counts invalid')
            if type(group.get('aggregate_consistent')) is not bool or type(group.get('nominal_group_complete')) is not bool:
                raise ValueError('Group consistency invalid')
        return {'mode':'USER_SUPPLIED_CSV_UNCERTIFIED', 'certified':False,
                'real_person_scoring':False,'VSDS':1,'report_sha256':signature,
                'n_nominal_rows':votes['n_rows'],'n_votations':votes['n_votations'],
                'n_deputy_ids':votes['n_deputy_ids'],
                'explicit_no_vote':votes['explicit_no_vote'],
                'n_aggregate_votes':sums['n_rows'],
                'sum_aggregate_yes':sums['sum_yes'],
                'sum_aggregate_no':sums['sum_no'],
                'sum_aggregate_abstain':sums['sum_abstain'],
                'sum_aggregate_no_vote':sums['sum_no_vote'],
                'reconciliation_complete':loaded.get('reconciliation',{}).get('any_unresolved') is False,
                'group_audit':None if group is None else {
                    'group_rows':group['group_rows'],'group_labels':group['group_labels'],
                    'votations':group['votations'],
                    'aggregate_consistent':group['aggregate_consistent'],
                    'nominal_group_complete':group['nominal_group_complete'],
                    'nominal_group_undercounts':group['nominal_group_undercounts'],
                    'nominal_group_overages':group['nominal_group_overages'],
                    'group_date_conflicts':group['group_date_conflicts'],
                    'interpretation':'RECUENTOS_DESCRIPTIVOS_NO_DISCIPLINA',
                    'certified':False},
                'message':'CSV aportados localmente. Sin certificación histórica ni predicción política validada.'}
    except (OSError,ValueError,UnicodeError,TypeError,KeyError,AttributeError):
        return {'mode':'FIELD_REPORT_REJECTED','certified':False,'real_person_scoring':False,'VSDS':1,
                'message':'Informe no verificable. Regénere el JSON desde los CSV; sin datos personales expuestos.'}
