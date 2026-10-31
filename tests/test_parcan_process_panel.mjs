import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';

const js = readFileSync(new URL('../src/politics_fantasy/web/app.js', import.meta.url), 'utf8');
const match = js.match(/function spanishProcessesPanel\(\)\{[\s\S]*?\n\}/);
assert.ok(match, 'Canary cohort panel must exist');

function render(c,proceduralCoverage=null) {
  const esc = s => String(s ?? '').replace(/[&<>"']/g,
    t => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[t]));
  return runInNewContext(match[0] + '\nspanishProcessesPanel', {
    ui: {parcanCohorts:c,proceduralCoverage}, esc, count:n=>String(n),
    stat:(n,v,c)=>'<div>'+esc(n)+':'+esc(v)+'('+esc(c)+')</div>',
  })();
}

const sample = () => ({
  ok:true, status:'AUDITED_METADATA_CURRENT_CAPTURE',
  observed_rows:1211, local_snapshot_audited_at:'2026-10-31T05:19:18Z',
  source_cohorts:[
    {institution:'Parlamento de Canarias',initiative_type:'PPL',legislature:10,year:2023,rows_in_captured_distribution:1,capture_sha256:'a'.repeat(64)},
    {institution:'Parlamento de Canarias',initiative_type:'PE',legislature:11,year:2024,rows_in_captured_distribution:686,capture_sha256:'b'.repeat(64)},
    {institution:'Parlamento de Canarias',initiative_type:'PE',legislature:11,year:2026,rows_in_captured_distribution:524,capture_sha256:'c'.repeat(64)},
  ],
});

test('displays three real *metadata* strata without inventing full censes or temporal outcomes', () => {
  const html = render(sample());
  assert.match(html,/1211/);
  assert.match(html,/686/);
  assert.match(html,/524/);
  assert.match(html,/3 distribuciones observadas/);
  assert.match(html,/sin OUTCOMES/i);
  assert.match(html,/no son fechas de primera publicación/i);
  assert.match(html,/2024, 2026/);
  assert.doesNotMatch(html,/2025/);
  assert.doesNotMatch(html,/probabilidad de aprobar|calificación de políticos/i);
});

test('new PE/2025 capture appears only in later audit snapshot without census claim',()=>{
  const later=sample();
  later.observed_rows=1754;
  later.local_snapshot_audited_at='2026-10-31T05:34:51Z';
  later.source_cohorts.splice(2,0,{
    institution:'Parlamento de Canarias',initiative_type:'PE',legislature:11,
    year:2025,rows_in_captured_distribution:543,capture_sha256:'d'.repeat(64)
  });
  const html=render(later);
  assert.match(html,/1754/);
  assert.match(html,/543/);
  assert.match(html,/4 distribuciones observadas/);
  assert.match(html,/2024, 2025, 2026/);
  assert.match(html,/no demuestra cobertura exhaustiva/i);
  assert.doesNotMatch(html,/conclusión causal|aprobadas: 543/i);
});

test('month observations appear only with audited derivative, never zeros or outcomes',()=>{
  const later=sample();
  later.observed_rows=1754;
  later.creation_monthly_status='SOURCE_CREATION_MONTHS_AUDITED_ONLY';
  later.creation_monthly_observed_entries=[
    {scope:'PARCAN:LEG11:PE:YEAR2024',source_reported_created_month:'2024-02',observed_entries:100}
  ];
  const html=render(later);
  assert.match(html,/Meses con registros observados/);
  assert.match(html,/2024-02/);
  assert.match(html,/no acredita primera publicación histórica/);
  assert.match(html,/meses sin filas no se convierten en meses sin iniciativas/i);
  assert.doesNotMatch(html,/2024-08/);
  later.creation_monthly_status='MONTHLY_DERIVATIVE_QUARANTINED';
  const quarantined=render(later);
  assert.doesNotMatch(quarantined,/2024-02|Meses con registros observados/);
});

test('second editorial view is separately gated, never a risk-set denominator',()=>{
 const c=sample();
 const witness={
  status:'CONCORDANT_SOURCE_COUNTERS_NOT_CENSUS',
  editorial_count_total:1753,
  source_strata:[
   {year:2024,publisher_editorial_count:686,local_original_rows:686},
   {year:2025,publisher_editorial_count:543,local_original_rows:543},
   {year:2026,publisher_editorial_count:524,local_original_rows:524},
  ],
  missing_for_survival:['EXHAUSTIVE_ENTRY_CENSUS','DATED_PROCEDURAL_TRANSITIONS'],
 };
 const html=render(c,witness);
 assert.match(html,/Comprobación editorial de preguntas escritas: 1753 observadas/);
 assert.match(html,/misma base de datos/);
 assert.match(html,/Denominador de riesgo: desconocido/);
 assert.match(html,/EXHAUSTIVE_ENTRY_CENSUS/);
 assert.doesNotMatch(html,/1\.753 expedientes cerrados|probabilidad de éxito/);
 witness.status='CROSSVIEW_QUARANTINED';
 const quarantine=render(c,witness);
 assert.doesNotMatch(quarantine,/1753|EXHAUSTIVE_ENTRY_CENSUS/);
});

test('source quarantine refuses synthetic fallback', () => {
  assert.match(render({ok:false,source_cohorts:[],observed_rows:9999}),/no genera cifras sustitutivas/i);
  assert.doesNotMatch(render({ok:false,source_cohorts:[],observed_rows:9999}),/9999/);
});

test('rendered untrusted institution strings cannot become HTML',()=>{
  const x=sample();
  x.source_cohorts[0].institution='<img src=x onerror=alert(1)>';
  const html=render(x);
  assert.match(html,/&lt;img/);
  assert.doesNotMatch(html,/<img/);
});
