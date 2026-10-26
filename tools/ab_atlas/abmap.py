#!/usr/bin/env python3
"""AB Atlas 0.2: portable graph + project operations, no third-party dependencies.

The store is a versioned JSON document.  It never claims empirical validation based on
files or unit tests alone. CLI writes atomically and validates before replacement.
"""
import argparse
from collections import Counter
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys
import uuid

VERSION = '1.1'
KINDS = {'project','research','goal','question','hypothesis','experiment','finding','decision','task','deliverable','risk','blocker','artifact','method_change','milestone','requirement','gate','complaint'}
STATUSES = {'open','active','answered','validated','blocked','closed','refuted','superseded','proposed','unreviewed'}
MODES = {'research','project','hybrid','meta'}
RELATIONS = {'branches_from','depends_on','tests','supports','refutes','answers','produces','blocks','replaces','merges','references','implements','improves','related_to'}
SEVERITIES = {'info','minor','major','critical'}
ISSUE_STATES = {'open','triaged','repaired','verified','rejected'}
GATE_STATES = {'pending','blocked','passed','waived'}
RUN_STATES = {'planned','running','completed','failed','invalid','stopped'}
PHASES = {'discover','specify','build','verify','release','operate'}
SCHEMA_SUPPORTED = {'1.0','1.1'}

def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

def newid(prefix='n'):
    return prefix + '_' + uuid.uuid4().hex[:14]

def read(path):
    with open(path, encoding='utf-8') as f:
        doc=json.load(f)
    return doc

def atomic_write(path, doc):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name + '.tmp.' + uuid.uuid4().hex[:10])
    try:
        with temp.open('w',encoding='utf-8') as f:
            json.dump(doc,f,ensure_ascii=False,indent=2)
            f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(temp,path)
    finally:
        if temp.exists(): temp.unlink()

def event(doc, action, payload, actor='cli'):
    doc.setdefault('events',[]).append({'id':newid('evt'),'at':now(),'actor':actor,'action':action,'payload':payload})
    doc['updated_at']=now()

def _cycles(edges,relation):
    adjacency={}
    for e in edges:
        if e.get('relation')==relation:
            adjacency.setdefault(e.get('from'),[]).append(e.get('to'))
    visiting=set();done=set()
    def visit(v):
        if v in visiting:return True
        if v in done:return False
        visiting.add(v)
        for u in adjacency.get(v,[]):
            if visit(u):return True
        visiting.remove(v);done.add(v)
        return False
    return any(visit(v) for v in adjacency)

