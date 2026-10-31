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
