import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const source=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const func=source.match(/function populationReadinessPanel\(\)\{[\s\S]*?\n\}/);
assert.ok(func,'The actual UI renderer must be tested');
const escapeText=s=>String(s??'').replace(/[&<>"']/g,
 c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function render(cut){
 const input={as_of:cut,reusable_scientific_cohort:false,risk_set_denominator:null,
  schema:'pfl.spanish_procedural_population_readiness.v1',
  institutional_sources:[],coverage_gates:[],
  denominator_evidence:{schema:'pfl.denominator_evidence_nonadditive.v1',
   reported_sources:[{source_id:'PARCAN_SOURCE_LOCAL',institution:'Canarias',
    observable_unit:'SOURCE_LOCAL',observed_source_local_items:null,
    principal_identification_block:'NO_EXTERNAL_CENSUS'}]}};
 return runInNewContext(func[0]+'\npopulationReadinessPanel',{
  ui:{populationReadiness:input},esc:escapeText,count:n=>String(n)
 })();
}

test('R18 ISO offset cut is preserved by the real source-scoped link',()=>{
 const html=render('2026-11-01T01:05:00+01:00');
 assert.ok(html.includes('source_id=PARCAN_SOURCE_LOCAL&amp;as_of=2026-11-01T01%3A05%3A00%2B01%3A00'));
});

test('R18 invalid historical cut never produces an unscoped CURRENT link',()=>{
 const html=render('INVALID_HISTORICAL_TIMESTAMP');
 assert.ok(!html.includes('href="/api/registration-readiness?source_id=PARCAN_SOURCE_LOCAL"'));
 assert.ok(html.includes('corte no válido'));
});

test('R18 explicit current mode remains distinct from historical mode',()=>{
 const html=render(null);
 assert.ok(html.includes('href="/api/registration-readiness?source_id=PARCAN_SOURCE_LOCAL"'));
});
