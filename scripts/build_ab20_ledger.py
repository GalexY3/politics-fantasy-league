"""Generate auditable PF-AB20 campaign metadata; no results synthesized for C02-C20."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json

root = Path(__file__).resolve().parents[1]
base = root/'research'/'AB20_REALES_20261024'
proposals = [
  ('C02','JSON-vs-HTML','Desacuerdo entre recuentos web y payload nominal','Mismo voto; comparación de conteos', 'Parear ID de votación y comprobar total/semántica/actualización','Diferencia no nula tras resolver identidad; invalidar transcripción'),
  ('C03','Bitemporalidad','Inferencia errónea de disponibilidad retroactiva','Instante observable vs instante de evento','Primeras capturas independientes/archivadas; auditoría del retraso','No existe timestamp independiente de primera publicación'),
  ('C04','Cobertura longitudinal','Periodos aparentemente vacíos por ausencia de ingesta','Sesión programada vs sesión registrada','Contrastar calendario y sesiones publicadas por trimestre','Fuente oficial carece de censo de sesiones confiable'),
  ('C05','Cambios de identidad','Nombres duplicados/variantes llevan a atribución incorrecta','Actor institucional con ID duradero','Enlace nominal persona-voto basado en ID y supervisión de cambios','Colisiones o traslados de cargo no resueltos'),
  ('C06','Mandatos y grupos','Afiliación retrospectiva induce fuga del futuro','Membresía a fecha de corte','Reconstruir ventanas de adscripción, comparación estática/temporal','No puede fecharse cambio o hay conflictos sin resolver'),
  ('C07','Eventos e iniciativas','Falsa independencia entre votaciones de la misma iniciativa','Dependencia intraexpediente','Agrupación por expediente y contraste de errores agrupados','No se logra id único de expediente-votación'),
  ('C08','Elegibilidad','Recuentos sin exposición inflan actividad de cargos','Personas-sem. elegibles','Auditar universo elegible con calendario y mandatos','Sesgo sistemático de no-observación según cargo'),
  ('C09','Baselines','Un modelo de media histórica es rival competente','Persona-semana, pérdida de Poisson','Modelo persistencia/tasa por cargo con cortes cronológicos','Cobertura demasiado pequeña para holdout'),
  ('C10','Heterogeneidad','Dispersión no Poisson por posición y agenda','Varianza condicional y log-score','Comparar Poisson y NB con misma covariación','Ventaja desaparece con folds/intervalos'),
  ('C11','Estructura temporal','Calendario explica actividad mejor que reputación','Efecto predictivo de calendario conocido','Ablación calendario conocido antes del corte','Calendario construido con futuro'),
  ('C12','Jerarquía','Pooling parcial generaliza mejor para actividad escasa','Riesgo para actores poco observados','NB/Poisson jerárquicos frente a modelos independientes','No mejora en nuevos actores/folds'),
  ('C13','Modelos de secuencia','Autocorrelación varía según temporalidad legislativa','Error por horizonte','Benchmark lag/event history y modelo temporal','No mejora frente a baseline simple'),
  ('C14','Validación de fuentes','Resúmenes tercerizados difieren de material oficial','Contaminación cruzada de fuentes','Revisar selección doble ciego y discordancia','Fuentes no comparables o licencias incompatibles'),
  ('C15','Fuga temporal','Backfills alteran artificialmente el forecast','Riesgo prequential','Comparación as-known vs final-record, con reglas congeladas','No se puede medir as-known verdadero'),
  ('C16','Grafo institucional','Centralidad aporta predicción incremental','Delta log-loss relacional-baseline','Red sólo con información previa, igual presupuesto y fuentes','Mejora nula o negativa con holdout'),
  ('C17','Control grafo','Mejora atribuible solo a tamaño/roles','Valor de topología verdadera vs nula','Permutar enlaces preservando grado/cargos','Grafo real no supera control aleatorizado'),
  ('C18','Variación de régimen','Inestabilidad de predicción entre etapas legislativas','Transportabilidad temporal','Evaluación por tramos y test posterior protegido','Ventaja es específica del periodo explorado'),
  ('C19','Equidad scoring','Puntos de actividad dependen de cargo/exposición','Brecha de puntuación condicionada','Reponderación por oportunidad vs reglas base','Pérdida de auditabilidad o sesgo nuevo'),
  ('C20','Simulación versus política','ABM aparenta descubrimiento por supuesto impuesto','Efecto del mecanismo en mundo simulado','Ablación incentivo/estructura y baseline probabilístico','El patrón desaparece al retirar regla generadora')
]
rows=[{'cycle_id':'C01','branch':'B1','short_title':'Auditoría de recuentos oficiales agregados',
       'status':'EXPLORATORY_OBSERVATIONAL_PILOT_INCOMPLETE_FREEZE','data_status':'20 manually transcribed vote tallies / one official session',
       'evidence':'RESULT_C01.json','grade_0_3':0,'ct2_before':24,'ct2_after':24,'decision':'REPAIR_ACCESS_AND_FREEZE',
       'not_validated_reason':'No official raw HTML bytes, no independently confirmed payload, no prereg GitHub/code freeze, no as-known publication timestamp.'}]
for cid,theme,title,unit,design,falsifier in proposals:
 rows.append({'cycle_id':cid,'branch':'ADAPTIVE_NOT_FINAL','short_title':title,'theme':theme,
             'prospective_unit_or_estimand':unit, 'prospective_discriminant':design,
             'prospective_falsifier':falsifier,'status':'NOT_EXECUTED','data_status':'NEED_VERIFIED_SOURCE',
             'grade_0_3':None,'ct2_before':None,'ct2_after':None,'decision':'NOT_MADE',
             'prereg_commit':None,'result_commit':None,
             'note':'Candidate only; may be adapted/abandoned following evidence. NOT a completed A-J cycle or committed prereg.'})
assert len(rows)==20 and len({x['cycle_id'] for x in rows})==20
(base/'CYCLES_LEDGER.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
prereg=base/'PREREG_C01.md'
result=base/'RESULT_C01.json'
content={
  'campaign_id':'PF-AB20-20261024', 'method':'AB3.2.1/O1-O6',
  'authorized_by_user':20,
  'cycle_slots':20,'pilot_work_items_completed':1,'ab_cycles_confirmatory_valid':0,
  'scientifically_executed_status':'C01 exploratory observational incomplete freeze; C02-C20 unexecuted',
  'pending_or_unexecuted':19,'grant_unspent_pending':19,
  'source_real_observational_transcriptions':20,
  'institutional_raw_bytes_downloaded':0,
  'github_committed':False, 'github_write_status':'PREVIOUS_403_FORBIDDEN',
  'source_last_update_verified':False,'bitemporal_history_verified':False,
  'nominal_personal_observations':0,'independent_external_confirmations':0,
  'ct2_trajectory':{'branch':'B3','begin':24,'after_C01':24,'scale':'ordinal; no P(discovery)'},
  'N1_new':0,'N2':0,'N3':0, 'grade_2_3_accredited':False,
  'prereg_local_sha256':sha256(prereg.read_bytes()).hexdigest(),
  'result_sha256':sha256(result.read_bytes()).hexdigest(),
  'status':'REPAIR_BARRIER_ACCESS_AND_PROVENANCE',
  'next_required_evidence':'Official nominal XML/JSON body with schema + as-known first-availability / original revision; permissions to freeze design in repo',
  'license_and_reuse':'Congress legal notice verified; source last update unknown, distribution and attribution review unfinished',
  'created_date':'2026-10-24'
}
(base/'campaign.json').write_text(json.dumps(content,indent=2,ensure_ascii=False)+'\n')
lines=['# C02–C20 — reservas de ciclo; NO experimentos ejecutados','',
       'El bloque está **autorizado**, pero cada entrada es un **candidato** condicionado a adquisición e inspección lícita de microdatos con procedencia. Ningún candidato siguiente tiene aún preregistro A–J congelado, ni ejecución E, ni confirmación G. R5 permite parar; el branching exigirá evidencia disparadora antes de formular la prueba definitiva.','']
for (cid,theme,title,unit,design,falsifier) in proposals:
 lines += [f'## {cid} · {theme}: {title}',
           f'- A **unidad/estimando propuesto**: {unit}.',
           f'- B **rivales**: hipótesis estructural vs baseline parsimonioso y error de medición/selección.',
           f'- C **prueba candidata**: {design}.',
           f'- D **instrumentación**: exige raw oficial, ids estables, corte de publicación e integridad de hash, con congelación previa en GitHub.',
           f'- E **ejecución**: **NOT_EXECUTED**.',
           f'- F **auditoría adversarial**: {falsifier}.',
           f'- G **confirmación**: no disponible; requerirá datos/folds independientes de selección.',
           f'- H **prior**: NO_UPDATED, a la espera de evidencia.',
           f'- I **dictamen**: NOT_ASSESSED; CT2 no puntuado.',
           f'- J **decisión**: NOT_MADE; decidir después de ciclo precedente.', '']
(base/'C02_C20_BACKLOG.md').write_text('\n'.join(lines)+'\n')
print('created',base/'campaign.json',base/'C02_C20_BACKLOG.md',len(rows))