"""Format substantive A-J ledger from immutable *anonymized summary*.

This does not re-create institutional data, which remain in upstream Git blobs.
Does not confer scientific confirmation on source audits.
"""
from __future__ import annotations
from datetime import date
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'research' / 'BRANCH30E_20261025'
S = json.loads((DIR/'HISTORICAL_SUMMARY.json').read_text())
SRC = 'https://github.com/MarcoAnarmo/CongresoAbierto/blob/main/data/raw/votaciones/pleno.jsonl'
CUR = 'https://github.com/MarcoAnarmo/CongresoAbierto/blob/main/data/congreso/votaciones.json'
IMP = 'https://github.com/MarcoAnarmo/CongresoAbierto/blob/main/scripts/importar-votaciones.ts'
ORIG = 'https://www.congreso.es/es/opendata/votaciones'
cases = [
('Importador: orden de cómputo y resolución de identidades','Los totales se calculan antes de intentar emparejar nombres con catálogo vigente','El programa alteraría los agregados cuando falla el match','Revisar orden de cuenta[letra]++ y if(cod) de importar-votaciones.ts','El contador oficial se incrementa antes de if(cod); grupoDe y votos solo si cod existe','Rastro de implementación, no verificación de cada registro',IMP),
('Capacidad mecánica de producir huecos','Bajo proyección parcial de nombres se mantiene suma agregada pero disminuye número vinculado','No puede aparecer hueco si totales son correctos','Derivar identidad recuento_total = recuento_nominal + nombres_no_resueltos','Suma independiente de mapa actual; igualdad solo si todos resueltos','Identidad condicionada al mecanismo del programa, no explicación exclusiva',IMP),
('Descomposición de siete votaciones curadas','Diferencia agregados-nominal = 42 posiciones de votación','Un recuento distinto contradice la transcripción anterior','Sumar 4,0,4,4,4,8,18 y 21+16+0+5','42 posiciones; 21 YES, 16 NO, 0 ABSTAIN, 5 NO_VOTE','Muestra seleccionada, no población general',CUR),
('No votar no es no tener ID','NO_VOTE declarado y falta por catálogo son mecanismos distintos','Ambos son siempre equivalentes','Comparar NO_VOTE declarado (26) y huecos de ID (42) en siete votos','26 no-votos explícitos frente a 42 posiciones sin correspondencia','26 es total declarado explícito en siete ejemplos, no asistencia ni ausencia personal',CUR),
('RDL 8/2026: cotejo oficial agregado','La terna 166/177/5 coincide con ficha institucional de 28/04','Alguna categoría difiere','Comparación exacta mismo expediente 130/000039, misma fecha','166/177/5 coincide','No coteja nominal oficial ni fecha de primera publicación',ORIG),
('Alquiler temporada 2024: cotejo oficial','Terna 176/169/0 coincide con 17/12/2024','Alguna categoría difiere','Comparación exacta expediente 122/000136','176/169/0 coincide','No certifica lista nominal',ORIG),
('Pisos turísticos 2025: cotejo oficial','Terna 176/169/0 coincide con 07/10/2025','Alguna categoría difiere','Comparación por fecha y expediente 122/000214','176/169/0 coincide','No certifica lista nominal',ORIG),
('Ocupación 2026: cotejo oficial','Terna 171/164/11 coincide con 19/05/2026','Alguna categoría difiere','Comparación expediente 122/000254','171/164/11 coincide','No certifica lista nominal',ORIG),
('Vivienda Sumar septiembre: cotejo oficial','Terna 44/175/127 coincide con 15/09/2026','Alguna categoría difiere','Comparación expediente 122/000251','44/175/127 coincide','No certifica lista nominal',ORIG),
('Cotejo agregado y límites de identidad','Que coincidan los totales no demuestra correspondencia nominal completa','Totales permiten inferir lista de individuos sin ambigüedad','Buscar evidencia nominal independiente para los cinco casos','Ninguna de las cinco páginas agregadas resuelve los nombres ausentes','Concluir incertidumbre residual, no ausencia o error del Congreso',ORIG),
('Ámbito temporal del archivo de Pleno','Archivo revisado contiene 2175 votos 2023-09-19 a 2026-09-30','Otra cantidad o fechas lo contradicen','Contar JSONL tras sha y fechas ISO','2175 votos; 2023-09-19—2026-09-30','Universo de archivo secundario, no censo de votaciones secretas',SRC),
('Unicidad de votaciones','No hay IDs de votación duplicados en archivo','Existen colisiones de clave sesión+votación','Contar IDs distintos','2175 ids únicos para 2175 registros','No certifica completitud de sesiones',SRC),
('Conservación de capacidad de la Cámara','Ningún total supera 350; algunos son inferiores','Algún total > 350','Suma de cuatro categorías por fila','0 >350; 32 menores de 350','No equiparar total<350 a diputado ausente',SRC),
('Suma de votos de grupos históricos','Suma de 4 opciones por grupo igual a agregado cuando existe grupo','Existen grupos que no concilian','Reagregar 19561 grupo×voto','0 conflictos; 19561 registros de grupo','Derivados de mismo JSON del Congreso, no fuentes independientes',SRC),
('Magnitud de falta de vinculación nominal','34654 posiciones no están vinculadas o carecen de nominal','Todos los votos están nominalizados','761218 - 726564','34654 posiciones; incluye 700 de dos votos sin nominal','Denominador es posición-voto, no persona única',SRC),
('Diferencia por categoría en votos con nominal','Faltantes aparecen también en Sí y No, no solo No vota','Toda diferencia es NO_VOTE','Suma por S/N/A/X en 2173 votos','YES 14579; NO 15491; ABSTAIN 2841; NO_VOTE 1043','No deduce por qué persona concreta falta',SRC),
('Frecuencia de correspondencia completa','La mayoría de votaciones tiene mapeo nominal parcial','La mayoría es completa','Contar igualdades y déficits sobre 2173 votos con nominal','95 completas; 2078 parciales','Dependencia fuerte entre votos del mismo periodo',SRC),
('Tamaño por año','Distribución de votaciones y sesiones varía entre años','Volumen uniforme en años','Contar votos/sesiones por año','2023:32/5; 2024:862/52; 2025:741/50; 2026:540/37','2023 y 2026 no son años completos',SRC),
('Cobertura nominal por año','Proporción de IDs vinculados crece en año del evento','Es similar en 2023 y 2026','Dividir vinculados/posiciones por año','2023 85.830%; 2024 92.334%; 2025 96.824%; 2026 99.098%','Efecto esperado por catalogación retrospectiva y cobertura, no participación',SRC),
('Sensibilidad al clustering por sesión','Desigualdad 2026-2023 persiste al remuestrear sesiones','Diferencia desaparece al tratar sesiones como bloques','Bootstrap 1000 resamples de sesiones; LCG semilla 20261025','Intervalo de sensibilidad 12.42 a 15.72 puntos porcentuales','5 sesiones en 2023; NO intervalo inferencial de población aleatoria',SRC),
('Votos sin nominal','Existen registros con total pero sin mapa nominal','Todos son mapeados al menos parcialmente','Inspeccionar map S/N/A/X vacío','Dos votaciones sin nominal (2025-01-22 y 2026-09-30)','Posible forma de votación/procedimiento; no imputar 350 ausentes',SRC),
('No-votos declarados y temporalidad','Los no-votos explícitos cambian por periodo','Categoría NO_VOTE es residual de falta de ID','Contar totales.noVota por año','7973 explícitos total; por año 96/3760/2618/1499','No ausencias personales; sintaxis fuente preservada',SRC),
('Tamaño de grupo y denominadores','19561 filas grupo×voto; grupos de composición variable','Un grupo fijo y uniforme funciona en todos los periodos','Revisar 4 contadores por grupo y votos','19561 pares de grupo histórico y votación','No asumir disciplina de grupos por suma aritmética',SRC),
('Empates en opción modal','Los empates entre opciones expresadas deben registrarse','Nunca existen empates','Mayoría clara entre S/N/A, excluyendo X','36 pares grupo-voto con empate de opción expresada','Grupo Mixto heterogéneo',SRC),
('Concentración modal por grupo','La concentración es alta en conteos por grupo','Conteos internos se reparten homogéneamente','Suma maxima(S,N,A) / suma expresados por grupo','99.4525% de los votos expresados','Descriptivo de agregado, no métrica de obediencia ni causalidad',SRC),
('Ablación de grupo mixto y grupos pequeños','Cambiar universo analítico modifica concentración modal','Excluir grupos heterogéneos y pequeños no cambia indicador','Excluir GMx y grupos con <=5 votos totales','99.9185% concentración filtrada vs 99.4525% completa','Selección de universos impide comparar como efecto causal',SRC),
('Ponderación de votaciones frente a sesiones','Media de cobertura depende de unidad de agregación','Ambos estimadores son iguales','Cobertura ponderada por fila vs media igual por sesión','95.5354% por posición-voto vs 95.2753% media por sesión','No confundir unidades ni inferir significación',SRC),
('Sensibilidad a mitad temporal','Cobertura primera y segunda mitad difiere','Ambas mitades son idénticas','Dividir 2173 eventos nominalizados por orden temporal','92.7374% primera mitad vs 98.3307% segunda','Corte arbitrario, estudio exploratorio, efecto del propio matching',SRC),
('Identidades resolubles a lo largo del tiempo','Universo de IDs vinculados crece de 305 a 350 a lo largo de periodo','Cobertura de códigos igual desde el inicio','Unión de códigos por año sin publicarlos','305/332/343/350; unión total 350; 305 comunes 2023/2026','No representar composición efectiva histórica de la Cámara',SRC),
('Triangulación macro con otro observatorio','Fuentes publican recuentos no idénticos y no son comparables fila a fila sin emparejar','Cifras idénticas y definiciones sincronizadas','Comparar solo metadatos agregados publicados a 25/10/2026','CongresoAbierto 2175/726564/350 códigos; QuienVota 2176/761568/412 personas históricas','Diferencia 1 votación y 35004 votos reportados; no confirmar causas por falta de join', 'https://quienvota.org/')
]

