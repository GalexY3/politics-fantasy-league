import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';

const js = readFileSync(new URL('../src/politics_fantasy/web/app.js', import.meta.url), 'utf8');
const match = js.match(/function spanishProcessesPanel\(\)\{[\s\S]*?\n\}/);
assert.ok(match, 'Canary cohort panel must exist');

function render(c) {
  const esc = s => String(s ?? '').replace(/[&<>"']/g,
    t => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[t]));
  return runInNewContext(match[0] + '\nspanishProcessesPanel', {
    ui: {parcanCohorts:c}, esc, count:n=>String(n),
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
  assert.match(html,/sin OUTCOMES/i);
  assert.match(html,/no son fechas de primera publicación/i);
  assert.match(html,/2025/);
  assert.doesNotMatch(html,/probabilidad de aprobar|calificación de políticos/i);
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
