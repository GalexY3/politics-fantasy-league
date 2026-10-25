"""Ledger assembly from explicit acceptance contracts + pytest evidence.
Runs no experiments itself. Engineering ledger, NOT scientific confirmation.
"""
from __future__ import annotations
import hashlib,json,subprocess,sys
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'research/BRANCH30_20261025'
branches={
 'A':('contratos_nominales','D0.8','ee73c9b5b8c8c816559b3c9d6713d01159045656','tests/test_rollcall.py','src/politics_fantasy/rollcall.py'),
 'B':('medicion_sociologica','D1.7','33fb72ae867eefc99f0580ac63ad17f082b635b8','tests/test_sociometrics.py','src/politics_fantasy/sociometrics.py'),
 'C':('estructura_relacional','D1.9','65309826bd554493f07b3105551193cacb31eb4f','tests/test_structural.py','src/politics_fantasy/structural.py'),
 'D':('evaluacion_temporal','D2.2','13f4943a5f9c46751f91f8f8c520622dc4c692a9','tests/test_evaluation.py','src/politics_fantasy/evaluation.py'),
 'E':('integracion_producto','D2.0','96cab425a35d4f1b0b2216917853588dadc177b6','tests/test_lab.py','src/politics_fantasy/lab.py'),
}
contracts=[
 ('A','Vocabulario de elecciones nominales', 'Rechazar elecciones fuera de YES, NO, ABSTAIN, NO_VOTE','NO_VOTE explícito no equivale a ausente'),
 ('A','Contradicción intrarrevisión', 'Fallo cerrado ante dos decisiones incompatibles','Primera fila ganadora por azar'),
 ('A','Corte de publicación', 'Exclusión de votos publicados después de corte','Usar únicamente occurred_at'),
 ('A','Corte de adquisición', 'Exclusión de información integrada después de corte','Retrodatar observaciones por fecha declarada'),
 ('A','Revisión conocida más reciente', 'No resucitar versiones antiguas ni conocer futuras','Última fila en orden de lectura'),
 ('A','Afiliación histórica', 'Retener group_at_vote por voto, no grupo presente','Reasignación retrospectiva'),
 ('B','Missingness real', 'Ausencia de fila deviene UNKNOWN, nunca NO_VOTE','Codificar silencio como ausencia'),
 ('B','Exposición elegible', 'Tasa solo con censo íntegro, no censos duplicados','Dividir por n registrado'),
 ('B','Grano grupo–voto–actor', 'Contar cambios de grupo en el evento correcto','Agregado por persona o grupo actual'),
 ('B','Mayoría temporal', 'Mayoría de grupo por cada votación, no global','Moda de toda la legislatura'),
 ('B','Empates y Mixto', 'Excluir empates y Mixto del denominador de discrepancia','Contar toda diferencia como disidencia'),
 ('B','Abstención expresada', 'ABSTAIN cuenta como decisión; NO_VOTE no votó','Tratar abstención como missing'),
 ('C','Margen mayoritario', 'Márgenes sobre solo votos expresos, vacío es unknown','Dividir por escaños nominales'),
 ('C','Diversidad expresada', 'Entropía normalizada de YES/NO/ABSTAIN','Incluir silencios como opción política'),
 ('C','Estandarización directa', 'Pesos comunes y censos de estratos completos','Media cruda de agenda sesgada'),
 ('C','Simpson descriptivo', 'Detectar inversión agregada sin inferir causalidad','Ignorar composición de estratos'),
 ('C','Exposición conjunta', 'Acuerdo entre actores solo ante coobservación expresada','Asumir no-voto como desacuerdo/acuerdo'),
 ('C','Comparador de marginales', 'Acuerdo esperado empírico por marginales de pares','Declarar afinidad por coincidencia bruta'),
 ('D','Logloss Poisson completo', 'Factorial y caso lambda=0 en pérdida propia','Ignorar constante y los ceros'),
 ('D','MAE de conteos', 'MAE válida solo sobre conteos y tasas finitas','Evaluar sin rango de dominio'),
 ('D','Skill baseline', 'No dividir por pérdida del baseline cero','Rival nulo deliberadamente débil'),
 ('D','Calibración por intervalos', 'Bin sin soporte no reporta tasa ficticia','Interpolar faltantes como acierto'),
 ('D','Walk-forward con embargo', 'Separación temporal train-gap-test sin solapes','Split aleatorio con fuga'),
 ('D','Bootstrap por sesión', 'Sesión como cluster, semilla fija','Pseudorreplicar votos intrasesión'),
 ('E','Fixture nominal determinista', 'Once registros reproducibles con IDs ficticios','Datos de políticos inventados presentados como reales'),
 ('E','Reporte con desconocidos', 'Censo de 3 oportunidades con no-voto y unknown separados','Dar cero por omisión de fila'),
 ('E','Reporte comparativo', 'Comparador de acuerdo observado y esperado con n conjunta','Etiquetar covoto como influencia'),
 ('E','Escala VSDS local', 'No subir de 1 por fixture; ciencia AB por separado','Equiparar demo con descubrimiento'),
 ('E','API readonly separada', '/api/lab retorna demo independiente del estado del fantasy','Unificar puntuación real y sintética'),
 ('E','Interfaz informativa', 'Mostrar advertencia y desconocidos; JS sintaxis válida','Ocultar limitación al usuario'),
]
assert len(contracts)==30
# pytest suite output separately collected and validated by caller
paths=sorted((ROOT/'tests').glob('test_*.py'))
all_src='\n'.join(x.read_text(encoding='utf-8') for x in paths)
from re import findall
found=set(findall(r'def\s+(test_br30_\d{2}_[A-Za-z0-9_]+)\s*\(',all_src))
assert len(found)==30,(len(found),found)
rows=[]
for j,(b,title,expect,rival) in enumerate(contracts,1):
    info=branches[b]
    names=[n for n in found if n.startswith('test_br30_'+f'{j:02d}'+'_')]
    assert len(names)==1,(j,names)
    test_name=names[0]
    test_file=ROOT/info[3];source_file=ROOT/info[4]
    assert test_name in test_file.read_text(encoding='utf-8')
    rows.append({
      'id':f'PF-B30-{j:02d}','parent':f'PF-B30-{j-1:02d}' if j>1 else 'PF-B50-08',
      'branch':info[0],'drift_distance':info[1],'kind':'PRODUCTION_AB_A_J',
      'status':'PRODUCTION_VERIFIED_LOCAL_NOT_CONFIRMATORY','prereg_committed_before_run':info[2],
      'prereg_type':'DESIGN_ONLY_GITHUB; CODE_NOT_FROZEN_BEFORE_TEST',
      'A':{'question':title,'estimand':'Correcto cumplimiento del invariante en datos sintéticos','population':'Fixtures sintéticas, no política española'},
      'B':{'claim':expect,'competent_rival':rival,'other':'Otros errores de implementación y de semántica no cubiertos por un test'},
      'C':{'test_protocol':'Test determinista de aceptación y caso negativo','falsification_rule':'Assertion o suite incompatible con criterio de aceptación','randomization':'NO para fixtures salvo bootstrap con semilla fija'},
      'D':{'test':test_name,'test_file':info[3],'source_file':info[4],
           'source_sha256':hashlib.sha256(source_file.read_bytes()).hexdigest(),
           'freeze_disclaimer':'Versión de código congelada mediante entrega final, no antes del ensayo'},
      'E':{'observed':'PASS_LOCAL_SYNTHETIC','evidence':'research/BRANCH30_20261025/QA_20261025.txt'},
      'F':{'adversarial_control':rival,'limitations':'Fixture diseñada por autores; alcance circunscrito al invariante'},
      'G':{'external_confirmation':'NOT_PERFORMED','independence':'Una suite de mismo equipo, no nuevo corpus'},
      'H':{'prior_update':'La instrumentación permite auditar este riesgo; no evidencia sobre distribución de votos reales.',
           'prior_type':'ENGINEERING_ONLY'},
      'I':{'engineering_value':'VSDS-1/3 LOCAL','AB_scientific_grade':'0/3 NO_REAL_DATA','CT2_predictive':24,
           'external_validity':'UNKNOWN','ethics':'No inferir virtud, influencia o ideología'},
      'J':{'decision':'CONTINUE_NEXT_BRANCH' if j in (6,12,18,24) else 'CONTINUE_PRODUCTION',
           'next_evidence':'Microdatos nominales certificados y pruebas de usuario reales'},
      'VSDS_grade':1,'AB_novelty_grade':0,'CT2_predictive_before':24,'CT2_predictive_after':24,
      'finding_counted_once':False})
ledger={'campaign':'Politics Fantasy League BRANCH30','date':'2026-10-25','authorised_block':30,
        'deduction':'PF-B50 42 remaining -> 12 remaining (this is not 30 EXTRA to backlog)',
        'research_mode':'PRODUCTION_AB_A_J','engineering_cycles_completed':30,
        'valid_empirical_causal_or_predictive_AB':0,'scientific_findings':{'N1':0,'N2':0,'N3':0},
        'VSDS_project_value':1,'CT2_predictive':24,'branches':[{'letter':k,'name':v[0],'prereg_commit':v[2]} for k,v in branches.items()],
        'failed_iteration':'PF-B30-13: initial test assertion mistakenly assumed margin 1/2; independently checked 2 YES vs 1 NO => 1/3, repaired expected value without changing formula, same cycle, not a new result',
        'prior_authorizations':{'PF_AB20_pending':19,'PF_F45_unused':45,'PF_B50_remaining_after':12},
        'source_certified':False,'external_confirmation':False,'cycles':rows}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'CYCLES_LEDGER.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('LEDGER:',len(rows),'entries; 5 frozen lot commits; statuses local engineering only')