def validate(doc, strict=False):
    err=[]
    if doc.get('schema_version') not in SCHEMA_SUPPORTED:err.append('schema_version no soportada')
    nodes=doc.get('nodes'); edges=doc.get('edges')
    if not isinstance(nodes,list) or not isinstance(edges,list):return ['nodes/edges deben ser listas']
    ids=[n.get('id') for n in nodes]
    if len(ids)!=len(set(ids)):err.append('IDs de nodos duplicados')
    if not ids:err.append('Se exige al menos un nodo raíz')
    if doc.get('mode') not in MODES:err.append('Modo general inválido')
    nodeids=set(ids)
    for n in nodes:
        nid=n.get('id')
        if not isinstance(nid,str) or not nid:err.append('ID de nodo no válido')
        if not str(n.get('title','')).strip():err.append(f'{nid}: título obligatorio')
        if n.get('kind') not in KINDS:err.append(f'{nid}: tipo inválido')
        if n.get('mode') not in MODES:err.append(f'{nid}: modo inválido')
        if n.get('status') not in STATUSES:err.append(f'{nid}: estado inválido')
        a=n.get('acceptance')
        if a is not None:
            if not isinstance(a,dict):err.append(f'{nid}: aceptación no estructurada')
            elif a.get('verified') and not (a.get('criteria') and a.get('evidence') and a.get('verified_by')):
                err.append(f'{nid}: aceptación verificada sin criterios, evidencia y verificador')
        if strict and doc.get('schema_version')=='1.1' and n.get('kind') in ('deliverable','requirement') and n.get('status')=='validated':
            if not isinstance(a,dict) or not a.get('verified'):err.append(f'{nid}: validación sin aceptación verificada')
    edgeids=[e.get('id') for e in edges]
    if len(edgeids)!=len(set(edgeids)):err.append('IDs de relaciones duplicados')
    for e in edges:
        if e.get('from') not in nodeids or e.get('to') not in nodeids:err.append(f'{e.get("id")}: extremo de enlace inexistente')
        if e.get('relation') not in RELATIONS:err.append(f'{e.get("id")}: relación inválida')
        if e.get('from')==e.get('to'):err.append(f'{e.get("id")}: autorrelación inválida')
    for relation in ('depends_on','branches_from'):
        if _cycles(edges,relation):err.append(f'Ciclo detectado en relación {relation}')
    runids=[r.get('id') for r in doc.get('runs',[])]
    if len(runids)!=len(set(runids)):err.append('IDs de ejecución duplicados')
    for r in doc.get('runs',[]):
        if r.get('status') not in RUN_STATES:err.append(f'{r.get("id")}: estado run inválido')
    complaints=doc.get('complaints',[])
    cids=[c.get('id') for c in complaints]
    if len(cids)!=len(set(cids)):err.append('IDs de complaints duplicados')
    for c in complaints:
        if c.get('run_id') not in runids:err.append(f'{c.get("id")}: ejecución inexistente')
        if c.get('severity') not in SEVERITIES:err.append(f'{c.get("id")}: gravedad inválida')
        if c.get('status') not in ISSUE_STATES and c.get('status') not in {'resolved','dismissed'}:err.append(f'{c.get("id")}: estado complaint inválido')
        if not str(c.get('description','')).strip():err.append(f'{c.get("id")}: descripción obligatoria')
    for r in doc.get('runs',[]):
        expected={c['id'] for c in complaints if c.get('run_id')==r['id']}
        actual=r.get('complaint_ids',[])
        if set(actual)!=expected or len(actual)!=len(set(actual)):err.append(f'{r["id"]}: índices de complaints inconsistentes')
    p=doc.get('project_contract')
    if p is not None:
        if not isinstance(p,dict):err.append('project_contract inválido')
        else:
            gates=p.get('release_gates',[])
            gids=[g.get('id') for g in gates]
            if len(gids)!=len(set(gids)):err.append('IDs de gates duplicados')
            for g in gates:
                if g.get('status') not in GATE_STATES:err.append(f'{g.get("id")}: gate inválido')
                if g.get('status')=='passed' and not g.get('evidence'):err.append(f'{g.get("id")}: gate passed sin evidencia')
                if g.get('status')=='waived' and not g.get('rationale'):err.append(f'{g.get("id")}: gate waived sin justificación')
    return err

def require_valid(doc, strict=False):
    errors=validate(doc,strict)
    if errors:raise ValueError('; '.join(errors))

def mutate(path, callback, strict=False):
    doc=read(path);require_valid(doc)
    value=callback(doc)
    require_valid(doc,strict)
    atomic_write(path,doc)
    return value

def add_node(doc,title,kind,mode,status='open',detail='',parent=None,sources=None,phase=None,workstream=None,acceptance=None):
    n={'id':newid(),'title':title,'kind':kind,'mode':mode,'status':status,'detail':detail,'sources':sources or [],'phase':phase,'workstream':workstream,'acceptance':acceptance or {'criteria':'','evidence':[],'verified':False,'verified_by':''},'created_at':now(),'updated_at':now()}
    doc['nodes'].append(n)
    if parent:
        doc['edges'].append({'id':newid('edge'),'from':parent,'to':n['id'],'relation':'branches_from'})
    event(doc,'node_created',{'node_id':n['id'],'parent':parent})
    return n

