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
