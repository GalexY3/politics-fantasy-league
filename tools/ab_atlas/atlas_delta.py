#!/usr/bin/env python3
"""AB Atlas 0.3: append-only patch batches for cheap agent-driven graph maintenance.

Source of truth: immutable baseline JSON + ordered, immutable JSON batch deltas.
No external dependencies. Graph validation provided by the sibling abmap.py.
"""
import argparse
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import sys
from collections import Counter

import abmap

PATCH_SCHEMA = 'ab.atlas.delta.v1'
OPERATIONS = {'node.add','node.set','edge.add','run.add','complaint.add',
              'complaint.triage','gate.add','gate.set','scope.revise','method.propose','method.adopt'}
ALLOWED_NODE_FIELDS = {'title','kind','mode','status','detail','sources','phase','workstream','acceptance'}
MUTABLE_GATE_FIELDS = {'status','evidence','rationale'}
ID_RE = re.compile(r'^[A-Za-z0-9_./:-]{1,100}$')


def canonical(doc):
    return json.dumps(doc, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def digest(doc):
    return hashlib.sha256(canonical(doc)).hexdigest()


def require(cond, message):
    if not cond:
        raise ValueError(message)


def locate(seq, key, value):
    return next((item for item in seq if item.get(key) == value), None)


def record(doc, batch, i, action, payload):
    doc.setdefault('events', []).append({'id':f"{batch['batch_id']}:ev:{i}", 'at':batch['at'],
        'actor': batch.get('actor','agent'), 'action':action, 'payload':payload})
    doc['updated_at'] = batch['at']


def batch_check(batch):
    require(batch.get('schema') == PATCH_SCHEMA,'Schema patch inválido')
    require(isinstance(batch.get('batch_id'),str) and bool(ID_RE.fullmatch(batch['batch_id'])), 'batch_id inválido')
    require(isinstance(batch.get('at'),str) and bool(batch['at'].strip()),'Timestamp obligatorio')
    require(isinstance(batch.get('reason'),str) and bool(batch['reason'].strip()),'Justificación obligatoria')
    require(isinstance(batch.get('ops'),list) and len(batch['ops'])<=250, 'Máximo 250 operaciones por batch')
    require(isinstance(batch.get('parent_batch'),str), 'parent_batch obligatorio, usar "" para origen')


def apply_one(doc, batch, i, op):
    kind=op.get('op'); require(kind in OPERATIONS,f'Op {i}: operación no permitida {kind}')
    nodes=doc['nodes']; edges=doc['edges']; runs=doc['runs']; issues=doc['complaints']
    if kind=='node.add':
        n=copy.deepcopy(op.get('node'))
        require(isinstance(n,dict) and ID_RE.fullmatch(str(n.get('id',''))),f'Op {i}: ID nodo inválido')
        require(not locate(nodes,'id',n['id']),f'Op {i}: nodo duplicado')
        require(set(n)-({'id','created_at','updated_at'}|ALLOWED_NODE_FIELDS)==set(),f'Op {i}: campos nodo desconocidos')
        require(bool(str(n.get('title','')).strip()),'Título de nodo obligatorio')
        n.setdefault('kind','task'); n.setdefault('mode',doc['mode']);n.setdefault('status','proposed')
        n.setdefault('detail',''); n.setdefault('sources',[]); n.setdefault('phase',None)
        n.setdefault('acceptance',{'criteria':'','evidence':[],'verified':False,'verified_by':''})
        n.setdefault('created_at',batch['at']); n['updated_at']=batch['at'];nodes.append(n)
        record(doc,batch,i,kind,{'node_id':n['id']})
    elif kind=='node.set':
        n=locate(nodes,'id',op.get('id')); require(n is not None,f'Op {i}: nodo ausente')
        changes=op.get('set'); require(isinstance(changes,dict) and changes and set(changes)<=ALLOWED_NODE_FIELDS,'Actualización de campos no permitida')
        require(bool(op.get('reason')),'Cambio de nodo requiere reason')
        before={k:n.get(k) for k in changes}
        n.update(copy.deepcopy(changes));n['updated_at']=batch['at']
        if n.get('status')=='validated' and n.get('kind') in {'deliverable','requirement'}:
            require(isinstance(n.get('acceptance'),dict) and n['acceptance'].get('verified'), 'Entregable validado sin aceptación verificada')
        record(doc,batch,i,kind,{'node_id':n['id'],'before':before,'after':changes,'reason':op['reason']})
    elif kind=='edge.add':
        e={k:op.get(k) for k in ('id','from','to','relation')}
        require(ID_RE.fullmatch(str(e['id'] or '')) is not None,'ID relación inválido')
        require(not locate(edges,'id',e['id']),'Relación duplicada')
        require(not any(t['from']==e['from'] and t['to']==e['to'] and t['relation']==e['relation'] for t in edges),'Enlace semánticamente duplicado')
        edges.append(e); record(doc,batch,i,kind,e)
    elif kind=='run.add':
        r=copy.deepcopy(op.get('run'))
        require(isinstance(r,dict) and ID_RE.fullmatch(str(r.get('id',''))),'ID run inválido')
        require(not locate(runs,'id',r['id']),'Run duplicado')
        require(bool(str(r.get('activity','')).strip()),'Actividad run obligatoria')
        r.setdefault('at',batch['at']); r.setdefault('status','completed');r.setdefault('complaint_ids',[])
        r.setdefault('evidence',[]);r.setdefault('cost',{})
        r.setdefault('method_version',doc.get('method',{}).get('version','unknown'))
        r.setdefault('scope',(doc.get('project_contract') or {}).get('scope_version',''))
        runs.append(r);record(doc,batch,i,kind,{'run_id':r['id']})
    elif kind=='complaint.add':
        c=copy.deepcopy(op.get('complaint'))
        require(isinstance(c,dict) and ID_RE.fullmatch(str(c.get('id',''))),'ID complaint inválido')
        require(not locate(issues,'id',c['id']),'Complaint duplicada')
        run=locate(runs,'id',c.get('run_id'));require(run is not None,'Complaint requiere run existente')
        require(bool(str(c.get('description','')).strip()),'Complaint sin descripción')
        c.setdefault('at',batch['at']);c.setdefault('status','open');c.setdefault('severity','minor')
        c.setdefault('category','review');c.setdefault('source','agent')
        c.setdefault('suspected_cause','');c.setdefault('verified_cause','');c.setdefault('resolution','')
        require(not any(t['run_id']==c['run_id'] and t['description'].strip().lower()==c['description'].strip().lower() for t in issues),'Complaint duplicada para run')
        issues.append(c);run.setdefault('complaint_ids',[]).append(c['id']);record(doc,batch,i,kind,{'complaint_id':c['id'],'run_id':c['run_id']})
    elif kind=='complaint.triage':
        c=locate(issues,'id',op.get('id'));require(c is not None,'Complaint inexistente')
        require(bool(op.get('reason')),'Triage sin justificación')
        new=op.get('status');require(new in abmap.ISSUE_STATES,'Estado complaint inválido')
        if new=='verified':require(bool(op.get('evidence') or c.get('evidence')),'Verificación sin evidencia')
        c['status']=new;c['resolution']=op['reason']
        if op.get('evidence'):c['evidence']=op['evidence']
        record(doc,batch,i,kind,{'complaint_id':c['id'],'status':new,'reason':op['reason']})
    elif kind=='gate.add':
        p=doc.get('project_contract');require(isinstance(p,dict),'Los gates exigen AB-P o AB-H')
        g=copy.deepcopy(op.get('gate'))
        require(isinstance(g,dict) and ID_RE.fullmatch(str(g.get('id',''))),'ID gate inválido')
        require(not locate(p['release_gates'],'id',g['id']),'Gate duplicado')
        g.setdefault('status','pending');g.setdefault('critical',True);g.setdefault('evidence',[]);g.setdefault('rationale','')
        require(bool(str(g.get('label','')).strip()),'Etiqueta gate obligatoria')
        p['release_gates'].append(g);record(doc,batch,i,kind,{'gate_id':g['id']})
    elif kind=='gate.set':
        p=doc.get('project_contract') or {};g=locate(p.get('release_gates',[]),'id',op.get('id'))
        require(g is not None,'Gate desconocido')
        changes=op.get('set');require(isinstance(changes,dict) and bool(changes) and set(changes)<=MUTABLE_GATE_FIELDS,'Campo gate inválido')
        require(bool(op.get('reason')),'Cambio gate sin justificación')
        g.update(copy.deepcopy(changes));record(doc,batch,i,kind,{'gate_id':g['id'],'after':changes,'reason':op['reason']})
    elif kind=='scope.revise':
        p=doc.get('project_contract');require(isinstance(p,dict),'Scope requiere proyecto')
        require(bool(op.get('reason')),'Cambio de alcance sin justificación')
        prev=p['scope_version'];nxt=op.get('version')
        require(bool(nxt) and nxt!=prev and nxt not in {v.get('version') for v in p.get('scope_history',[])},'Versión scope nueva y explícita obligatoria')
        p['scope_version']=nxt
        if 'outcome' in op:p['outcome']=op['outcome']
        p['scope_history'].append({'version':nxt,'previous':prev,'at':batch['at'],'reason':op['reason']})
        record(doc,batch,i,kind,{'before':prev,'after':nxt,'reason':op['reason']})
    elif kind in {'method.propose','method.adopt'}:
        require(bool(op.get('description')) and bool(op.get('reason')), 'Propuesta metodológica sin justificación')
        if kind=='method.adopt':
            require(all(op.get(k) for k in ('version','approved_by','baseline','evidence')),'Adopción exige versión, aprobador, comparador y evidencia')
            doc['method']['version']=op['version']
        doc.setdefault('method_changes',[]).append({'id':f"{batch['batch_id']}:rfc:{i}",'at':batch['at'],
            'status':'ADOPTED_UNDER_REVIEW' if kind=='method.adopt' else 'UNVALIDATED',
            'description':op['description'],'rationale':op['reason'],'baseline':op.get('baseline',''),
            'evidence':op.get('evidence',''),'approved_by':op.get('approved_by','')})
        record(doc,batch,i,kind,{'description':op['description']})


def replay(base, patch_dir):
    doc=abmap.read(base);abmap.require_valid(doc,strict=True)
    files=sorted(Path(patch_dir).glob('*.json')) if Path(patch_dir).exists() else []
    last='';batches=[]
    for file in files:
        batch=json.loads(file.read_text(encoding='utf-8'));batch_check(batch)
        require(batch['parent_batch']==last,
            f'{file.name}: conflicto de base, esperaba parent_batch={last!r}, llega {batch["parent_batch"]!r}')
        require(batch['batch_id'] not in batches, f'{file.name}: batch duplicado')
        trial=copy.deepcopy(doc)
        for i,op in enumerate(batch['ops']):apply_one(trial,batch,i,op)
        abmap.require_valid(trial,strict=True)
        # No partial batch commits: validation is applied before accepting trial.
        doc=trial;batches.append(batch['batch_id']);last=batch['batch_id']
    return doc,batches


def brief(doc, batches, count=8, events=6):
    actions=abmap.select_next(doc,limit=count)
    p=doc.get('project_contract')
    blocked=[{'id':n['id'],'title':n['title']} for n in doc['nodes'] if n['status']=='blocked'][:count]
    complaints=[{'id':c['id'],'run_id':c['run_id'],'severity':c['severity'],'description':c['description'][:140]}
                for c in doc.get('complaints',[]) if c['status'] in ('open','triaged')][:count]
    return {'format':'AB-ATLAS-BRIEF-v1','project':doc['project_id'],'mode':doc['mode'],
        'method':doc.get('method',{}).get('version'), 'head_batch':batches[-1] if batches else '',
        'state_sha256':digest(doc),'node_count':len(doc['nodes']),'edge_count':len(doc['edges']),
        'states':dict(Counter(n['status'] for n in doc['nodes'])),'scope':(p or {}).get('scope_version'),
        'readiness':abmap.gate_readiness(doc) if p else None, 'next_actions':actions,
        'blocked':blocked,'open_complaints':complaints,
        'recent_events':[{'at':x.get('at'), 'action':x.get('action'), 'id':x.get('id')} for x in doc['events'][-events:]] if events else []}


def cli():
    parser=argparse.ArgumentParser(description='AB Atlas: actualización incremental y resumen breve para ChatGPT/GitHub')
    sub=parser.add_subparsers(dest='cmd',required=True)
    for cmd in ('template','check','replay','brief','build'):
        p=sub.add_parser(cmd);p.add_argument('--base',required=True);p.add_argument('--updates',required=True)
        if cmd=='template':p.add_argument('--batch-id',required=True);p.add_argument('--out',required=True)
        if cmd in {'replay','build'}:p.add_argument('--out',required=True)
        if cmd=='brief':p.add_argument('--out');p.add_argument('--limit',type=int,default=8)
    a=parser.parse_args()
    try:
        doc,batches=replay(a.base,a.updates)
        if a.cmd=='template':
            batch={'schema':PATCH_SCHEMA,'batch_id':a.batch_id,'parent_batch':batches[-1] if batches else '',
                   'at':dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
                   'actor':'chatgpt','reason':'Actualizar progreso tras bloque de ciclos AB; especificar hallazgos y decisiones','ops':[]}
            Path(a.out).parent.mkdir(parents=True,exist_ok=True)
            Path(a.out).write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(a.out)
        elif a.cmd=='check':print('OK',len(batches),'lotes',len(doc['nodes']),'nodos','SHA256',digest(doc))
        elif a.cmd=='replay':abmap.atomic_write(a.out,doc);print('Reconstruido:',a.out)
        elif a.cmd=='brief':
            content=json.dumps(brief(doc,batches,a.limit),ensure_ascii=False,indent=2)+'\n'
            if a.out:Path(a.out).write_text(content,encoding='utf-8');print(a.out)
            else:print(content)
        elif a.cmd=='build':
            import tempfile
            from types import SimpleNamespace
            with tempfile.TemporaryDirectory() as td:
                f=Path(td)/'state.json';abmap.atomic_write(f,doc)
                abmap.cmd_build(SimpleNamespace(file=str(f),output=a.out))
    except (ValueError,KeyError,TypeError,OSError) as e:
        print('ERROR:',e,file=sys.stderr);sys.exit(2)

if __name__=='__main__':cli()