def init_doc(name,mode='hybrid',outcome='',audience='',scaffold=True):
    root={'id':'root','title':name,'kind':'research' if mode in ('research','meta') else 'project','mode':mode,'status':'active','detail':outcome or 'Objetivo inicial pendiente de especificar','sources':[],'created_at':now(),'updated_at':now()}
    p={'scope_version':'SCOPE-1','outcome':outcome,'audience':audience,'out_of_scope':[],'release_gates':[], 'scope_history':[{'version':'SCOPE-1','at':now(),'reason':'Inicialización; requisitos por definir'}]}
    doc={'schema_version':VERSION,'project_id':re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-') or 'ab-project','title':name,'mode':mode,'created_at':now(),'updated_at':now(),'nodes':[root],'edges':[],'events':[],'runs':[],'complaints':[],'method':{'version':'AB 3.2.1 + O7 pilot','mutable':True},'project_contract':p if mode in ('project','hybrid') else None}
    if scaffold:
        if mode in ('research','meta'):
            seeds=[('Pregunta central','question',mode,'discover'),('Hipótesis alternativas y falsadores','hypothesis',mode,'specify'),('Evidencia y baselines','task',mode,'verify')]
        else:
            seeds=[('Usuarios y resultado esperado','goal','project','discover'),('Alcance y criterios de aceptación','requirement','project','specify'),('Entregables y dependencias','milestone','project','build'),('Verificación y seguridad','gate','project','verify'),('Entrega y operación','deliverable','project','release')]
            if mode=='hybrid':seeds.append(('Preguntas que requieren investigación','question','research','discover'))
        for title,kind,node_mode,phase in seeds:
            add_node(doc,title,kind,node_mode,'proposed','Plantilla inicial no verificada; concretar según contexto.','root',[],phase)
    event(doc,'map_initialized',{'mode':mode,'scaffold':scaffold})
    require_valid(doc)
    return doc

def gate_readiness(doc):
    contract=doc.get('project_contract') or {}
    gates=contract.get('release_gates',[])
    critical=[g for g in gates if g.get('critical',True)]
    return {'ready':bool(critical) and all(g['status']=='passed' for g in critical), 'defined':len(gates),'critical':len(critical),'critical_pending':[g for g in critical if g['status']!='passed'],'all':gates}

def select_next(doc,limit=12):
    """Transparent heuristic, not evidence of information gain or AI planning."""
    edges=doc.get('edges',[])
    blocking=Counter(e['to'] for e in edges if e['relation']=='depends_on' and e.get('from')!=e.get('to'))
    candidates=[]
    for n in doc['nodes']:
        if n['id']=='root' or n['status'] not in ('open','active','blocked','proposed','unreviewed'):continue
        if n['kind']=='artifact' and n['status']=='unreviewed':continue
        issue=2 if n['status']=='blocked' else 0
        gain=3 if n['kind'] in ('blocker','gate','requirement') else 1
        priority=issue+gain+min(4,blocking[n['id']])*2
        candidates.append({'id':n['id'],'title':n['title'],'status':n['status'],'mode':n['mode'],'priority':priority,'blocked_dependents':blocking[n['id']]})
    return sorted(candidates,key=lambda n:(-n['priority'],n['id']))[:limit]

def cmd_init(a):
    path=Path(a.file)
    if path.exists() and not a.force:raise ValueError('Archivo existente; usar --force explícitamente')
    atomic_write(path,init_doc(a.name,a.mode,a.outcome,a.audience,not a.no_scaffold));print(path)

def cmd_add(a):
    def fn(doc):return add_node(doc,a.title,a.kind,a.mode or ('project' if doc['mode']=='hybrid' else doc['mode']),a.status,a.detail,a.parent,[a.source] if a.source else [],a.phase,a.workstream)['id']
    print(mutate(a.file,fn))

def cmd_link(a):
    def fn(doc):
        if any(e['from']==a.source and e['to']==a.target and e['relation']==a.relation for e in doc['edges']):raise ValueError('Relación duplicada')
        e={'id':newid('edge'),'from':a.source,'to':a.target,'relation':a.relation};doc['edges'].append(e);event(doc,'edge_created',e);return e['id']
    print(mutate(a.file,fn))

def cmd_status(a):
    def fn(doc):
        if not a.reason.strip():raise ValueError('Motivo obligatorio')
        n=next((x for x in doc['nodes'] if x['id']==a.node),None)
        if n is None:raise ValueError('Nodo inexistente')
        if a.status=='validated' and doc['schema_version']=='1.1' and n['kind'] in ('deliverable','requirement'):
            if not (n.get('acceptance') or {}).get('verified'):raise ValueError('Exigir aceptación verificada para validar un entregable/requisito')
        prev=n['status'];n['status']=a.status;n['updated_at']=now();event(doc,'status_changed',{'node_id':n['id'],'before':prev,'after':a.status,'reason':a.reason});return a.status
    print(mutate(a.file,fn))

def cmd_accept(a):
    def fn(doc):
        n=next((n for n in doc['nodes'] if n['id']==a.node),None)
        if not n:raise ValueError('Nodo inexistente')
        if n['kind'] not in ('deliverable','requirement','milestone','task'):raise ValueError('Aceptación solo para tareas/entregables/requisitos/hitos')
        if not a.criteria.strip() or not a.evidence.strip() or not a.verified_by.strip():raise ValueError('Criterio, prueba y verificador obligatorios')
        n['acceptance']={'criteria':a.criteria,'evidence':[a.evidence],'verified_by':a.verified_by,'verified':True,'at':now()}
        n['updated_at']=now();event(doc,'acceptance_verified',{'node_id':a.node,'evidence':a.evidence,'verified_by':a.verified_by});return a.node
    print(mutate(a.file,fn))

def cmd_gate(a):
    def fn(doc):
        p=doc.get('project_contract')
        if not p:raise ValueError('Gate disponible solo en proyecto/híbrido')
        gates=p['release_gates'];g=next((g for g in gates if g['id']==a.id),None)
        if not g:
            if not a.label:raise ValueError('Etiqueta obligatoria para nuevo gate')
            g={'id':a.id,'label':a.label,'critical':not a.noncritical,'status':'pending','evidence':[],'rationale':''};gates.append(g)
        if a.status:
            if a.status=='passed' and not a.evidence:raise ValueError('Gate pasado requiere evidencia')
            if a.status=='waived' and not a.reason:raise ValueError('Waiver requiere justificación')
            before=g['status'];g['status']=a.status
            if a.evidence:g['evidence'].append(a.evidence)
            if a.reason:g['rationale']=a.reason
            event(doc,'gate_status_changed',{'gate_id':a.id,'before':before,'after':a.status,'reason':a.reason,'evidence':a.evidence})
        else:event(doc,'gate_created',{'gate_id':a.id})
        return g['id']
    print(mutate(a.file,fn))

def cmd_scope(a):
    def fn(doc):
        p=doc.get('project_contract')
        if not p:raise ValueError('Scope solo para proyectos')
        if not a.reason.strip():raise ValueError('Justificación obligatoria')
        previous=p['scope_version'];next_version='SCOPE-'+str(len(p['scope_history'])+1)
        p['scope_version']=next_version
        if a.outcome is not None:p['outcome']=a.outcome
        p['scope_history'].append({'version':next_version,'previous':previous,'at':now(),'reason':a.reason,'outcome':p['outcome']})
        event(doc,'scope_revision',{'previous':previous,'new':next_version,'reason':a.reason})
        return next_version
    print(mutate(a.file,fn))

def cmd_run(a):
    def fn(doc):
        if any(x['id']==a.run_id for x in doc['runs']):raise ValueError('ID de ejecución repetido')
        if a.node and a.node not in {n['id'] for n in doc['nodes']}:raise ValueError('Nodo de ejecución inexistente')
        r={'id':a.run_id,'at':now(),'activity':a.activity,'status':a.status,'node_id':a.node or None,'method_version':a.method_version or doc.get('method',{}).get('version','unknown'),'scope':a.scope or (doc.get('project_contract') or {}).get('scope_version',''),'complaint_ids':[],'cost':{},'evidence':[a.evidence] if a.evidence else []}
        doc['runs'].append(r);event(doc,'run_recorded',{'run_id':a.run_id,'status':a.status});return r['id']
    print(mutate(a.file,fn))

def cmd_complaint(a):
    def fn(doc):
        run=next((r for r in doc['runs'] if r['id']==a.run_id),None)
        if not run:raise ValueError('Registra primero la ejecución')
        if not a.description.strip():raise ValueError('Descripción obligatoria')
        duplicates=[c for c in doc['complaints'] if c['run_id']==a.run_id and c['description'].strip().casefold()==a.description.strip().casefold()]
        if duplicates:raise ValueError('Complaint duplicada en la misma ejecución: '+duplicates[0]['id'])
        c={'id':newid('cmp'),'run_id':a.run_id,'at':now(),'source':a.reporter,'severity':a.severity,'category':a.category,'description':a.description,'evidence':a.evidence or '','status':'open','suspected_cause':'','verified_cause':'','proposed_change':'','resolution':''}
        doc['complaints'].append(c);run['complaint_ids'].append(c['id']);event(doc,'complaint_created',{'complaint_id':c['id'],'run_id':a.run_id});return c['id']
    print(mutate(a.file,fn))

def cmd_triage(a):
    def fn(doc):
        c=next((x for x in doc['complaints'] if x['id']==a.complaint),None)
        if not c:raise ValueError('Complaint inexistente')
        if not a.reason.strip():raise ValueError('Motivo de triage obligatorio')
        if a.status=='verified' and not (a.evidence or c.get('evidence')):raise ValueError('Verificación requiere evidencia')
        before=c['status'];c['status']=a.status;c['resolution']=a.reason
        if a.evidence:c['evidence']=a.evidence
        event(doc,'complaint_triaged',{'complaint_id':c['id'],'before':before,'after':a.status,'reason':a.reason});return c['id']
    print(mutate(a.file,fn))

def cmd_method_change(a):
    def fn(doc):
        if a.decision=='adopt' and not (a.version and a.version.strip() and a.approved_by and a.baseline and a.evidence):raise ValueError('Adopción requiere aprobador, comparador y evidencia; si es exploratorio usar propose')
        entry={'id':newid('rfc'),'at':now(),'decision':a.decision,'description':a.description,'rationale':a.rationale,'baseline':a.baseline or '', 'evidence':a.evidence or '', 'approved_by':a.approved_by or '', 'status':'UNVALIDATED' if a.decision=='propose' else 'ADOPTED_UNDER_REVIEW'}
        doc.setdefault('method_changes',[]).append(entry)
        if a.decision=='adopt':doc['method']['version']=a.version
        event(doc,'method_change',{'rfc_id':entry['id'],'decision':a.decision})
        return entry['id']
    print(mutate(a.file,fn))

def cmd_scan(a):
    base=Path(a.root).resolve()
    if not base.is_dir():raise ValueError('Directorio inexistente')
    if not 0 <= a.limit <= 10000:raise ValueError('Límite fuera de rango')
    suffixes={'.md','.json','.yaml','.yml','.csv','.py','.js','.mjs','.ts','.ipynb','.html','.sql','.txt'}
    ignored={'.git','node_modules','.venv','venv','__pycache__','dist','build','.next','.cache'}
    def fn(doc):
        seen={s for n in doc['nodes'] for s in n.get('sources',[])};count=0
        for p in sorted(base.rglob('*')):
            if count>=a.limit:break
            if p.is_symlink() or not p.is_file() or p.suffix.lower() not in suffixes:continue
            rel=p.relative_to(base)
            if any(part in ignored or part.startswith('.tmp') for part in rel.parts):continue
            if str(rel) in seen or p.resolve()==Path(a.file).resolve():continue
            add_node(doc,str(rel),'artifact',doc.get('mode','hybrid'),'unreviewed','Inventario de archivo no inspeccionado: ninguna conclusión de validez.',a.parent,[str(rel)])
            seen.add(str(rel));count+=1
        event(doc,'scan_completed',{'new_artifacts':count,'root':str(base),'limit':a.limit})
        return count
    print('Artefactos sin revisar:',mutate(a.file,fn))

def cmd_summary(a):
    doc=read(a.file);require_valid(doc)
    result={'project':doc['title'],'mode':doc['mode'],'schema':doc['schema_version'],'nodes':len(doc['nodes']),'edges':len(doc['edges']),'status':dict(Counter(n['status'] for n in doc['nodes'])),'runs':len(doc['runs']),'open_complaints':[c for c in doc['complaints'] if c['status'] not in ('verified','rejected','resolved','dismissed')],'release':gate_readiness(doc) if doc.get('project_contract') else None,'next_actions':select_next(doc)}
    if a.output:atomic_write(a.output,result);print(a.output)
    else:print(json.dumps(result,ensure_ascii=False,indent=2))

def cmd_inspect(a):
    doc=read(a.file);require_valid(doc)
    seed=a.node or 'root'
    if seed not in {n['id'] for n in doc['nodes']}:raise ValueError('Nodo desconocido')
    selected={seed};frontier={seed}
    for _ in range(a.depth):
        found=set()
        for e in doc['edges']:
            if e['from'] in frontier:found.add(e['to'])
            if e['to'] in frontier:found.add(e['from'])
        frontier=found-selected;selected|=frontier
        if len(selected)>a.max_nodes:raise ValueError('Límite de contexto excedido; reduce --depth')
    out={'project':doc['title'],'selected_nodes':[n for n in doc['nodes'] if n['id'] in selected],'selected_edges':[e for e in doc['edges'] if e['from'] in selected and e['to'] in selected],'open_complaints':[c for c in doc['complaints'] if c['status'] in ('open','triaged')],'release':gate_readiness(doc) if doc.get('project_contract') else None}
    print(json.dumps(out,ensure_ascii=False,indent=2))

def cmd_validate(a):
    e=validate(read(a.file),a.strict)
    if e:
        print('ERRORES:',*e,sep='\n- ');sys.exit(1)
    print('OK: esquema e integridad referencial; no verifica verdad de fuentes ni validación empírica')

def cmd_build(a):
    doc=read(a.file);require_valid(doc)
    base=Path(__file__).resolve().parent
    template=(base/'viewer/template.html').read_text(encoding='utf-8')
    fallback=read(base/'examples/ab_meta_example.json')
    def embed(obj):return json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    template=template.replace('__POLITICS_JSON__',embed(doc)).replace('__META_JSON__',embed(fallback))
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(template,encoding='utf-8')
    print(f'{out} · {len(doc["nodes"])} nodos · archivo autónomo')

def main():
    p=argparse.ArgumentParser(description='AB Atlas 0.2 · mapa, proyecto y metodología autocorrectiva')
    sub=p.add_subparsers(dest='cmd',required=True)
    def action(name,handler):
        x=sub.add_parser(name);x.add_argument('--file',default='ab_graph.json');x.set_defaults(fn=handler);return x
    x=action('init',cmd_init);x.add_argument('--name',required=True);x.add_argument('--mode',choices=sorted(MODES),default='hybrid');x.add_argument('--outcome',default='');x.add_argument('--audience',default='');x.add_argument('--no-scaffold',action='store_true');x.add_argument('--force',action='store_true')
    x=action('add',cmd_add);x.add_argument('--title',required=True);x.add_argument('--kind',choices=sorted(KINDS),default='task');x.add_argument('--mode',choices=sorted(MODES));x.add_argument('--status',choices=sorted(STATUSES),default='open');x.add_argument('--detail',default='');x.add_argument('--parent',default='root');x.add_argument('--source');x.add_argument('--phase',choices=sorted(PHASES));x.add_argument('--workstream')
    x=action('link',cmd_link);x.add_argument('--source',required=True);x.add_argument('--target',required=True);x.add_argument('--relation',choices=sorted(RELATIONS),required=True)
    x=action('status',cmd_status);x.add_argument('--node',required=True);x.add_argument('--status',choices=sorted(STATUSES),required=True);x.add_argument('--reason',required=True)
    x=action('accept',cmd_accept);x.add_argument('--node',required=True);x.add_argument('--criteria',required=True);x.add_argument('--evidence',required=True);x.add_argument('--verified-by',required=True)
    x=action('gate',cmd_gate);x.add_argument('--id',required=True);x.add_argument('--label');x.add_argument('--noncritical',action='store_true');x.add_argument('--status',choices=sorted(GATE_STATES));x.add_argument('--evidence');x.add_argument('--reason')
    x=action('scope',cmd_scope);x.add_argument('--reason',required=True);x.add_argument('--outcome')
    x=action('run',cmd_run);x.add_argument('--run-id',required=True);x.add_argument('--activity',required=True);x.add_argument('--status',choices=sorted(RUN_STATES),default='completed');x.add_argument('--method-version');x.add_argument('--node');x.add_argument('--scope');x.add_argument('--evidence')
    x=action('complaint',cmd_complaint);x.add_argument('--run-id',required=True);x.add_argument('--reporter',choices=['human','agent','automatic','auditor'],default='agent');x.add_argument('--severity',choices=sorted(SEVERITIES),required=True);x.add_argument('--category',required=True);x.add_argument('--description',required=True);x.add_argument('--evidence')
    x=action('triage',cmd_triage);x.add_argument('--complaint',required=True);x.add_argument('--status',choices=sorted(ISSUE_STATES),required=True);x.add_argument('--reason',required=True);x.add_argument('--evidence')
    x=action('method-change',cmd_method_change);x.add_argument('--decision',choices=['propose','adopt'],required=True);x.add_argument('--version',default='');x.add_argument('--description',required=True);x.add_argument('--rationale',required=True);x.add_argument('--baseline');x.add_argument('--evidence');x.add_argument('--approved-by')
    x=action('scan',cmd_scan);x.add_argument('--root',required=True);x.add_argument('--limit',type=int,default=150);x.add_argument('--parent',default='root')
    x=action('inspect',cmd_inspect);x.add_argument('--node');x.add_argument('--depth',type=int,default=1);x.add_argument('--max-nodes',type=int,default=150)
    x=action('summary',cmd_summary);x.add_argument('--output')
    x=action('validate',cmd_validate);x.add_argument('--strict',action='store_true')
    x=action('build',cmd_build);x.add_argument('--output',default='AB_Atlas.html')
    a=p.parse_args()
    try:a.fn(a)
    except (ValueError,KeyError,OSError,TypeError) as e:
        print('ERROR:',e,file=sys.stderr);sys.exit(2)

if __name__=='__main__':main()
