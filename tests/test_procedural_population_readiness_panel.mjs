import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const js=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const fn=js.match(/function populationReadinessPanel\(\)\{[\s\S]*?\n\}/);
assert.ok(fn,'Readiness rendering function must be present');
const esc=s=>String(s??'').replace(/[&<>"']/g,
 c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function render(readiness){
 return runInNewContext(fn[0]+'\npopulationReadinessPanel',{
  ui:{populationReadiness:readiness},esc,count:n=>String(n)
 })();
}
const sample=()=>({
 schema:'pfl.spanish_procedural_population_readiness.v1',
 reusable_scientific_cohort:false,
 risk_set_denominator:null,
 institutional_sources:[
  {institution:'Parlamento de Canarias',unit:'CURRENT_CAPTURE_SOURCE_LOCAL_INITIATIVE_ID',observed_metadata_rows:1754,provenance_status:'AUDITED_METADATA_CURRENT_CAPTURE'},
  {institution:'Parlament de Catalunya',unit:'SOURCE_INDEX_PAGE_LINK_NOT_ENTRY_EVENT',observed_metadata_rows:20,provenance_status:'ONE_INDEX_PAGE_OF_UNCERTIFIED_POPULATION'},
  {institution:'Congreso de los Diputados',unit:'WEB_DISCOVERY_ONLY_NO_ADMITTED_ORIGINAL',observed_metadata_rows:null,provenance_status:'DISCOVERY_NOT_ORIGINAL_CAPTURE'},
 ],
 coverage_gates:[
  {gate:'INDEPENDENT_ENTRY_REGISTRY_DENOMINATOR',scientific_admission:'NOT_ATTESTED'},
  {gate:'DATED_DOCUMENTED_TRANSITIONS',scientific_admission:'NOT_ATTESTED'},
 ]
});

test('renders three disjoint sources and all unpassed gates without summing cases',()=>{
 const html=render(sample());
 assert.match(html,/1754/);
 assert.match(html,/20/);
 assert.match(html,/Congreso de los Diputados/);
 assert.match(html,/Desconocido/);
 assert.match(html,/INDEPENDENT_ENTRY_REGISTRY_DENOMINATOR/);
 assert.match(html,/no deben sumarse/);
 assert.match(html,/Denominador de riesgo desconocido/);
 assert.doesNotMatch(html,/1774.*(expedientes|personas)|casos aprobados/);
});

test('unavailable coverage is not replaced with invented denominators',()=>{
 const html=render({schema:'other',institutional_sources:[{observed_metadata_rows:99999}]});
 assert.match(html,/No se dispone de un informe de procedencia admisible/);
 assert.doesNotMatch(html,/99999/);
});

test('source names and misleading fields cannot inject HTML',()=>{
 const data=sample();
 data.institutional_sources[0].institution='<img src=x onerror=alert(1)>';
 data.coverage_gates[0].scientific_admission='<script>alert(1)</script>';
 const html=render(data);
 assert.match(html,/&lt;img/);
 assert.match(html,/&lt;script/);
 assert.doesNotMatch(html,/<img|<script/);
});

test('new documentary candidates are explicitly displayed as blocked and non-censal',()=>{
 const data=sample();
 data.documentary_candidate_status='DOCUMENTARY_CANDIDATES_BLOCKED_FROM_SOURCE_ADMISSION';
 data.documentary_candidate_sources=[
  {institution:'Asamblea de Madrid',catalogue_asset:'ExpedientesAsambleaMadrid',access_gate:'TERMS_ACCEPTED_BY_USE_NOT_AUTHORIZED_FOR_AUTOMATED_ORIGINAL_GET'},
  {institution:'Centro de Estudios Políticos y Constitucionales',catalogue_asset:'INICPAR',access_gate:'ALL_RIGHTS_RESERVED_NO_BULK_DATASET_REUSE_ATTESTED'},
 ];
 const html=render(data);
 assert.match(html,/ExpedientesAsambleaMadrid/);
 assert.match(html,/INICPAR/);
 assert.match(html,/No se han aceptado sus términos/);
 assert.match(html,/no es una población de entradas/);
 assert.doesNotMatch(html,/censo completo verificado/);
});

test('candidate source text cannot inject active markup',()=>{
 const data=sample();
 data.documentary_candidate_status='DOCUMENTARY_CANDIDATES_BLOCKED_FROM_SOURCE_ADMISSION';
 data.documentary_candidate_sources=[
  {institution:'<img src=x onerror=alert(1)>',catalogue_asset:'<script>alert(1)</script>',access_gate:'UNKNOWN'},
 ];
 const html=render(data);
 assert.match(html,/&lt;img/);
 assert.match(html,/&lt;script/);
 assert.doesNotMatch(html,/<img|<script/);
});

test('methodology panel explains unidentifiable selection rather than zero outcomes',()=>{
 const data=sample();
 data.linkage_and_identification={
   event_by_cut_status:'NOT_IDENTIFIABLE_ON_CURRENT_REAL_SOURCES',
   register_to_expediente:'NOT_ATTESTED_WITH_OFFICIAL_DUAL_ID_AND_RAW_RECEIPT'
 };
 const html=render(data);
 assert.match(html,/Identificabilidad de entradas y sesgo de selección/);
 assert.match(html,/no se consideran inadmitidos/);
 assert.match(html,/exclusivamente sintéticas/);
 assert.doesNotMatch(html,/éxito 0%|rechazadas 0/);
});

test('linkage text is escaped to prevent HTML injection',()=>{
 const data=sample();
 data.linkage_and_identification={
  event_by_cut_status:'NOT_IDENTIFIABLE_ON_CURRENT_REAL_SOURCES',
  register_to_expediente:'<img src=x onerror=alert(1)>'
 };
 const html=render(data);
 assert.match(html,/&lt;img/);
 assert.doesNotMatch(html,/<img/);
});

test('R8 separated documentary regions and advisory consultations cannot become case totals',()=>{
 const data=sample();
 data.r8_documentary_status='R8_DOCUMENTARY_ONLY_NO_SOURCE_ADMISSION';
 data.r8_audit_safe_by='2026-11-01T00:00:00+00:00';
 data.r8_regional_routes=[{institution:'Parlament de les Illes Balears',asset:'WebGTP manual',limitation:'Only previously processed entries'}];
 data.r8_national_core_routes=[{institution:'Consejo de Estado',unit:'YEARLY_PUBLICATION_INDEX',limitation:'Historical annual report only'}];
 const html=render(data);
 assert.match(html,/R8 · nuevas fuentes regionales/);
 assert.match(html,/Parlament de les Illes Balears/);
 assert.match(html,/Consejo de Estado/);
 assert.match(html,/una población distinta/);
 assert.doesNotMatch(html,/2027 consultas/);
});

test('R8 hides blocked unrecognized source state and escapes names',()=>{
 const data=sample();
 data.r8_documentary_status='R8_DOCUMENTARY_ONLY_NO_SOURCE_ADMISSION';
 data.r8_regional_routes=[{institution:'<svg onload=alert(1)>',asset:'<img src=x>',limitation:'<script>alert(1)</script>'}];
 data.r8_national_core_routes=[];
 const html=render(data);
 assert.match(html,/&lt;svg/);
 assert.match(html,/&lt;script/);
 assert.doesNotMatch(html,/<svg|<script|<img/);
 data.r8_documentary_status='R8_NOT_KNOWN_AT_CUT';
 assert.doesNotMatch(render(data),/&lt;svg/);
});

test('R9 source integrity audit is shown only as prior byte validation, not institutional census',()=>{
 const data=sample();
 data.retained_original_integrity={
   status:'PAST_LOCAL_BINARY_INTEGRITY_CONFIRMED',
   official_originals_byte_checked:5,
   private_derivatives_byte_checked:2,
   local_audit_safe_by:'2026-10-31T07:08:42+00:00'
 };
 const html=render(data);
 assert.match(html,/R9 · integridad de originales/);
 assert.match(html,/5 originales capturados y 2 derivados privados/);
 assert.match(html,/NO acredita censo completo/);
 assert.match(html,/no una monitorización permanente/);
});

test('R9 does not reveal future counts or injection in receipt clock',()=>{
 const data=sample();
 data.retained_original_integrity={
  status:'INTEGRITY_AUDIT_NOT_KNOWN_AT_CUT',official_originals_byte_checked:null,
  private_derivatives_byte_checked:null,local_audit_safe_by:null
 };
 assert.doesNotMatch(render(data),/R9 · integridad de originales/);
 data.retained_original_integrity.status='PAST_LOCAL_BINARY_INTEGRITY_CONFIRMED';
 data.retained_original_integrity.official_originals_byte_checked=5;
 data.retained_original_integrity.private_derivatives_byte_checked=2;
 data.retained_original_integrity.local_audit_safe_by='<img src=x onerror=alert(1)>';
 const html=render(data);
 assert.match(html,/&lt;img/);
 assert.doesNotMatch(html,/<img/);
});

test('R9 documentary highlights distinguish units and prereg outcome exposure',()=>{
 const data=sample();
 data.r9_documentary_status='R9_DISCOVERY_ONLY_RIGHTS_AND_DENOMINATORS_BLOCKED';
 data.r9_documentary_safe_by='2026-11-01T00:00:00+00:00';
 data.r9_regional_highlights=[{institution:'Parlamento de Galicia',documentary_limit:'CONTRADICTORY_EDITORIAL_HEADING_AND_ENNUMERATION'}];
 data.r9_national_highlights=[{institution:'TRIBUNAL_CONSTITUCIONAL',documentary_unit:'TC_INITIAL_PROCEDURAL_DOCUMENTS_RECEIVED'}];
 const html=render(data);
 assert.match(html,/R9 · Galicia/);
 assert.match(html,/TRIBUNAL_CONSTITUCIONAL/);
 assert.match(html,/quedaría contaminada/);
 assert.match(html,/Sin identificación causal/);
 assert.doesNotMatch(html,/9155|9160|PPLI-000/);
});

test('R9 hidden at earlier cut, and escaped if source string malicious',()=>{
 const data=sample();
 data.r9_documentary_status='R9_DISCOVERY_NOT_KNOWN_AT_CUT';
 data.r9_regional_highlights=[{institution:'SENSITIVE',documentary_limit:'MORE'}];
 assert.doesNotMatch(render(data),/SENSITIVE/);
 data.r9_documentary_status='R9_DISCOVERY_ONLY_RIGHTS_AND_DENOMINATORS_BLOCKED';
 data.r9_documentary_safe_by='2026-11-01T00:00:00Z';
 data.r9_regional_highlights=[{institution:'<svg onload=alert(1)>',documentary_limit:'<script>alert(1)</script>'}];
 const html=render(data);
 assert.match(html,/&lt;svg/);
 assert.match(html,/&lt;script/);
 assert.doesNotMatch(html,/<svg|<script/);
});

test('R10 denominators show source local counts but never invent pending or censor counts',()=>{
 const data=sample();
 data.denominator_evidence={
  schema:'pfl.denominator_evidence_nonadditive.v1',
  eligible_risk_denominator:null,
  reported_sources:[
   {institution:'Parlamento de Canarias',observable_unit:'SOURCE_LOCAL',
    observed_source_local_items:1754,principal_identification_block:'NO_INDEPENDENT_ALL_RECEIVED_FRAME'},
   {institution:'TRIBUNAL_CONSTITUCIONAL',observable_unit:'REGISTRY_INITIAL_WRITING',
    observed_source_local_items:null,principal_identification_block:'INCOMPATIBLE_GRANULARITY'}
  ]
 };
 const html=render(data);
 assert.match(html,/R10 · comparación de denominadores/);
 assert.match(html,/1754/);
 assert.match(html,/REGISTRY_INITIAL_WRITING/);
 assert.match(html,/Censurados: desconocidos/);
 assert.match(html,/N independiente: desconocido/);
 assert.doesNotMatch(html,/1774 casos|5 rechazos|0 pendientes/);
});

test('R10 no table without trusted source shape; supplied labels escaped',()=>{
 const data=sample();
 data.denominator_evidence={schema:'other',reported_sources:[{institution:'SECRET'}]};
 assert.doesNotMatch(render(data),/SECRET/);
 data.denominator_evidence={
  schema:'pfl.denominator_evidence_nonadditive.v1',
  reported_sources:[{institution:'<img src=x onerror=alert(1)>',
   observable_unit:'<script>bad()</script>',observed_source_local_items:null,
   principal_identification_block:'NO_RIGHTS'}]
 };
 const html=render(data);
 assert.match(html,/&lt;img/);
 assert.match(html,/&lt;script/);
 assert.doesNotMatch(html,/<img|<script/);
});

test('R10 official documentary routes present stage selection, not a political change estimate',()=>{
 const data=sample();
 data.r10_documentary_status='R10_DOCUMENTARY_ONLY_NO_RISK_FRAME';
 data.r10_asof_safe_by='2026-11-01T00:00:00+00:00';
 data.r10_regional_highlights=[
  {source_id:'andalucia_ilpa_xii_jea',institution:'Junta Electoral de Andalucía',
   scope_failure:'POST_MESA_REFERRED_ONLY_NOT_ALL_RECEIVED'},
  {source_id:'castilla_y_leon_xi_dissolution_feb2026',institution:'Cortes de Castilla y León',
   scope_failure:'PENDING_AT_DISSOLUTION_IS_SURVIVOR_SELECTED_STOCK'}];
 data.r10_national_highlights=[
  {institution:'Consejo de Transparencia y Buen Gobierno',entry_unit:'RECLAMACION_RECIBIDA',
   scope_failure:'APPEALS_RECEIVED_DISTINCT_FROM_RESOLUTIONS_AND_INITIAL_REQUESTS'}];
 const html=render(data);
 assert.match(html,/R10 · fases ILP/);
 assert.match(html,/Junta Electoral de Andalucía/);
 assert.match(html,/POST_MESA_REFERRED_ONLY_NOT_ALL_RECEIVED/);
 assert.match(html,/una fotografía seleccionada de supervivientes/);
 assert.match(html,/riesgo de medición, no un efecto político demostrado/);
 assert.match(html,/resolución no necesariamente equivale a reclamación/);
});

test('R10 future documentary names are hidden; source strings escaped',()=>{
 const data=sample();
 data.r10_documentary_status='R10_DOCUMENTARY_NOT_KNOWN_AT_CUT';
 data.r10_regional_highlights=[{institution:'FUTURE_ANDALUCIA',source_id:'hi',scope_failure:'foo'}];
 assert.doesNotMatch(render(data),/FUTURE_ANDALUCIA/);
 data.r10_documentary_status='R10_DOCUMENTARY_ONLY_NO_RISK_FRAME';
 data.r10_asof_safe_by='<svg onload=alert(1)>';
 data.r10_regional_highlights=[{
  institution:'<img src=x onerror=alert(1)>',
  source_id:'source',scope_failure:'<script>danger()</script>'}];
 data.r10_national_highlights=[];
 const html=render(data);
 assert.match(html,/&lt;img/);
 assert.match(html,/&lt;script/);
 assert.match(html,/&lt;svg/);
 assert.doesNotMatch(html,/<img|<script|<svg/);
});

test('R11 source-scoped audit links point to local JSON and do not allow unsafe IDs',()=>{
 const data=sample();
 data.denominator_evidence={schema:'pfl.denominator_evidence_nonadditive.v1',reported_sources:[
  {source_id:'PARCAN_SOURCE_LOCAL',institution:'Canarias',observable_unit:'METADATA',
   observed_source_local_items:1754,principal_identification_block:'NOT_CENSUS'},
  {source_id:'X&source_id=Y',institution:'Unsafe',observable_unit:'OTHER',
   observed_source_local_items:null,principal_identification_block:'UNVERIFIED'}
 ]};
 const html=render(data);
 assert.match(html,/api\/denominator-evidence\?source_id=PARCAN_SOURCE_LOCAL/);
 assert.match(html,/Fuente verificable/);
 assert.match(html,/Identificador no disponible/);
 assert.doesNotMatch(html,/href="[^"]*source_id=X&amp;/);
});

test('R11 source discovery separates Madrid AIP from economic and rights restrictions',()=>{
 const data=sample();
 data.r11_documentary_status='R11_DOCUMENTARY_RIGHTS_AND_RISK_FRAME_BLOCKED';
 data.r11_documentary_safe_by='2026-11-01T00:00:00+00:00';
 data.r11_documentary_routes=[
  {institution:'Ayuntamiento de Madrid',institutional_entry_unit:'FORMAL_ACCESS_REQUEST_CASE',
   classification:'ALL_RECEIVED_CLAIM_NOT_INDEPENDENTLY_RECONCILED',
   rights_gate:'CC_BY_4_CATALOGUE_WITH_BINDING_PORTAL_TERMS'},
  {institution:'Ministerio de Hacienda',institutional_entry_unit:'PUBLIC_TENDER_REVISION',
   classification:'REPEATED_ATOM_VERSIONS_AND_2026_COVERAGE_OUTAGE',
   rights_gate:'MINISTRY_REUSE_TERMS_BY_USE'}
 ];
 const html=render(data);
 assert.match(html,/R11 · registros municipales/);
 assert.match(html,/FORMAL_ACCESS_REQUEST_CASE/);
 assert.match(html,/REPEATED_ATOM_VERSIONS_AND_2026_COVERAGE_OUTAGE/);
 assert.match(html,/las condiciones generales vinculan por mero uso/);
 assert.match(html,/sin outcomes examinados, sin first_public_at/);
});

test('R11 hidden before source time and malicious names cannot execute HTML',()=>{
 const data=sample();
 data.r11_documentary_status='R11_DOCUMENTARY_NOT_KNOWN_AT_CUT';
 data.r11_documentary_routes=[{institution:'FUTURE_MADRID'}];
 assert.doesNotMatch(render(data),/FUTURE_MADRID/);
 data.r11_documentary_status='R11_DOCUMENTARY_RIGHTS_AND_RISK_FRAME_BLOCKED';
 data.r11_documentary_safe_by='<svg onload=alert(1)>';
 data.r11_documentary_routes=[
  {institution:'<img src=x onerror=alert(1)>',
   institutional_entry_unit:'<script>x()</script>',
   classification:'UNVERIFIED',rights_gate:'LEGAL_LIMIT'}
 ];
 const html=render(data);
 assert.match(html,/&lt;svg/);
 assert.match(html,/&lt;img/);
 assert.match(html,/&lt;script/);
 assert.doesNotMatch(html,/<svg|<img|<script/);
});

test('R12 normative planned output and administrative appeals are not the same at-risk cohort',()=>{
 const data=sample();
 data.r12_documentary_status='R12_DOCUMENTARY_ONLY_NO_ADMISSIBLE_POPULATION';
 data.r12_documentary_safe_by='2026-11-01T00:00:00+00:00';
 data.r12_documentary_routes=[
  {source_id:'AGE_PAN_2026',documentary_unit:'PLANNED_NORMATIVE_INSTRUMENT',
   risk_frame_limitation:'YEAR_AGENDA_NOT_ALL_SUBMITTED_CONSULTATIONS',
   specific_rights_scope:'GENERAL_REUSE_CONDITIONS_NO_ASSET_RIGHTS_CERTIFICATION'},
  {source_id:'TARCJA_PUBLIC_RESOLUTIONS',documentary_unit:'PUBLISHED_APPEALS_DECISION',
   risk_frame_limitation:'OUTCOME_SELECTED_CSV_NOT_REGISTERED_APPEAL_DENOMINATOR',
   specific_rights_scope:'CC_BY_4_CSV_ONLY_NOT_EDITORIAL_REPORT_OR_FILINGS'}
 ];
 const html=render(data);
 assert.match(html,/R12 · producción normativa y recursos/);
 assert.match(html,/YEAR_AGENDA_NOT_ALL_SUBMITTED_CONSULTATIONS/);
 assert.match(html,/OUTCOME_SELECTED_CSV_NOT_REGISTERED_APPEAL_DENOMINATOR/);
 assert.match(html,/recurso presentado y la resolución publicada no tienen correspondencia uno a uno/);
 assert.match(html,/primera disponibilidad pública acreditada NO son equivalentes/);
});

test('R12 future metadata not shown; potentially malicious source fields escaped',()=>{
 const data=sample();
 data.r12_documentary_status='R12_NOT_KNOWN_AT_CUT';
 data.r12_documentary_routes=[{source_id:'FUTURE_TARCJA'}];
 assert.doesNotMatch(render(data),/FUTURE_TARCJA/);
 data.r12_documentary_status='R12_DOCUMENTARY_ONLY_NO_ADMISSIBLE_POPULATION';
 data.r12_documentary_safe_by='<img src=x onerror=alert(1)>';
 data.r12_documentary_routes=[
  {source_id:'<svg onload=alert(1)>',
   documentary_unit:'<script>mal()</script>',
   risk_frame_limitation:'UNVERIFIED',specific_rights_scope:'LICENSE_UNKNOWN'}
 ];
 const html=render(data);
 assert.match(html,/&lt;svg/);
 assert.match(html,/&lt;script/);
 assert.match(html,/&lt;img/);
 assert.doesNotMatch(html,/<svg|<script|<img/);
});

test('R13 senate 870 reports 871 and GAIP final resolution are not denominators',()=>{
 const data=sample();
 data.r13_documentary_status='R13_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED';
 data.r13_documentary_safe_by='2026-11-01T00:00:00+00:00';
 data.r13_documentary_sources=[
  {source_id:'SENATE_PETITIONS_PERIODIC_REPORTS',unit:'COMMISSION_PERIOD_REPORT_871',
   identification_limit:'ADMITTED_DICTAMENS_AND_REPORTS_NOT_PRECLASSIFICATION_SEATS',
   rights_gate:'GENERAL_NOTICE_CANNOT_LICENSE_PETITION_REGISTER'},
  {source_id:'GENCAT_SAIP_INITIAL_FILINGS',unit:'INITIAL_REQUEST_FOR_ACCESS_TO_INFORMATION',
   identification_limit:'GENCAT_ADMINISTRATION_ONLY_NOT_ALL_GAIP_APPEALS',
   rights_gate:'GENERAL_LICENSE_BY_ACCESS_DISTRIBUTION_RIGHTS_UNCONFIRMED'}
 ];
 const html=render(data);
 assert.match(html,/R13 · peticiones Senado/);
 assert.match(html,/COMMISSION_PERIOD_REPORT_871/);
 assert.match(html,/GENCAT_ADMINISTRATION_ONLY_NOT_ALL_GAIP_APPEALS/);
 assert.match(html,/NO hay dos originales capturados legalmente y comparados/);
 assert.match(html,/sin testigo positivo contemporáneo pendiente significa desconocido/);
});

test('R13 before archive cut hides sources and returned strings are escaped',()=>{
 const data=sample();
 data.r13_documentary_status='R13_NOT_KNOWN_AT_CUT';
 data.r13_documentary_sources=[{source_id:'FUTURE_SENATE'}];
 assert.doesNotMatch(render(data),/FUTURE_SENATE/);
 data.r13_documentary_status='R13_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED';
 data.r13_documentary_safe_by='<svg onload=alert(1)>';
 data.r13_documentary_sources=[{
  source_id:'<img onerror=alert(1)>',
  unit:'<script>bad()</script>',
  identification_limit:'INCOMPLETE',rights_gate:'NO_RIGHTS'
 }];
 const html=render(data);
 assert.match(html,/&lt;svg/);
 assert.match(html,/&lt;img/);
 assert.match(html,/&lt;script/);
 assert.doesNotMatch(html,/<svg|<img|<script/);
});

test('R14 documents SAIP enhancement once and four disjoint non-censal routes',()=>{
 const data=sample();
 data.r14_documentary_status='R14_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED';
 data.r14_documentary_safe_by='2026-11-01T00:00:00+00:00';
 data.r14_saip_enrichment_not_additive={
   source_declared_columns:35,column_names_visible_in_index:15,
   column_names_not_verified:20,restore_point_metadata_entries_visible:2,
   original_snapshots_compared:0
 };
 data.r14_documentary_routes=[{source_id:'ARAGON_GENERAL_ACCESS_STATISTICS',
   documentary_unit:'ACCESS_REQUEST_REGISTER_LEGAL_RULE_AND_AGGREGATES',
   limitation:'STATUTORY_REGISTER_NOT_PUBLIC_COMPLETE_CASE_DISTRIBUTION',
   rights_scope:'OPEN_DATA_TERMS_BIND_ON_ACCESS_PDF_ASSET_RIGHTS_UNVERIFIED'}];
 const html=render(data);
 assert.match(html,/R14 · SAIP y registros autonómicos/);
 assert.match(html,/Aragón: registro descrito normativamente/);
 assert.match(html,/15 nombres visibles y 20 desconocidos/);
 assert.match(html,/NO son dos archivos históricos originales/);
 assert.match(html,/OPEN_DATA_TERMS_BIND_ON_ACCESS/);
});

test('R14 future assets hidden and labels escaped against XSS',()=>{
 const data=sample();
 data.r14_documentary_status='R14_NOT_KNOWN_AT_CUT';
 data.r14_documentary_routes=[{source_id:'FUTURE_CLM'}];
 assert.doesNotMatch(render(data),/FUTURE_CLM/);
 data.r14_documentary_status='R14_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED';
 data.r14_documentary_safe_by='<svg onload=alert(1)>';
 data.r14_documentary_routes=[{source_id:'<img src=x onerror=alert(1)>',
   documentary_unit:'<script>bad()</script>',limitation:'SCOPED',
   rights_scope:'NO_DATASET_LICENSE'}];
 const html=render(data);
 assert.match(html,/&lt;img/);
 assert.match(html,/&lt;script/);
 assert.match(html,/&lt;svg/);
 assert.doesNotMatch(html,/<img|<script|<svg/);
});