if len(cases)!=30: raise RuntimeError(len(cases))
cycle_list=[]
for i,(title,hyp,null,method,result,limit,link) in enumerate(cases,1):
    source_research = i>=11
    verdict = 'POST_HOC_AUDIT' if i<=10 else 'SOURCE_AUDIT_EXPLORATORY'
    if i in (10,30): verdict='INCONCLUSIVE_SOURCE_SCOPE'
    act = 'REPAIR_SOURCE' if i in (1,2,3,4,10,15,16,17,19,20,21,28,29,30) else 'CONTINUE_AUDIT_NO_CAUSAL_CLAIM'
    cycle_list.append({
        'id':f'PF_AB30E_C{i:02d}', 'parent':'PFL-BR30E', 'type':verdict,
        'prereg_git': 'ea1cb76df82e67c44c0e25c2c1f6b9732e3a5f32' if i<=10 else 'db28924d3fac80fe635f7baeece013372bc94488',
        'research_title':title,
        'A':{'estimand':title, 'unit': 'vote, group-vote or source definition as indicated',
             'population':'source-selected 7 votes' if i<=10 else '2175 historical votes in one secondary file',
             'field_data_provenance':'secondary public parliamentary-source reconstruction, not direct independent official nominal certification',
             'outcome_truth':'source-measured counts; original official JSON must be compared separately'},
        'B':{'preferred':hyp,'null_or_rival':null,'H_otras':'schema drift; catalog censoring; delayed publication; editorial selection'},
        'C':{'design':method,'falsifier':null,'budget':'one source audit, no repeated optional testing; no confirmatory p-value',
             'preselection':'publicly known seven votes' if i<=10 else 'fixed upstream history; first coarse counts exposed before B freeze'},
        'D':{'instrument':'GitHub blob-locked source count; independent aggregation/check where possible; test suite',
             'source_git_blob':'71918bb689c7a62cfbbdafe0b9248eac6b5c4be1' if i>=11 else 'ecaf3b02b9a453265d6bcb588a9121ddaae9ed78',
             'code_freeze':'a309b5d58f2f2b6e5b113be8409be947c3a4d6b6' if i>=11 else 'upstream source code hash 2a9d63c7b247cf6ad2a74b03e9c4afd2a6bfa47e'},
        'E':{'observed':result,'status':'EXECUTED_DESCRIPTIVE_SOURCE_AUDIT','data_source':link},
        'F':{'adversarial_audit':limit, 'strongest_rival':null, 'control_result':'checks against alternative category / denominator; does not remove source dependence',
             'selection_exposure':'posthoc' if i<=10 else 'source-exposed exploratory after preliminary read'},
        'G':{'independent_external_replication':'NOT_AVAILABLE','reason':'public secondary transformations and official aggregates do not independently verify individual historical identities'},
        'H':{'prior_update':'Source coverage / roster history remains an evidence bottleneck; mechanistic explanation strengthens only instrument inference, not causality',
             'no_posterior_numeric_due_to_selection':True,'next_discriminating_evidence':'original official nominal JSON and rosters by date; independent join'},
        'I':{'internal_validity':'descriptive arithmetic/code inspection within frozen blob', 'external_validity':'NOT_ESTABLISHED',
             'causal_identification':'NONE','scientific_originality':'NOT_CLAIMED','value_for_sociology':'audit observability; avoid false participation/rankings',
             'ethics':'no individual identity rows copied into report','limitations':limit},
        'J':{'decision':act,'reason':'next meaningful evidence must be independent nominal/roster source; R5 prevents redundant resampling',
             'VSDS_project_after':'1/3','CT2_predictive_after':24,'AB_grade':'0/3 (no novel external confirmation)'},
    })
result={'campaign':'PFL-BR30E','authorized':30,'full_A_to_J_documented':30,
        'source_audits_not_independent_experiments':30,'empirical_causal_experiments':0,'independent_nominal_confirmations':0,
        'source_data':'public secondary curated and 2175-vote file',
        'status':'DESCRIPTIVE_POSTHOC_OR_SOURCE_EXPOSED',
        'levels':{'VSDS':1,'CT2_predictive':24,'AB_2_of_3':0},'cycles':cycle_list}
(DIR/'CYCLES_AJ.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('wrote 30 A-J observational cycles')
