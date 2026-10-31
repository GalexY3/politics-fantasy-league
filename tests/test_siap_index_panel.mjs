import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const script=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const found=script.match(/function siapIndexPanel\(\)\{[\s\S]*?\n\}/);
assert.ok(found,'SIAP panel should exist');
const escape=s=>String(s??'').replace(/[&<>"']/g,
  c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function render(row){
 return runInNewContext(found[0]+'\nsiapIndexPanel',{
  ui:{siapCoverage:row},esc:escape,count:n=>String(n),
  stat:(label,value,desc)=>'<div>'+escape(label)+' '+escape(value)+' '+escape(desc)+'</div>',
 })();
}

test('real single source page displays gaps without pretending a census',()=>{
 const text=render({
  status:'ONE_INDEX_PAGE_OF_UNCERTIFIED_POPULATION',
  source_pages_captured:1,source_index_pages:44,
  observed_links:20,original_sha256:'3846b9fec8f20b426bfa1c231b717e0c20664d08aaf8586e49171339d927fc8d',
  safe_local_observation_by:'2026-10-31T06:02:49Z',
 });
 assert.match(text,/1 \/ 44/);
 assert.match(text,/Enlaces observados 20/);
 assert.match(text,/43 páginas sin verificar/);
 assert.match(text,/Denominador longitudinal DESCONOCIDO/);
 assert.match(text,/nunca primera publicación histórica/);
 assert.doesNotMatch(text,/20 iniciativas completas|20 aprobadas|personas puntuadas/);
});

test('unavailable or quarantined index hides all page counts and hash',()=>{
 for(const status of ['NOT_YET_IN_LOCAL_OBSERVATORY','INDEX_METADATA_QUARANTINED',undefined]){
  const html=render({status,observed_links:99999,original_sha256:'f'.repeat(64)});
  assert.match(html,/Sin metadatos de captura admisibles/);
  assert.doesNotMatch(html,/99999|ffffffffff/);
 }
});
